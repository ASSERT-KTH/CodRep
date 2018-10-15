this.fireSubscriptionListener(fromID, presence.getType());

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
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectConfig;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContext;
import org.eclipse.ecf.core.sharedobject.SharedObjectInitException;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectMessageListener;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.internal.provider.xmpp.events.IQEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.MessageEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.PresenceEvent;
import org.eclipse.ecf.internal.provider.xmpp.identity.XMPPID;
import org.eclipse.ecf.internal.provider.xmpp.identity.XMPPRoomID;
import org.eclipse.ecf.internal.provider.xmpp.smack.ECFConnection;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceListener;
import org.eclipse.ecf.presence.IPresenceSender;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.im.ITypingMessage;
import org.eclipse.ecf.presence.im.TypingMessage;
import org.eclipse.ecf.presence.roster.AbstractRosterManager;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterGroup;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.presence.roster.IRosterManager;
import org.eclipse.ecf.presence.roster.IRosterSubscriptionSender;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.RosterEntry;
import org.jivesoftware.smack.RosterGroup;
import org.jivesoftware.smack.packet.IQ;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smack.packet.RosterPacket;
import org.jivesoftware.smack.packet.Presence.Mode;
import org.jivesoftware.smack.packet.Presence.Type;

public class XMPPContainerPresenceHelper implements ISharedObject {

	ISharedObjectConfig config = null;

	Vector messageListeners = new Vector();

	Vector sharedObjectMessageListeners = new Vector();

	XMPPContainer container = null;

	XMPPChatManager chatManager = null;

	Vector presenceListeners = new Vector();

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
	 * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
	 */
	public void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
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
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
	 */
	public void handleEvents(Event[] events) {
		for (int i = 0; i < events.length; i++) {
			handleEvent(events[i]);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
	 */
	public void dispose(ID containerID) {
		if (messageListeners != null)
			messageListeners.clear();
		messageListeners = null;
		if (sharedObjectMessageListeners != null)
			sharedObjectMessageListeners.clear();
		sharedObjectMessageListeners = null;
		container = null;
		config = null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		return null;
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
			this.fireSubscriptionListener(fromID, presence);
		}

		public void notifyRosterUpdate(IRosterItem changedItem) {
			fireRosterUpdate(changedItem);
		}

		public void setUser(IUser user) {
			org.eclipse.ecf.presence.roster.Roster roster = (org.eclipse.ecf.presence.roster.Roster) getRoster();
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
				} catch (IOException e) {
					traceAndThrowECFException("sendPresenceUpdate", e);
				}
			}

		};

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.roster.AbstractRosterManager#getPresenceSender()
		 */
		public IPresenceSender getPresenceSender() {
			return rosterPresenceSender;
		}

