presenceListeners.remove(listener);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.xmpp;

import java.io.IOException;
import java.util.*;
import org.eclipse.core.runtime.IAdapterManager;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.*;
import org.eclipse.ecf.core.sharedobject.events.*;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.internal.provider.xmpp.events.*;
import org.eclipse.ecf.internal.provider.xmpp.smack.ECFConnection;
import org.eclipse.ecf.presence.*;
import org.eclipse.ecf.presence.im.*;
import org.eclipse.ecf.presence.roster.*;
import org.eclipse.ecf.provider.xmpp.XMPPContainer;
import org.eclipse.ecf.provider.xmpp.identity.XMPPID;
import org.eclipse.ecf.provider.xmpp.identity.XMPPRoomID;
import org.eclipse.equinox.concurrent.future.*;
import org.jivesoftware.smack.*;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.RosterEntry;
import org.jivesoftware.smack.RosterGroup;
import org.jivesoftware.smack.packet.*;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smack.packet.Presence.Mode;
import org.jivesoftware.smack.packet.Presence.Type;
import org.jivesoftware.smackx.packet.VCard;

public class XMPPContainerPresenceHelper implements ISharedObject {

	public static final String VCARD = "vcard";
	public static final String VCARD_EMAIL = VCARD + ".email";
	public static final String VCARD_EMAIL_HOME = VCARD_EMAIL + ".home";
	public static final String VCARD_EMAIL_WORK = VCARD_EMAIL + ".work";
	public static final String VCARD_NAME = VCARD + ".name";
	public static final String VCARD_NAME_FIRST = VCARD_NAME + ".first";
	public static final String VCARD_NAME_MIDDLE = VCARD_NAME + ".middle";
	public static final String VCARD_NAME_LAST = VCARD_NAME + ".last";
	public static final String VCARD_NAME_NICK = VCARD_NAME + ".nick";
	public static final String VCARD_PHONE = VCARD + ".phone";
	public static final String VCARD_PHONE_HOME = VCARD_PHONE + ".home";
	public static final String VCARD_PHONE_HOME_VOICE = VCARD_PHONE_HOME
			+ ".voice";
	public static final String VCARD_PHONE_HOME_CELL = VCARD_PHONE_HOME
			+ ".cell";
	public static final String VCARD_PHONE_WORK = VCARD_PHONE + ".work";
	public static final String VCARD_PHONE_WORK_VOICE = VCARD_PHONE_WORK
			+ ".voice";
	public static final String VCARD_PHONE_WORK_CELL = VCARD_PHONE_WORK
			+ ".cell";

	private ISharedObjectConfig config = null;

	private final List sharedObjectMessageListeners = new ArrayList();

	private XMPPContainer container = null;

	private XMPPChatManager chatManager = null;

	private final List presenceListeners = new ArrayList();

	public XMPPContainerPresenceHelper(XMPPContainer container) {
		this.container = container;
		chatManager = new XMPPChatManager(this);
		roster = new org.eclipse.ecf.presence.roster.Roster(container);
		rosterManager = new PresenceRosterManager(roster);
	}

	// ISharedObject implementation

