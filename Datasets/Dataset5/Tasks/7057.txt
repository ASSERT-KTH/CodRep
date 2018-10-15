import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.provider.xmpp;

import java.net.URISyntaxException;
import java.util.Iterator;
import java.util.Vector;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectConfig;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContext;
import org.eclipse.ecf.core.sharedobject.SharedObjectInitException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chat.IChatRoomParticipantListener;
import org.eclipse.ecf.provider.xmpp.events.ChatMembershipEvent;
import org.eclipse.ecf.provider.xmpp.events.MessageEvent;
import org.eclipse.ecf.provider.xmpp.events.PresenceEvent;
import org.eclipse.ecf.provider.xmpp.identity.XMPPID;
import org.eclipse.ecf.provider.xmpp.identity.XMPPRoomID;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smack.packet.Presence.Mode;
import org.jivesoftware.smack.packet.Presence.Type;

public class XMPPChatRoomContainerHelper implements ISharedObject {

	ISharedObjectConfig config = null;

	Vector messageListeners = new Vector();
	Namespace usernamespace = null;
	XMPPConnection connection = null;
	Vector participantListeners = new Vector();

	protected void trace(String message) {

	}

	protected void addChatParticipantListener(IChatRoomParticipantListener listener) {
		participantListeners.add(listener);
	}

	protected void removeChatParticipantListener(
			IChatRoomParticipantListener listener) {
		participantListeners.remove(listener);
	}

	protected void addMessageListener(IMessageListener listener) {
		messageListeners.add(listener);
	}

	protected void removeMessageListener(IMessageListener listener) {
		messageListeners.add(listener);
	}

	public XMPPChatRoomContainerHelper(Namespace usernamespace,
			XMPPConnection conn) {
		super();
		this.usernamespace = usernamespace;
		this.connection = conn;
	}

	protected ISharedObjectContext getContext() {
		return config.getContext();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
	 */
	public void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
	}

	protected ID createUserIDFromName(String name) {
		ID result = null;
		try {
			result = new XMPPID(usernamespace, name);
			return result;
		} catch (Exception e) {
			return null;
		}
	}

	protected Message.Type[] ALLOWED_MESSAGES = { Message.Type.GROUP_CHAT };

	protected Message filterMessageType(Message msg) {
		for (int i = 0; i < ALLOWED_MESSAGES.length; i++) {
			if (ALLOWED_MESSAGES[i].equals(msg.getType())) {
				return msg;
			}
		}
		return null;
	}

	protected String canonicalizeRoomFrom(String from) {
		if (from == null)
			return null;
		int atIndex = from.indexOf('@');
		String hostname = null;
		String username = null;
		int index = from.indexOf("/");
		if (atIndex > 0 && index > 0) {
			hostname = from.substring(atIndex + 1, index);
			username = from.substring(index + 1);
			return username + "@" + hostname;
		}
		return from;
	}

	protected IMessageListener.Type createMessageType(Message.Type type) {
		if (type == null)
			return IMessageListener.Type.NORMAL;
		if (type == Message.Type.CHAT) {
			return IMessageListener.Type.CHAT;
		} else if (type == Message.Type.NORMAL) {
			return IMessageListener.Type.NORMAL;
		} else if (type == Message.Type.GROUP_CHAT) {
			return IMessageListener.Type.GROUP_CHAT;
		} else if (type == Message.Type.HEADLINE) {
			return IMessageListener.Type.SYSTEM;
		} else if (type == Message.Type.HEADLINE) {
			return IMessageListener.Type.SYSTEM;
		} else
			return IMessageListener.Type.NORMAL;
	}

	protected void fireMessage(ID from, ID to, IMessageListener.Type type,
			String subject, String body) {
		for (Iterator i = messageListeners.iterator(); i.hasNext();) {
			IMessageListener l = (IMessageListener) i.next();
			l.handleMessage(from, to, type, subject, body);
		}
	}

	protected String canonicalizeRoomTo(String to) {
		if (to == null)
			return null;
		int index = to.indexOf("/");
		if (index > 0) {
			return to.substring(0, index);
		} else
			return to;
	}

	protected ID createRoomIDFromName(String from) {
		try {
			return new XMPPRoomID(usernamespace, connection, from);
		} catch (URISyntaxException e) {
			return null;
		}
	}

	protected void handleMessageEvent(MessageEvent evt) {
		Message msg = evt.getMessage();
		String from = msg.getFrom();
		String to = msg.getTo();
		String body = msg.getBody();
		String subject = msg.getSubject();
		ID fromID = createUserIDFromName(canonicalizeRoomFrom(from));
		ID toID = createUserIDFromName(canonicalizeRoomTo(to));
		msg = filterMessageType(msg);
		if (msg != null)
			fireMessage(fromID, toID, createMessageType(msg.getType()),
					subject, body);
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

	protected IPresence createIPresence(Presence xmppPresence) {
		String status = xmppPresence.getStatus();
		IPresence newPresence = new org.eclipse.ecf.presence.Presence(
				createIPresenceType(xmppPresence), status,
				createIPresenceMode(xmppPresence));
		return newPresence;
	}

	protected void handlePresenceEvent(PresenceEvent evt) {
		Presence xmppPresence = evt.getPresence();
		String from = canonicalizeRoomFrom(xmppPresence.getFrom());
		IPresence newPresence = createIPresence(xmppPresence);
		ID fromID = createUserIDFromName(from);
		fireParticipant(fromID, newPresence);
	}

	protected void handleChatMembershipEvent(ChatMembershipEvent evt) {
		String from = canonicalizeRoomFrom(evt.getFrom());
		ID fromID = createUserIDFromName(from);
		fireChatParticipant(fromID, evt.isAdd());
	}

	protected void fireParticipant(ID fromID, IPresence presence) {
		for (Iterator i = participantListeners.iterator(); i.hasNext();) {
			IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();
			l.handlePresence(fromID, presence);
		}
	}

	protected void fireChatParticipant(ID fromID, boolean join) {
		for (Iterator i = participantListeners.iterator(); i.hasNext();) {
			IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();
			if (join) {
				l.handleArrivedInChat(fromID);
			} else {
				l.handleDepartedFromChat(fromID);
			}
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
	 */
	public void handleEvent(Event event) {
		trace("handleEvent(" + event + ")");
		if (event instanceof MessageEvent) {
			handleMessageEvent((MessageEvent) event);
		} else if (event instanceof PresenceEvent) {
			handlePresenceEvent((PresenceEvent) event);
		} else if (event instanceof ChatMembershipEvent) {
			handleChatMembershipEvent((ChatMembershipEvent) event);
		} else
			trace("unrecognized event " + event);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
	 */
	public void handleEvents(Event[] events) {
		for (int i = 0; i < events.length; i++) {
			this.handleEvent(events[i]);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
	 */
	public void dispose(ID containerID) {
		messageListeners.clear();
		participantListeners.clear();
		this.config = null;
		this.connection = null;
		this.usernamespace = null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		return null;
	}
}