		org.eclipse.ecf.presence.roster.IRosterSubscriptionSender rosterSubscriptionSender = new org.eclipse.ecf.presence.roster.IRosterSubscriptionSender() {
			/*
			 * (non-Javadoc)
			 * 
			 * @see org.eclipse.ecf.presence.roster.IRosterSubscriptionSender#sendRosterAdd(java.lang.String,
			 *      java.lang.String, java.lang.String[])
			 */
			public void sendRosterAdd(String user, String name, String[] groups)
					throws ECFException {
				try {
					getConnectionOrThrowIfNull().sendRosterAdd(user, name,
							groups);
				} catch (IOException e) {
					traceAndThrowECFException("sendRosterAdd", e);
				}
			}

			/*
			 * (non-Javadoc)
			 * 
			 * @see org.eclipse.ecf.presence.roster.IRosterSubscriptionSender#sendRosterRemove(org.eclipse.ecf.core.identity.ID)
			 */
			public void sendRosterRemove(ID userID) throws ECFException {
				try {
					if (!(userID instanceof XMPPID))
						throw new ECFException("invalid userID");
					XMPPID xmppID = (XMPPID) userID;
					getConnectionOrThrowIfNull().sendRosterRemove(
							xmppID.getUsernameAtHost());
				} catch (IOException e) {
					traceAndThrowECFException("sendRosterRemove", e);
				}
			}

		};

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.roster.AbstractRosterManager#getRosterSubscriptionSender()
		 */
		public IRosterSubscriptionSender getRosterSubscriptionSender() {
			return rosterSubscriptionSender;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.roster.IRosterManager#addPresenceListener(org.eclipse.ecf.presence.roster.IPresenceListener)
		 */
		public void addPresenceListener(IPresenceListener listener) {
			presenceListeners.add(listener);
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.roster.IRosterManager#removePresenceListener(org.eclipse.ecf.presence.roster.IPresenceListener)
		 */
		public void removePresenceListener(IPresenceListener listener) {
			presenceListeners.add(listener);
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
		sharedObjectMessageListeners.add(listener);
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
		for (Iterator i = sharedObjectMessageListeners.iterator(); i.hasNext();) {
			ISharedObjectMessageListener l = (ISharedObjectMessageListener) i
					.next();
			l.handleSharedObjectMessage(event);
		}

		Object data = event.getData();
		if (data instanceof ITypingMessage) {
			ITypingMessage tmess = (ITypingMessage) data;
			chatManager.fireTypingMessage(tmess.getFromID(), tmess);
		}

	}

	protected void removeSharedObjectMessageListener(
			ISharedObjectMessageListener listener) {
		sharedObjectMessageListeners.remove(listener);
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
		return createRosterEntry(createIDFromName(entry.getUser()), entry
				.getName(), entry.getGroups());
	}

	protected IRosterEntry createRosterEntry(RosterPacket.Item entry) {
		return createRosterEntry(createIDFromName(entry.getUser()), entry
				.getName(), entry.getGroupNames());
	}

	protected void handleIQEvent(IQEvent evt) {
		IQ iq = evt.getIQ();
		if (iq instanceof RosterPacket) {
			// Roster packet...report to UI
			RosterPacket rosterPacket = (RosterPacket) iq;
			if (rosterPacket.getType() == IQ.Type.SET
					|| rosterPacket.getType() == IQ.Type.RESULT) {
				for (Iterator i = rosterPacket.getRosterItems(); i.hasNext();) {
					RosterPacket.Item item = (RosterPacket.Item) i.next();
					RosterPacket.ItemType itemType = item.getItemType();
					boolean remove = false;
					IRosterItem items[] = createRosterEntries(item);
					IRosterEntry entry = createRosterEntry(item);
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
		for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
			IPresenceListener l = (IPresenceListener) i.next();
			if (remove)
				l.handleRosterEntryRemove(entry);
			else
				l.handleRosterEntryUpdate(entry);
		}
	}

	private void removeItemFromRoster(Collection rosterItems,
			XMPPID itemIDToRemove) {
		synchronized (rosterItems) {
			for (Iterator i = rosterItems.iterator(); i.hasNext();) {
				IRosterItem item = (IRosterItem) i.next();
				if (item instanceof org.eclipse.ecf.presence.roster.RosterGroup) {
					org.eclipse.ecf.presence.roster.RosterGroup group = (org.eclipse.ecf.presence.roster.RosterGroup) item;
					removeItemFromRosterGroup(group, itemIDToRemove);
					if (group.getEntries().size() == 0)
						roster.removeItem(item);
					rosterManager.notifyRosterUpdate(roster);
				} else if (item instanceof org.eclipse.ecf.presence.roster.RosterEntry) {
					if (((org.eclipse.ecf.presence.roster.RosterEntry) item)
							.getUser().getID().equals(itemIDToRemove)) {
						roster.removeItem(item);
						rosterManager.notifyRosterUpdate(roster);
					}
				}
			}
		}
	}

	private void removeItemFromRosterGroup(
			org.eclipse.ecf.presence.roster.RosterGroup group,
			XMPPID itemIDToRemove) {
		for (Iterator i = group.getEntries().iterator(); i.hasNext();) {
			org.eclipse.ecf.presence.roster.RosterEntry entry = (org.eclipse.ecf.presence.roster.RosterEntry) i
					.next();
			if (entry.getUser().getID().equals(itemIDToRemove)) {
				group.remove(entry);
				rosterManager.notifyRosterUpdate(group);
			}
		}
	}

	protected void handleMessageEvent(MessageEvent evt) {
		Message msg = evt.getMessage();
		String from = msg.getFrom();
		String body = msg.getBody();
		String subject = msg.getSubject();
		ID fromID = createIDFromName(from);
		ID threadID = createThreadID(msg.getThread());
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
				Iterator xhtmlbodies = evt.getXHTMLBodies();
				if (xhtmlbodies != null) {
					List xhtmlbodylist = new ArrayList();
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
		Presence xmppPresence = evt.getPresence();
		String from = xmppPresence.getFrom();
		IPresence newPresence = createIPresence(xmppPresence, evt
				.getPhotoData());
		XMPPID fromID = createIDFromName(from);
		if (newPresence.getType().equals(IPresence.Type.SUBSCRIBE)
				|| newPresence.getType().equals(IPresence.Type.UNSUBSCRIBE)
				|| newPresence.getType().equals(IPresence.Type.SUBSCRIBED)
				|| newPresence.getType().equals(IPresence.Type.UNSUBSCRIBED)) {
			rosterManager.notifySubscriptionListener(fromID, newPresence);
		} else {
			firePresenceListeners(fromID, newPresence);
			updatePresence(fromID, newPresence);
		}
	}

	private void firePresenceListeners(ID fromID, IPresence presence) {
		for (Iterator i = presenceListeners.iterator(); i.hasNext();) {
			IPresenceListener l = (IPresenceListener) i.next();
			l.handlePresence(fromID, presence);
		}
	}

	private void updatePresence(XMPPID fromID, IPresence newPresence) {
		for (Iterator i = roster.getItems().iterator(); i.hasNext();) {
			IRosterItem item = (IRosterItem) i.next();
			if (item instanceof IRosterGroup) {
				updatePresenceInGroup((IRosterGroup) item, fromID, newPresence);
			} else if (item instanceof org.eclipse.ecf.presence.roster.RosterEntry) {
				updatePresenceForMatchingEntry(
						(org.eclipse.ecf.presence.roster.RosterEntry) item,
						fromID, newPresence);
			}
		}
	}

	private void updatePresenceForMatchingEntry(
			org.eclipse.ecf.presence.roster.RosterEntry entry, XMPPID fromID,
			IPresence newPresence) {
		IUser user = entry.getUser();
		if (fromID.equals(user.getID())) {
			entry.setPresence(newPresence);
			rosterManager.notifyRosterUpdate(entry);
		}
	}

	private void updatePresenceInGroup(IRosterGroup group, XMPPID fromID,
			IPresence newPresence) {
		for (Iterator i = group.getEntries().iterator(); i.hasNext();) {
			updatePresenceForMatchingEntry(
					(org.eclipse.ecf.presence.roster.RosterEntry) i.next(),
					fromID, newPresence);
		}
	}

	protected void handleRoster(Roster roster) {
		for (Iterator i = roster.getEntries(); i.hasNext();) {
			IRosterItem[] items = createRosterEntries((RosterEntry) i.next());
			synchronized (roster) {
				for (int j = 0; j < items.length; j++) {
					this.roster.addItem(items[j]);
				}
			}
		}
		rosterManager.notifyRosterUpdate(this.roster);
	}

	protected XMPPID createIDFromName(String uname) {
		try {
			return new XMPPID(container.getConnectNamespace(), uname);
		} catch (Exception e) {
			traceStack("Exception in createIDFromName", e);
			return null;
		}
	}

	protected ID createThreadID(String thread) {
		try {
			if (thread == null || thread.equals(""))
				return null;
			return IDFactory.getDefault().createStringID(thread);
		} catch (Exception e) {
			traceStack("Exception in createThreadID", e);
			return null;
		}

	}

	protected IPresence createIPresence(Presence xmppPresence, byte[] photoData) {
		return new org.eclipse.ecf.presence.Presence(
				createIPresenceType(xmppPresence), xmppPresence.getStatus(),
				createIPresenceMode(xmppPresence), ECFConnection
						.getPropertiesFromPacket(xmppPresence), photoData);
	}

	protected Presence createPresence(IPresence ipresence) {
		Presence newPresence = new Presence(createPresenceType(ipresence),
				ipresence.getStatus(), 0, createPresenceMode(ipresence));
		ECFConnection.setPropertiesInPacket(newPresence, ipresence
				.getProperties());
		return newPresence;
	}

	protected IPresence.Mode createIPresenceMode(Presence xmppPresence) {
		if (xmppPresence == null)
			return IPresence.Mode.AVAILABLE;
		Mode mode = xmppPresence.getMode();
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
		IPresence.Mode mode = ipresence.getMode();
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
		Type type = xmppPresence.getType();
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
		IPresence.Type type = ipresence.getType();
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
		return createRosterEntries(entry.getGroups(), roster, new User(
				createIDFromName(entry.getUser()), entry.getName()));
	}

	private IRosterItem[] createRosterEntries(Iterator grps,
			IRosterItem parent, IUser user) {
		List result = new ArrayList();
		if (grps.hasNext()) {
			for (; grps.hasNext();) {
				Object o = grps.next();
				// Get group name
				String groupName = (o instanceof String) ? (String) o
						: ((RosterGroup) o).getName();

				if (groupName == null || groupName.equals("")) {
					createRosterEntries(parent, user, result);
					continue;
				}
				// See if group is already in roster
				org.eclipse.ecf.presence.roster.RosterGroup rosterGroup = findRosterGroup(
						parent, groupName);
				// Set flag if not
				boolean groupFound = rosterGroup != null;
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
		List groups = new ArrayList();
		for (; grps.hasNext();) {
			Object o = grps.next();
			String groupName = (o instanceof String) ? (String) o
					: ((RosterGroup) o).getName();
			IRosterGroup localGrp = new org.eclipse.ecf.presence.roster.RosterGroup(
					roster, groupName);
			groups.add(localGrp);
		}
		IUser user = new User(userID, name);
		IRosterEntry newEntry = null;
		if (groups.size() == 0)
			return new org.eclipse.ecf.presence.roster.RosterEntry(roster,
					user, null);
		else
			for (int i = 0; i < groups.size(); i++) {
				IRosterGroup grp = (IRosterGroup) groups.get(i);
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
		org.eclipse.ecf.presence.roster.RosterEntry oldEntry = findRosterEntry(
				(org.eclipse.ecf.presence.roster.RosterGroup) null, user);
		if (oldEntry == null) {
			org.eclipse.ecf.presence.roster.RosterEntry newEntry = new org.eclipse.ecf.presence.roster.RosterEntry(
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
		for (Iterator i = entries.iterator(); i.hasNext();) {
			Object o = i.next();
			if (o instanceof org.eclipse.ecf.presence.roster.RosterEntry) {
				org.eclipse.ecf.presence.roster.RosterEntry entry = (org.eclipse.ecf.presence.roster.RosterEntry) o;
				if (entry.getUser().getID().equals(user.getID()))
					return entry;
			}
		}
		return null;
	}

	protected IRosterItem[] createRosterEntries(RosterPacket.Item entry) {
		XMPPID id = createIDFromName(entry.getUser());
		String name = entry.getName();
		if (name == null)
			name = id.getUsername();
		return createRosterEntries(entry.getGroupNames(), roster, new User(id,
				name));
	}

	protected org.eclipse.ecf.presence.roster.RosterGroup findRosterGroup(
			Object parent, String grp) {
		Collection items = roster.getItems();
		for (Iterator i = items.iterator(); i.hasNext();) {
			IRosterItem item = (IRosterItem) i.next();
			if (item.getName().equals(grp))
				return (org.eclipse.ecf.presence.roster.RosterGroup) item;
		}
		return null;
	}

	// utility methods

	protected ECFConnection getConnectionOrThrowIfNull() throws IOException {
		ECFConnection conn = container.getECFConnection();
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
			ECFConnection ecfConnection = getConnectionOrThrowIfNull();
			return new XMPPRoomID(container.getConnectNamespace(),
					ecfConnection.getXMPPConnection(), from);
		} catch (Exception e) {
			traceStack("Exception in createRoomIDFromName", e);
			return null;
		}
	}

	protected ID createUserIDFromName(String name) {
		ID result = null;
		try {
			result = new XMPPID(container.getConnectNamespace(), name);
			return result;
		} catch (Exception e) {
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
	 * @return
	 */
	public IChatManager getChatManager() {
		return chatManager;
	}

}