	/*
	 * (non-Javadoc)
	 * 
	 * @seeorg.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.
	 * ISharedObjectConfig)
	 */
	public void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util
	 * .Event)
	 */
	public void handleEvent(Event event) {
		trace("handleEvent(" + event + ")");
		if (event instanceof ISharedObjectActivatedEvent) {
		} else if (event instanceof IQEvent) {
			handleIQEvent((IQEvent) event);
		} else if (event instanceof MessageEvent) {
			handleMessageEvent((MessageEvent) event);
		} else if (event instanceof PresenceEvent) {
			handlePresenceEvent((PresenceEvent) event);
		} else if (event instanceof ISharedObjectMessageEvent) {
			handleSharedObjectMessageEvent((ISharedObjectMessageEvent) event);
		} else {
			trace("unhandled event=" + event);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.
	 * util.Event[])
	 */
	public void handleEvents(Event[] events) {
		for (int i = 0; i < events.length; i++) {
			handleEvent(events[i]);
		}
	}

	public void disconnect() {
		rosterManager.disconnect();
		chatManager.disconnect();
		synchronized (sharedObjectMessageListeners) {
			sharedObjectMessageListeners.clear();
		}
		synchronized (presenceListeners) {
			presenceListeners.clear();
		}
		vcardCache.clear();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity
	 * .ID)
	 */
	public void dispose(ID containerID) {
		vcardCache.clear();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		if (adapter == null)
			return null;
		if (adapter.isInstance(this))
			return this;
		final IAdapterManager adapterManager = XmppPlugin.getDefault()
				.getAdapterManager();
		return (adapterManager == null) ? null : adapterManager.loadAdapter(
				this, adapter.getName());
	}

	// end ISharedObject implementation

	protected org.eclipse.ecf.presence.roster.Roster roster;

	protected PresenceRosterManager rosterManager;

	class PresenceRosterManager extends AbstractRosterManager {

		public PresenceRosterManager(
				org.eclipse.ecf.presence.roster.Roster roster) {
			super(roster);
		}

		public void notifySubscriptionListener(ID fromID, IPresence presence) {
			this.fireSubscriptionListener(fromID, presence.getType());
		}

		public void notifyRosterUpdate(IRosterItem changedItem) {
			fireRosterUpdate(changedItem);
		}

		public void notifyRosterAdd(IRosterEntry entry) {
			fireRosterAdd(entry);
		}

		public void notifyRosterRemove(IRosterEntry entry) {
			fireRosterRemove(entry);
		}

		public void disconnect() {
			getRoster().getItems().clear();
			super.disconnect();
			fireRosterUpdate(roster);
		}

		public void setUser(IUser user) {
			final org.eclipse.ecf.presence.roster.Roster roster = (org.eclipse.ecf.presence.roster.Roster) getRoster();
			roster.setUser(user);
			notifyRosterUpdate(roster);
		}

		org.eclipse.ecf.presence.IPresenceSender rosterPresenceSender = new org.eclipse.ecf.presence.IPresenceSender() {
			public void sendPresenceUpdate(ID toID,
					org.eclipse.ecf.presence.IPresence presence)
					throws ECFException {
				try {
					getConnectionOrThrowIfNull().sendPresenceUpdate(toID,
							createPresence(presence));
				} catch (final IOException e) {
					traceAndThrowECFException("sendPresenceUpdate", e);
				}
			}

		};

		/*
		 * (non-Javadoc)
		 * 
		 * @see
		 * org.eclipse.ecf.presence.roster.AbstractRosterManager#getPresenceSender
		 * ()
		 */
		public IPresenceSender getPresenceSender() {
			return rosterPresenceSender;
		}

		org.eclipse.ecf.presence.roster.IRosterSubscriptionSender rosterSubscriptionSender = new org.eclipse.ecf.presence.roster.IRosterSubscriptionSender() {
			/*
			 * (non-Javadoc)
			 * 
			 * @seeorg.eclipse.ecf.presence.roster.IRosterSubscriptionSender#
			 * sendRosterAdd(java.lang.String, java.lang.String,
			 * java.lang.String[])
			 */
			public void sendRosterAdd(String user, String name, String[] groups)
					throws ECFException {
				try {
					getConnectionOrThrowIfNull().sendRosterAdd(user, name,
							groups);
				} catch (final Exception e) {
					traceAndThrowECFException("sendRosterAdd", e);
				}
			}

			/*
			 * (non-Javadoc)
			 * 
			 * @seeorg.eclipse.ecf.presence.roster.IRosterSubscriptionSender#
			 * sendRosterRemove(org.eclipse.ecf.core.identity.ID)
			 */
			public void sendRosterRemove(ID userID) throws ECFException {
				try {
					if (!(userID instanceof XMPPID))
						throw new ECFException("invalid userID");
					final XMPPID xmppID = (XMPPID) userID;
					getConnectionOrThrowIfNull().sendRosterRemove(
							xmppID.getUsernameAtHost());
				} catch (final Exception e) {
					traceAndThrowECFException("sendRosterRemove", e);
				}
			}

		};

		/*
		 * (non-Javadoc)
		 * 
		 * @seeorg.eclipse.ecf.presence.roster.AbstractRosterManager#
		 * getRosterSubscriptionSender()
		 */
		public IRosterSubscriptionSender getRosterSubscriptionSender() {
			return rosterSubscriptionSender;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see
		 * org.eclipse.ecf.presence.roster.IRosterManager#addPresenceListener
		 * (org.eclipse.ecf.presence.roster.IPresenceListener)
		 */
		public void addPresenceListener(IPresenceListener listener) {
			synchronized (presenceListeners) {
				presenceListeners.add(listener);
			}
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see
		 * org.eclipse.ecf.presence.roster.IRosterManager#removePresenceListener
		 * (org.eclipse.ecf.presence.roster.IPresenceListener)
		 */
		public void removePresenceListener(IPresenceListener listener) {
			synchronized (presenceListeners) {
				presenceListeners.add(listener);
			}
		}

	}

	/**
	 * @return IRosterManager roster manager. Will not return <code>null</code>.
	 */
	public IRosterManager getRosterManager() {
		return rosterManager;
	}

	/**
	 * @param user
	 *            set the user for this presence helper.
	 */
	public void setUser(IUser user) {
		rosterManager.setUser(user);
	}

	protected void addSharedObjectMessageListener(
			ISharedObjectMessageListener listener) {
		synchronized (sharedObjectMessageListeners) {
			sharedObjectMessageListeners.add(listener);
		}
	}

	protected void sendTypingMessage(ID toID, boolean isTyping, String body)
			throws IOException {
		getContext().sendMessage(
				toID,
				new TypingMessage(rosterManager.getRoster().getUser().getID(),
						isTyping, body));
	}

	protected void handleSharedObjectMessageEvent(
			ISharedObjectMessageEvent event) {
		List toNotify = null;
		synchronized (sharedObjectMessageListeners) {
			toNotify = new ArrayList(sharedObjectMessageListeners);
		}
		for (final Iterator i = toNotify.iterator(); i.hasNext();) {
			final ISharedObjectMessageListener l = (ISharedObjectMessageListener) i
					.next();
			l.handleSharedObjectMessage(event);
		}

		final Object data = event.getData();
		if (data instanceof ITypingMessage) {
			final ITypingMessage tmess = (ITypingMessage) data;
			chatManager.fireTypingMessage(tmess.getFromID(), tmess);
		}

	}

	protected void removeSharedObjectMessageListener(
			ISharedObjectMessageListener listener) {
		synchronized (sharedObjectMessageListeners) {
			sharedObjectMessageListeners.remove(listener);
		}
	}

	private void addToRoster(IRosterItem[] items) {
		for (int i = 0; i < items.length; i++) {
			roster.addItem(items[i]);
		}
		rosterManager.notifyRosterUpdate(roster);
	}

	protected ISharedObjectContext getContext() {
		return config.getContext();
	}

	protected String getUserNameFromXMPPAddress(XMPPID userID) {
		return userID.getUsername();
	}

	protected IRosterEntry createRosterEntry(RosterEntry entry) {
		final XMPPID xmppid = createIDFromName(entry.getUser());
		final String name = (entry.getName() == null) ? xmppid.getUsername()
				: XMPPID.unfixEscapeInNode(entry.getName());
		return createRosterEntry(xmppid, name, entry.getGroups());
	}

	protected IRosterEntry createRosterEntry(XMPPID xmppid,
			RosterPacket.Item entry) {
		final String name = (entry.getName() == null) ? xmppid.getUsername()
				: XMPPID.unfixEscapeInNode(entry.getName());
		return createRosterEntry(xmppid, name, entry.getGroupNames());
	}

	protected void handleIQEvent(IQEvent evt) {
		final IQ iq = evt.getIQ();
		if (iq instanceof RosterPacket) {
			// Roster packet...report to UI
			final RosterPacket rosterPacket = (RosterPacket) iq;
			if (rosterPacket.getType() == IQ.Type.SET
					|| rosterPacket.getType() == IQ.Type.RESULT) {
				for (final Iterator i = rosterPacket.getRosterItems(); i
						.hasNext();) {
					final RosterPacket.Item item = (RosterPacket.Item) i.next();
					final RosterPacket.ItemType itemType = item.getItemType();
					boolean remove = false;
					XMPPID newID = createIDFromName(item.getUser());
					final IRosterItem items[] = createRosterEntries(newID, item);
					final IRosterEntry entry = createRosterEntry(newID, item);
					if (itemType == RosterPacket.ItemType.NONE
							|| itemType == RosterPacket.ItemType.REMOVE) {
						removeItemFromRoster(roster.getItems(),
								createIDFromName(item.getUser()));
						remove = true;
					} else {
						remove = false;
						addToRoster(items);
					}
					// In both cases fire set roster entry
					fireSetRosterEntry(remove, entry);
				}
			}
		} else {
			trace("Received non rosterpacket IQ message");
		}
	}

	protected void fireSetRosterEntry(boolean remove, IRosterEntry entry) {
		if (remove)
			rosterManager.notifyRosterRemove(entry);
		else
			rosterManager.notifyRosterAdd(entry);
	}

	private void removeItemFromRoster(Collection rosterItems,
			XMPPID itemIDToRemove) {
		boolean removed = false;
		synchronized (rosterItems) {
			for (final Iterator i = rosterItems.iterator(); i.hasNext();) {
				final IRosterItem item = (IRosterItem) i.next();
				if (item instanceof org.eclipse.ecf.presence.roster.RosterGroup) {
					final org.eclipse.ecf.presence.roster.RosterGroup group = (org.eclipse.ecf.presence.roster.RosterGroup) item;
					removed = removeItemFromRosterGroup(group, itemIDToRemove);
					// If group is empty, remove it too
					if (group.getEntries().size() == 0)
						i.remove();
				} else if (item instanceof org.eclipse.ecf.presence.roster.RosterEntry) {
					if (((org.eclipse.ecf.presence.roster.RosterEntry) item)
							.getUser().getID().equals(itemIDToRemove)) {
						i.remove();
						removed = true;
					}
				}
			}
		}
		if (removed)
			rosterManager.notifyRosterUpdate(roster);

	}

	private boolean removeItemFromRosterGroup(
			org.eclipse.ecf.presence.roster.RosterGroup group,
			XMPPID itemIDToRemove) {
		final Collection groupEntries = group.getEntries();
		synchronized (groupEntries) {
			for (final Iterator i = group.getEntries().iterator(); i.hasNext();) {
				final org.eclipse.ecf.presence.roster.RosterEntry entry = (org.eclipse.ecf.presence.roster.RosterEntry) i
						.next();
				if (entry.getUser().getID().equals(itemIDToRemove)) {
					i.remove();
					return true;
				}
			}
		}
		return false;
	}

	protected void handleMessageEvent(MessageEvent evt) {
		Message msg = evt.getMessage();
		final String from = msg.getFrom();
		final String body = msg.getBody();
		final String subject = msg.getSubject();
		final ID fromID = createIDFromName(from);
		final ID threadID = createThreadID(msg.getThread());
		msg = filterMessageType(msg);
		if (msg != null) {
			if (msg.getExtension("composing", //$NON-NLS-1$
					"http://jabber.org/protocol/chatstates") != null) { //$NON-NLS-1$
				chatManager.fireTypingMessage(fromID, new TypingMessage(fromID,
						true, body));
			} else if (msg.getExtension("paused", //$NON-NLS-1$
					"http://jabber.org/protocol/chatstates") != null) { //$NON-NLS-1$
				chatManager.fireTypingMessage(fromID, new TypingMessage(fromID,
						false, body));
			} else {
				final Iterator xhtmlbodies = evt.getXHTMLBodies();
				if (xhtmlbodies != null) {
					final List xhtmlbodylist = new ArrayList();
					for (; xhtmlbodies.hasNext();)
						xhtmlbodylist.add(xhtmlbodies.next());
					chatManager.fireXHTMLChatMessage(fromID, threadID, msg
							.getType(), subject, body, ECFConnection
							.getPropertiesFromPacket(msg), xhtmlbodylist);
				} else if (body != null) {
					chatManager.fireChatMessage(fromID, threadID,
							msg.getType(), subject, body, ECFConnection
									.getPropertiesFromPacket(msg));
				}
			}
		}
	}

	protected void handlePresenceEvent(PresenceEvent evt) {
		final Presence xmppPresence = evt.getPresence();
		final String from = xmppPresence.getFrom();
		final IPresence newPresence = createIPresence(xmppPresence);
		final XMPPID fromID = createIDFromName(from);
		if (newPresence.getType().equals(IPresence.Type.SUBSCRIBE)
				|| newPresence.getType().equals(IPresence.Type.UNSUBSCRIBE)
				|| newPresence.getType().equals(IPresence.Type.SUBSCRIBED)
				|| newPresence.getType().equals(IPresence.Type.UNSUBSCRIBED)) {
			rosterManager.notifySubscriptionListener(fromID, newPresence);
		} else {
			updatePresence(fromID, newPresence);
			firePresenceListeners(fromID, newPresence);
		}
	}

	private void firePresenceListeners(ID fromID, IPresence presence) {
		List toNotify = null;
		synchronized (presenceListeners) {
			toNotify = new ArrayList(presenceListeners);
		}
		for (final Iterator i = toNotify.iterator(); i.hasNext();) {
			final IPresenceListener l = (IPresenceListener) i.next();
			l.handlePresence(fromID, presence);
		}
	}

	private void updatePresence(XMPPID fromID, IPresence newPresence) {
		final Collection rosterItems = roster.getItems();
		List newEntrys = new ArrayList();
		synchronized (rosterItems) {
			for (final Iterator i = roster.getItems().iterator(); i.hasNext();) {
				final IRosterItem item = (IRosterItem) i.next();
				if (item instanceof IRosterGroup) {
					AdditionalClientRosterEntry[] es = updatePresenceInGroup(
							(IRosterGroup) item, fromID, newPresence);
					for (int j = 0; j < es.length; j++) {
						newEntrys.add(es[j]);
					}
				} else if (item instanceof org.eclipse.ecf.presence.roster.RosterEntry) {
					AdditionalClientRosterEntry entry = updatePresenceForMatchingEntry(
							(org.eclipse.ecf.presence.roster.RosterEntry) item,
							fromID, newPresence);
					if (entry != null)
						newEntrys.add(entry);
				}
			}
		}

		AdditionalClientRosterEntry[] entrys = (AdditionalClientRosterEntry[]) newEntrys
				.toArray(new AdditionalClientRosterEntry[] {});
		IRosterEntry entry = null;
		if (entrys.length > 0) {
			for (int i = 0; i < entrys.length; i++) {
				entry = new org.eclipse.ecf.presence.roster.RosterEntry(
						entrys[i].parent, entrys[i].user, entrys[i].presence);
				// roster.addItem(entry);
			}
			rosterManager.notifyRosterUpdate(roster);
			fireSetRosterEntry(false, entry);
		}
	}

	class AdditionalClientRosterEntry {

		IRosterItem parent;
		IUser user;
		IPresence presence;

		public AdditionalClientRosterEntry(IRosterItem parent, IUser user,
				IPresence presence) {
			this.parent = parent;
			this.user = user;
			this.presence = presence;
		}
	}

	private AdditionalClientRosterEntry updatePresenceForMatchingEntry(
			org.eclipse.ecf.presence.roster.RosterEntry entry, XMPPID fromID,
			IPresence newPresence) {
		final IUser user = entry.getUser();
		XMPPID oldID = (XMPPID) user.getID();
		// If the username/host part matches that means we either have to update
		// the resource, or create a new client
		if (oldID.equals(fromID)) {
			// set the new presence state
			entry.setPresence(newPresence);
			// and notify with roster update
			rosterManager.notifyRosterUpdate(entry);
		} else if (oldID.getUsernameAtHost().equals(fromID.getUsernameAtHost())) {
			if (oldID.getResourceName() == null) {
				oldID.setResourceName(fromID.getResourceName());
				// set the new presence state
				entry.setPresence(newPresence);
				// and notify with roster update
				rosterManager.notifyRosterUpdate(entry);
			} else if (fromID.getResourceName() != null
					&& !newPresence.getType()
							.equals(IPresence.Type.UNAVAILABLE)) {
				return new AdditionalClientRosterEntry(entry.getParent(),
						new User(fromID, user.getName()), newPresence);
			}
		}
		return null;
	}

	private AdditionalClientRosterEntry[] updatePresenceInGroup(
			IRosterGroup group, XMPPID fromID, IPresence newPresence) {
		List results = new ArrayList();
		final Collection groupEntries = group.getEntries();
		synchronized (groupEntries) {
			for (final Iterator i = group.getEntries().iterator(); i.hasNext();) {
				AdditionalClientRosterEntry newEntry = updatePresenceForMatchingEntry(
						(org.eclipse.ecf.presence.roster.RosterEntry) i.next(),
						fromID, newPresence);
				if (newEntry != null)
					results.add(newEntry);
			}
		}
		return (AdditionalClientRosterEntry[]) results
				.toArray(new AdditionalClientRosterEntry[] {});
	}

	protected void handleRoster(Roster roster) {
		for (final Iterator i = roster.getEntries(); i.hasNext();) {
			final IRosterItem[] items = createRosterEntries((RosterEntry) i
					.next());
			for (int j = 0; j < items.length; j++) {
				this.roster.addItem(items[j]);
			}
		}
		rosterManager.notifyRosterUpdate(this.roster);
	}

	protected XMPPID createIDFromName(String uname) {
		try {
			if (uname.lastIndexOf('@') == -1) {
				return new XMPPID(container.getConnectNamespace(), "admin"
						+ "@" + uname);
			}
			return new XMPPID(container.getConnectNamespace(), uname);
		} catch (final Exception e) {
			traceStack("Exception in createIDFromName", e);
			return null;
		}
	}

	protected ID createThreadID(String thread) {
		try {
			if (thread == null || thread.equals(""))
				return null;
			return IDFactory.getDefault().createStringID(thread);
		} catch (final Exception e) {
			traceStack("Exception in createThreadID", e);
			return null;
		}

	}

	private final Map vcardCache = new WeakHashMap();

	private VCard getFromCache(String id) {
		if (id == null)
			return null;
		return (VCard) vcardCache.get(id);
	}

	private void addToCache(String id, VCard card) {
		vcardCache.put(id, card);
	}

	private VCard getVCardForPresence(Presence xmppPresence) {
		VCard result = null;
		if (xmppPresence.getExtension("x", "vcard-temp:x:update") != null) {
			final String from = xmppPresence.getFrom();
			result = getFromCache(from);
			if (result == null && from != null) {
				result = new VCard();
				try {
					result.load(container.getXMPPConnection(), from);
					addToCache(from, result);
				} catch (final XMPPException e) {
					traceStack("vcard loading exception", e);
				}
			}
		}
		return result;
	}

	private Map addVCardProperties(VCard vcard, Map props) {
		if (vcard == null)
			return props;
		final String emailHome = vcard.getEmailHome();
		if (emailHome != null && !emailHome.equals(""))
			props.put(VCARD_EMAIL_HOME, emailHome);
		final String emailWork = vcard.getEmailWork();
		if (emailWork != null && !emailWork.equals(""))
			props.put(VCARD_EMAIL_WORK, emailWork);
		final String firstName = vcard.getFirstName();
		if (firstName != null && !firstName.equals(""))
			props.put(VCARD_NAME_FIRST, firstName);
		final String middleName = vcard.getMiddleName();
		if (middleName != null && !middleName.equals(""))
			props.put(VCARD_NAME_MIDDLE, middleName);
		final String lastName = vcard.getLastName();
		if (lastName != null && !lastName.equals(""))
			props.put(VCARD_NAME_LAST, lastName);
		final String nickName = vcard.getNickName();
		if (nickName != null && !nickName.equals(""))
			props.put(VCARD_NAME_NICK, nickName);
		final String phoneHomeVoice = vcard.getPhoneHome("VOICE");
		if (phoneHomeVoice != null && !phoneHomeVoice.equals(""))
			props.put(VCARD_PHONE_HOME_VOICE, phoneHomeVoice);
		final String phoneHomeCell = vcard.getPhoneHome("CELL");
		if (phoneHomeCell != null && !phoneHomeCell.equals(""))
			props.put(VCARD_PHONE_HOME_CELL, phoneHomeCell);
		final String phoneWorkVoice = vcard.getPhoneWork("VOICE");
		if (phoneWorkVoice != null && !phoneWorkVoice.equals(""))
			props.put(VCARD_PHONE_WORK_VOICE, phoneWorkVoice);
		final String phoneWorkCell = vcard.getPhoneWork("CELL");
		if (phoneWorkCell != null && !phoneWorkCell.equals(""))
			props.put(VCARD_PHONE_WORK_CELL, phoneWorkCell);
		return props;
	}

	class XMPPPresence extends org.eclipse.ecf.presence.Presence {

		private static final long serialVersionUID = 7843634971520771692L;

		IFuture asyncResult = null;
		String fromID = null;

		XMPPPresence(String fromID, Presence xmppPresence, IFuture future) {
			super(createIPresenceType(xmppPresence), xmppPresence.getStatus(),
					createIPresenceMode(xmppPresence), ECFConnection
							.getPropertiesFromPacket(xmppPresence), null);
			this.fromID = fromID;
		}

		private void fillFromVCard() {
			VCard card = getFromCache(fromID);
			if (card == null && asyncResult != null) {
				try {
					card = (VCard) asyncResult.get();
					asyncResult = null;
				} catch (final Exception e) {
				}
			}
			if (card != null) {
				addToCache(fromID, card);
				final byte[] bytes = card.getAvatar();
				this.pictureData = (bytes == null) ? new byte[0] : bytes;
				this.properties = addVCardProperties(card, this.properties);
			}
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.Presence#getPictureData()
		 */
		public byte[] getPictureData() {
			fillFromVCard();
			return this.pictureData;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.Presence#getProperties()
		 */
		public Map getProperties() {
			fillFromVCard();
			return this.properties;
		}
	}

	protected IPresence createIPresence(final Presence xmppPresence) {
		final IFuture asyncResult = new ThreadsExecutor().execute(
				new IProgressRunnable() {
					public Object run(IProgressMonitor monitor)
							throws Exception {
						return getVCardForPresence(xmppPresence);
					}
				}, null);
		return new XMPPPresence(xmppPresence.getFrom(), xmppPresence,
				asyncResult);
	}

	protected Presence createPresence(IPresence ipresence) {
		final Presence newPresence = new Presence(
				createPresenceType(ipresence), ipresence.getStatus(), 0,
				createPresenceMode(ipresence));
		ECFConnection.setPropertiesInPacket(newPresence, ipresence
				.getProperties());
		return newPresence;
	}

	protected IPresence.Mode createIPresenceMode(Presence xmppPresence) {
		if (xmppPresence == null)
			return IPresence.Mode.AVAILABLE;
		final Mode mode = xmppPresence.getMode();
		if (mode == Presence.Mode.AVAILABLE) {
			return IPresence.Mode.AVAILABLE;
		} else if (mode == Presence.Mode.AWAY) {
			return IPresence.Mode.AWAY;
		} else if (mode == Presence.Mode.CHAT) {
			return IPresence.Mode.CHAT;
		} else if (mode == Presence.Mode.DO_NOT_DISTURB) {
			return IPresence.Mode.DND;
		} else if (mode == Presence.Mode.EXTENDED_AWAY) {
			return IPresence.Mode.EXTENDED_AWAY;
		} else if (mode == Presence.Mode.INVISIBLE) {
			return IPresence.Mode.INVISIBLE;
		}
		return IPresence.Mode.AVAILABLE;
	}

	protected Presence.Mode createPresenceMode(IPresence ipresence) {
		if (ipresence == null)
			return Presence.Mode.AVAILABLE;
		final IPresence.Mode mode = ipresence.getMode();
		if (mode == IPresence.Mode.AVAILABLE) {
			return Presence.Mode.AVAILABLE;
		} else if (mode == IPresence.Mode.AWAY) {
			return Presence.Mode.AWAY;
		} else if (mode == IPresence.Mode.CHAT) {
			return Presence.Mode.CHAT;
		} else if (mode == IPresence.Mode.DND) {
			return Presence.Mode.DO_NOT_DISTURB;
		} else if (mode == IPresence.Mode.EXTENDED_AWAY) {
			return Presence.Mode.EXTENDED_AWAY;
		} else if (mode == IPresence.Mode.INVISIBLE) {
			return Presence.Mode.INVISIBLE;
		}
		return Presence.Mode.AVAILABLE;
	}

	protected IPresence.Type createIPresenceType(Presence xmppPresence) {
		if (xmppPresence == null)
			return IPresence.Type.AVAILABLE;
		final Type type = xmppPresence.getType();
		if (type == Presence.Type.AVAILABLE) {
			return IPresence.Type.AVAILABLE;
		} else if (type == Presence.Type.ERROR) {
			return IPresence.Type.ERROR;
		} else if (type == Presence.Type.SUBSCRIBE) {
			return IPresence.Type.SUBSCRIBE;
		} else if (type == Presence.Type.SUBSCRIBED) {
			return IPresence.Type.SUBSCRIBED;
		} else if (type == Presence.Type.UNSUBSCRIBE) {
			return IPresence.Type.UNSUBSCRIBE;
		} else if (type == Presence.Type.UNSUBSCRIBED) {
			return IPresence.Type.UNSUBSCRIBED;
		} else if (type == Presence.Type.UNAVAILABLE) {
			return IPresence.Type.UNAVAILABLE;
		}
		return IPresence.Type.AVAILABLE;
	}

	protected Presence.Type createPresenceType(IPresence ipresence) {
		if (ipresence == null)
			return Presence.Type.AVAILABLE;
		final IPresence.Type type = ipresence.getType();
		if (type == IPresence.Type.AVAILABLE) {
			return Presence.Type.AVAILABLE;
		} else if (type == IPresence.Type.ERROR) {
			return Presence.Type.ERROR;
		} else if (type == IPresence.Type.SUBSCRIBE) {
			return Presence.Type.SUBSCRIBE;
		} else if (type == IPresence.Type.SUBSCRIBED) {
			return Presence.Type.SUBSCRIBED;
		} else if (type == IPresence.Type.UNSUBSCRIBE) {
			return Presence.Type.UNSUBSCRIBE;
		} else if (type == IPresence.Type.UNSUBSCRIBED) {
			return Presence.Type.UNSUBSCRIBED;
		} else if (type == IPresence.Type.UNAVAILABLE) {
			return Presence.Type.UNAVAILABLE;
		}
		return Presence.Type.AVAILABLE;
	}

	protected IRosterItem[] createRosterEntries(RosterEntry entry) {
		final XMPPID xmppid = createIDFromName(entry.getUser());
		final String name = entry.getName();
		final User newUser = (name == null) ? new User(xmppid, xmppid
				.getUsername()) : new User(xmppid, XMPPID
				.unfixEscapeInNode(name));
		return createRosterEntries(entry.getGroups(), roster, newUser);
	}

	private IRosterItem[] createRosterEntries(Iterator grps,
			IRosterItem parent, IUser user) {
		final List result = new ArrayList();
		if (grps.hasNext()) {
			for (; grps.hasNext();) {
				final Object o = grps.next();
				// Get group name
				final String groupName = (o instanceof String) ? (String) o
						: ((RosterGroup) o).getName();

				if (groupName == null || groupName.equals("")) {
					createRosterEntries(parent, user, result);
					continue;
				}
				// See if group is already in roster
				org.eclipse.ecf.presence.roster.RosterGroup rosterGroup = findRosterGroup(
						parent, groupName);
				// Set flag if not
				final boolean groupFound = rosterGroup != null;
				if (!groupFound)
					rosterGroup = new org.eclipse.ecf.presence.roster.RosterGroup(
							parent, groupName);

				if (findRosterEntry(rosterGroup, user) == null) {
					// Now create new roster entry
					new org.eclipse.ecf.presence.roster.RosterEntry(
							rosterGroup, user,
							new org.eclipse.ecf.presence.Presence(
									IPresence.Type.UNAVAILABLE,
									IPresence.Type.UNAVAILABLE.toString(),
									IPresence.Mode.AWAY));
				}
				// Only add localGrp if not already in list
				if (!groupFound)
					result.add(rosterGroup);
			}
		} else
			createRosterEntries(parent, user, result);
		return (IRosterItem[]) result.toArray(new IRosterItem[] {});
	}

	protected IRosterEntry createRosterEntry(ID userID, String name,
			Iterator grps) {
		final List groups = new ArrayList();
		for (; grps.hasNext();) {
			final Object o = grps.next();
			final String groupName = (o instanceof String) ? (String) o
					: ((RosterGroup) o).getName();
			final IRosterGroup localGrp = new org.eclipse.ecf.presence.roster.RosterGroup(
					roster, groupName);
			groups.add(localGrp);
		}
		final IUser user = new User(userID, name);
		IRosterEntry newEntry = null;
		if (groups.size() == 0)
			return new org.eclipse.ecf.presence.roster.RosterEntry(roster,
					user, null);
		else
			for (int i = 0; i < groups.size(); i++) {
				final IRosterGroup grp = (IRosterGroup) groups.get(i);
				if (i == 0)
					newEntry = new org.eclipse.ecf.presence.roster.RosterEntry(
							grp, user, null);
				else {
					grp.getEntries().add(newEntry);
					newEntry.getGroups().add(grp);
				}
			}
		return newEntry;
	}

	private void createRosterEntries(IRosterItem parent, IUser user, List result) {
		final org.eclipse.ecf.presence.roster.RosterEntry oldEntry = findRosterEntry(
				(org.eclipse.ecf.presence.roster.RosterGroup) null, user);
		if (oldEntry == null) {
			final org.eclipse.ecf.presence.roster.RosterEntry newEntry = new org.eclipse.ecf.presence.roster.RosterEntry(
					parent, user, new org.eclipse.ecf.presence.Presence(
							IPresence.Type.UNAVAILABLE,
							IPresence.Type.UNAVAILABLE.toString(),
							IPresence.Mode.AWAY));
			result.add(newEntry);
		}
	}

	private org.eclipse.ecf.presence.roster.RosterEntry findRosterEntry(
			org.eclipse.ecf.presence.roster.RosterGroup rosterGroup, IUser user) {
		if (rosterGroup != null)
			return findRosterEntry(rosterGroup.getEntries(), user);
		else
			return findRosterEntry(roster.getItems(), user);
	}

	private org.eclipse.ecf.presence.roster.RosterEntry findRosterEntry(
			Collection entries, IUser user) {
		for (final Iterator i = entries.iterator(); i.hasNext();) {
			final Object o = i.next();
			if (o instanceof org.eclipse.ecf.presence.roster.RosterEntry) {
				final org.eclipse.ecf.presence.roster.RosterEntry entry = (org.eclipse.ecf.presence.roster.RosterEntry) o;
				if (entry.getUser().getID().equals(user.getID()))
					return entry;
			}
		}
		return null;
	}

	protected IRosterItem[] createRosterEntries(XMPPID id,
			RosterPacket.Item entry) {
		String name = entry.getName();
		if (name == null)
			name = id.getUsername();
		name = XMPPID.unfixEscapeInNode(name);
		return createRosterEntries(entry.getGroupNames(), roster, new User(id,
				name));
	}

	protected org.eclipse.ecf.presence.roster.RosterGroup findRosterGroup(
			Object parent, String grp) {
		final Collection items = roster.getItems();
		for (final Iterator i = items.iterator(); i.hasNext();) {
			final IRosterItem item = (IRosterItem) i.next();
			if (item.getName().equals(grp))
				return (org.eclipse.ecf.presence.roster.RosterGroup) item;
		}
		return null;
	}

	// utility methods

	protected ECFConnection getConnectionOrThrowIfNull() throws IOException {
		final ECFConnection conn = container.getECFConnection();
		if (conn == null)
			throw new IOException("Not connected");
		return conn;
	}

	protected void traceAndThrowECFException(String msg, Throwable t)
			throws ECFException {
		throw new ECFException(msg, t);
	}

	protected void trace(String msg) {

	}

	protected void traceStack(String msg, Throwable e) {

	}

	protected ID createRoomIDFromName(String from) {
		try {
			final ECFConnection ecfConnection = getConnectionOrThrowIfNull();
			return new XMPPRoomID(container.getConnectNamespace(),
					ecfConnection.getXMPPConnection(), from);
		} catch (final Exception e) {
			traceStack("Exception in createRoomIDFromName", e);
			return null;
		}
	}

	protected ID createUserIDFromName(String name) {
		ID result = null;
		try {
			result = new XMPPID(container.getConnectNamespace(), name);
			return result;
		} catch (final Exception e) {
			traceStack("Exception in createIDFromName", e);
			return null;
		}
	}

	protected Message.Type[] ALLOWED_MESSAGES = { Message.Type.CHAT,
			Message.Type.ERROR, Message.Type.HEADLINE, Message.Type.NORMAL };

	protected Message filterMessageType(Message msg) {
		for (int i = 0; i < ALLOWED_MESSAGES.length; i++) {
			if (ALLOWED_MESSAGES[i].equals(msg.getType())) {
				return msg;
			}
		}
		return null;
	}

	/**
	 * @return chat manager.
	 */
	public IChatManager getChatManager() {
		return chatManager;
	}

}