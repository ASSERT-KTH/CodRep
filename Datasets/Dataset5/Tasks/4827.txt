fireMessageEvent(toID, connectID, message);

/****************************************************************************
 * Copyright (c) 2006, 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.msn;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisposeEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.StringID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.ObjectCallback;
import org.eclipse.ecf.core.security.UnsupportedCallbackException;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.IAccountManager;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.IPresenceListener;
import org.eclipse.ecf.presence.IPresenceSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.im.ChatMessage;
import org.eclipse.ecf.presence.im.ChatMessageEvent;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.ecf.presence.im.IHistory;
import org.eclipse.ecf.presence.im.IHistoryManager;
import org.eclipse.ecf.presence.im.ITypingMessageSender;
import org.eclipse.ecf.presence.im.IChatMessage.Type;
import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterGroup;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.presence.roster.IRosterManager;
import org.eclipse.ecf.presence.roster.IRosterSubscriptionListener;
import org.eclipse.ecf.presence.roster.IRosterSubscriptionSender;
import org.eclipse.ecf.presence.roster.IRosterUpdateListener;
import org.hantsuki.gokigenyou.ChatSession;
import org.hantsuki.gokigenyou.Contact;
import org.hantsuki.gokigenyou.Group;
import org.hantsuki.gokigenyou.MsnClient;
import org.hantsuki.gokigenyou.Status;
import org.hantsuki.gokigenyou.events.IChatSessionListener;
import org.hantsuki.gokigenyou.events.IContactListListener;
import org.hantsuki.gokigenyou.events.IContactListener;
import org.hantsuki.gokigenyou.events.ISessionListener;

final class MSNContainer implements IContainer, IChatManager,
		IChatMessageSender, IPresenceSender, IPresenceContainerAdapter,
		IRoster, IRosterManager, IRosterSubscriptionSender,
		ITypingMessageSender {

	private static final long serialVersionUID = 1676711994010767942L;

	private final Map chatSessions;

	private final List containerListeners;

	private final List updateListeners;

	private final List messageListeners;

	private final List presenceListeners;

	private final List subscriptionListeners;

	private final List entries;

	private final IUser user;

	private MsnClient client;

	private final ID guid;

	private ID connectID;

	protected IHistoryManager historyManager = new IHistoryManager() {

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.presence.im.IHistoryManager#getHistory(org.eclipse.ecf.core.identity.ID, java.util.Map)
		 */
		public IHistory getHistory(ID partnerID, Map options) {
			// XXX TODO provide local storage (with some 
			return null;
		}

		/* (non-Javadoc)
		 * @see org.eclipse.core.runtime.IAdaptable#getAdapter(java.lang.Class)
		 */
		public Object getAdapter(Class adapter) {
			return null;
		}

		public boolean isActive() {
			return false;
		}

		public void makeActive(boolean active, Map options) {
		}
	};
	

	MSNContainer() throws IDCreateException {
		guid = IDFactory.getDefault().createGUID();
		user = new Account();
		chatSessions = new Hashtable();
		containerListeners = new ArrayList();
		updateListeners = new ArrayList();
		messageListeners = new ArrayList();
		presenceListeners = new ArrayList();
		subscriptionListeners = new ArrayList();
		entries = new ArrayList();
	}

	public synchronized void connect(ID targetID, IConnectContext connectContext)
			throws ContainerConnectException {
		if (!(targetID instanceof StringID)) {
			throw new ContainerConnectException();
		}

		connectID = targetID;
		client = new MsnClient();
		ObjectCallback[] cb = { new ObjectCallback() };
		try {
			connectContext.getCallbackHandler().handle(cb);
			client.addSessionListener(new ISessionListener() {
				public void sessionConnected(ChatSession session) {
					try {
						final ID toID = IDFactory.getDefault().createStringID(
								session.getParticipants()[0].getEmail());
						chatSessions.put(toID, session);
						session.addChatSessionListener(new ChatSessionListener(
								toID));
					} catch (IDCreateException e) {
						e.printStackTrace();
					}
				}
			});

			client.getContactList().addContactListListener(
					new IContactListListener() {

						public void contactAdded(Contact contact) {
							final MSNRosterEntry entry = new MSNRosterEntry(
									contact);
							contact.addContactListener(new IContactListener() {

								public void nameChanged(String name) {
									fireRosterUpdate(entry);
									fireRosterEntryUpdated(entry);
								}

								public void personalMessageChanged(
										String personalMessage) {
									fireRosterUpdate(entry);
									fireRosterEntryUpdated(entry);
								}

								public void statusChanged(Status status) {
									fireRosterUpdate(entry);
									fireRosterEntryUpdated(entry);
								}

							});

							for (int i = 0; i < entries.size(); i++) {
								MSNRosterGroup group = (MSNRosterGroup) entries
										.get(i);
								if (group.getGroup().contains(contact)) {
									group.add(entry);
									fireRosterUpdate(group);
									fireRosterEntryAdded(entry);
									return;
								}
							}

							entries.add(entry);
							fireRosterEntryAdded(entry);
						}

						public void contactRemoved(Contact contact) {
							IRosterEntry entry = findEntry(entries, contact
									.getEmail());
							if (entry != null) {
								fireHandleUnsubscribed(entry.getUser().getID());
							}
						}

						public void contactAddedUser(String email) {
							try {
								fireHandleSubscriptionRequest(IDFactory
										.getDefault().createStringID(email));
							} catch (IDCreateException e) {
								// ignored
							}
						}

						public void groupAdded(Group group) {
							entries.add(new MSNRosterGroup(MSNContainer.this,
									group));
						}

					});

			fireContainerEvent(new ContainerConnectingEvent(guid, connectID));
			client.connect(connectID.getName(), (String) cb[0].getObject());
			fireContainerEvent(new ContainerConnectedEvent(guid, connectID));
		} catch (UnsupportedCallbackException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private MSNRosterEntry findEntry(Collection entries, String email) {
		for (Iterator it = entries.iterator(); it.hasNext();) {
			Object o = it.next();
			if (o instanceof IRosterGroup) {
				MSNRosterEntry entry = findEntry(((IRosterGroup) o)
						.getEntries(), email);
				if (entry != null) {
					return entry;
				}
			} else {
				MSNRosterEntry entry = (MSNRosterEntry) o;
				if (entry.getUser().getID().getName().equals(email)) {
					return entry;
				}
			}
		}
		return null;
	}

	public synchronized void disconnect() {
		if (client != null) {
			for (Iterator it = chatSessions.values().iterator(); it.hasNext();) {
				((ChatSession) it.next()).close();
			}
			fireContainerEvent(new ContainerDisconnectingEvent(guid, connectID));
			client.disconnect();
			fireContainerEvent(new ContainerDisconnectedEvent(guid, connectID));
			connectID = null;
			client = null;
		}
	}

	public void dispose() {
		disconnect();
		fireContainerEvent(new ContainerDisposeEvent(guid));
	}

	private void fireContainerEvent(IContainerEvent event) {
		synchronized (containerListeners) {
			for (int i = 0; i < containerListeners.size(); i++) {
				((IContainerListener) containerListeners.get(i))
						.handleEvent(event);
			}
		}
	}

	private void fireMessageEvent(ID fromID, ID toID, String message) {
		synchronized (messageListeners) {
			for (int i = 0; i < messageListeners.size(); i++) {
				((IIMMessageListener) messageListeners.get(i))
						.handleMessageEvent(new ChatMessageEvent(fromID,
								new ChatMessage(fromID, toID, null, message,
										Collections.EMPTY_MAP)));
			}
		}
	}

	private void fireRosterUpdate(IRosterItem item) {
		synchronized (updateListeners) {
			for (int i = 0; i < updateListeners.size(); i++) {
				((IRosterUpdateListener) updateListeners.get(i))
						.handleRosterUpdate(this, item);
			}
		}
	}

	private void fireRosterEntryAdded(IRosterEntry entry) {
		synchronized (presenceListeners) {
			for (int i = 0; i < presenceListeners.size(); i++) {
				((IPresenceListener) presenceListeners.get(i))
						.handleRosterEntryAdd(entry);
			}
		}
	}

	private void fireRosterEntryUpdated(IRosterEntry entry) {
		synchronized (presenceListeners) {
			for (int i = 0; i < presenceListeners.size(); i++) {
				((IPresenceListener) presenceListeners.get(i))
						.handleRosterEntryUpdate(entry);
			}
		}
	}

	private void fireHandleSubscriptionRequest(ID fromID) {
		synchronized (subscriptionListeners) {
			for (int i = 0; i < subscriptionListeners.size(); i++) {
				((IRosterSubscriptionListener) subscriptionListeners.get(i))
						.handleSubscribeRequest(fromID);
			}
		}
	}

	private void fireHandleUnsubscribed(ID fromID) {
		synchronized (subscriptionListeners) {
			for (int i = 0; i < subscriptionListeners.size(); i++) {
				((IRosterSubscriptionListener) subscriptionListeners.get(i))
						.handleUnsubscribed(fromID);
			}
		}
	}

	public Object getAdapter(Class serviceType) {
		if (serviceType != null && serviceType.isInstance(this)) {
			return this;
		} else {
			return null;
		}
	}

	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(
				StringID.class.getName());
	}

	public ID getConnectedID() {
		return connectID;
	}

	public ID getID() {
		return guid;
	}

	public IAccountManager getAccountManager() {
		return null;
	}

	public IChatRoomManager getChatRoomManager() {
		return null;
	}

	public IPresenceSender getPresenceSender() {
		return this;
	}

	public void addListener(IContainerListener listener) {
		if (listener != null) {
			synchronized (containerListeners) {
				if (!containerListeners.contains(listener)) {
					containerListeners.add(listener);
				}
			}
		}
	}

	public void removeListener(IContainerListener listener) {
		if (listener != null) {
			synchronized (containerListeners) {
				containerListeners.remove(listener);
			}
		}
	}

	private class ChatSessionListener implements IChatSessionListener {

		private ID toID;

		private ChatSessionListener(ID toID) {
			this.toID = toID;
		}

		public void contactIsTyping(Contact contact) {
		}

		public void contactJoined(Contact contact) {
		}

		public void contactLeft(Contact contact) {
			chatSessions.remove(toID);
		}

		public void messageReceived(Contact contact, String message) {
			fireMessageEvent(toID, toID, message);
		}

		public void sessionTimedOut() {
			chatSessions.remove(toID);
		}

	}

	public void sendPresenceUpdate(ID toID, IPresence presence)
			throws ECFException {
		if (presence == null || client == null) {
			throw new ECFException();
		}

		IPresence.Mode mode = presence.getMode();
		try {
			if (presence.getType() == IPresence.Type.UNAVAILABLE) {
				disconnect();
			} else if (mode == IPresence.Mode.AVAILABLE
					|| mode == IPresence.Mode.CHAT) {
				client.setStatus(Status.ONLINE);
			} else if (mode == IPresence.Mode.AWAY
					|| mode == IPresence.Mode.EXTENDED_AWAY) {
				client.setStatus(Status.AWAY);
			} else if (mode == IPresence.Mode.DND) {
				client.setStatus(Status.BUSY);
			} else {
				client.setStatus(Status.APPEAR_OFFLINE);
			}
			client.setPersonalMessage(presence.getStatus());
		} catch (IOException e) {
			throw new ECFException(e);
		}
	}

	public IRosterManager getRosterManager() {
		return this;
	}

	public void addRosterUpdateListener(IRosterUpdateListener listener) {
		synchronized (updateListeners) {
			if (!updateListeners.contains(listener)) {
				updateListeners.add(listener);
			}
		}
	}

	public IRoster getRoster() {
		return this;
	}

	public IRosterSubscriptionSender getRosterSubscriptionSender() {
		return this;
	}

	public void addRosterSubscriptionListener(
			IRosterSubscriptionListener listener) {
		if (listener != null) {
			synchronized (subscriptionListeners) {
				if (!subscriptionListeners.contains(listener)) {
					subscriptionListeners.add(listener);
				}
			}
		}
	}

	public void removeRosterSubscriptionListener(
			IRosterSubscriptionListener listener) {
		if (listener != null) {
			synchronized (subscriptionListeners) {
				subscriptionListeners.remove(listener);
			}
		}
	}

	public void removeRosterUpdateListener(IRosterUpdateListener listener) {
		if (listener != null) {
			synchronized (updateListeners) {
				updateListeners.remove(listener);
			}
		}
	}

	public Collection getItems() {
		return Collections.unmodifiableCollection(entries);
	}

	public IUser getUser() {
		return connectID == null ? null : user;
	}

	public void addPresenceListener(IPresenceListener listener) {
		if (listener != null) {
			synchronized (presenceListeners) {
				if (!presenceListeners.contains(listener)) {
					presenceListeners.add(listener);
				}
			}
		}
	}

	public void removePresenceListener(IPresenceListener listener) {
		if (listener != null) {
			synchronized (presenceListeners) {
				presenceListeners.remove(listener);
			}
		}
	}

	public IChatManager getChatManager() {
		return this;
	}

	public IChatMessageSender getChatMessageSender() {
		return this;
	}

	public ITypingMessageSender getTypingMessageSender() {
		return this;
	}

	public void sendChatMessage(ID toID, ID threadID, Type type,
			String subject, String body, Map properties) throws ECFException {
		sendChatMessage(toID, body);
	}

	public void sendChatMessage(ID toID, String body) throws ECFException {
		try {
			ChatSession cs = (ChatSession) chatSessions.get(toID);
			if (cs == null) {
				cs = client.createChatSession(toID.getName());
				cs.addChatSessionListener(new ChatSessionListener(toID));
				chatSessions.put(toID, cs);
			}
			cs.sendMessage(body);
			fireMessageEvent(connectID, toID, body);
		} catch (IOException e) {
			throw new ECFException(e);
		}
	}

	public void sendTypingMessage(ID toID, boolean isTyping, String body)
			throws ECFException {
		try {
			if (isTyping) {
				ChatSession cs = (ChatSession) chatSessions.get(toID);
				if (cs == null) {
					cs = client.createChatSession(toID.getName());
					cs.addChatSessionListener(new ChatSessionListener(toID));
					chatSessions.put(toID, cs);
				}
				cs.sendTypingNotification();
			}
		} catch (IOException e) {
			throw new ECFException(e);
		}
	}

	public void addMessageListener(IIMMessageListener listener) {
		if (listener != null) {
			synchronized (messageListeners) {
				if (!messageListeners.contains(listener)) {
					messageListeners.add(listener);
				}
			}
		}
	}

	public void removeMessageListener(IIMMessageListener listener) {
		if (listener != null) {
			synchronized (messageListeners) {
				messageListeners.remove(listener);
			}
		}
	}

	private class Account implements IUser {

		private static final long serialVersionUID = 7497082891662391996L;

		public Object getAdapter(Class adapter) {
			return null;
		}

		public ID getID() {
			return connectID;
		}

		public Map getProperties() {
			return null;
		}

		public String getName() {
			return client.getDisplayName();
		}

		public String getNickname() {
			return client.getDisplayName();
		}

	}

	public void sendRosterAdd(String user, String name, String[] groups)
			throws ECFException {
		// TODO: implement this when the protocol implementation supports this
		throw new UnsupportedOperationException();
	}

	public void sendRosterRemove(ID userID) throws ECFException {
		MSNRosterEntry entry = findEntry(entries, userID.getName());
		if (entry != null) {
			try {
				client.getContactList().removeContact(entry.getContact());
			} catch (IOException e) {
				throw new ECFException(e);
			}
		}
	}

	public String getName() {
		IUser user = getUser();
		return user == null ? null : user.getName();
	}

	public IRosterItem getParent() {
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.im.IChatManager#getHistoryManager()
	 */
	public IHistoryManager getHistoryManager() {
		return historyManager;
	}

}