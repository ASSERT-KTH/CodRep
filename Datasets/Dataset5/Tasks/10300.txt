public IChat createChat(ID targetUser, IIMMessageListener messageListener) throws ECFException {

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

package org.eclipse.ecf.internal.provider.xmpp;

import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.history.IHistory;
import org.eclipse.ecf.presence.history.IHistoryManager;
import org.eclipse.ecf.presence.im.ChatMessage;
import org.eclipse.ecf.presence.im.ChatMessageEvent;
import org.eclipse.ecf.presence.im.IChat;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.im.IChatMessage;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.ecf.presence.im.ITypingMessage;
import org.eclipse.ecf.presence.im.ITypingMessageSender;
import org.eclipse.ecf.presence.im.TypingMessageEvent;
import org.eclipse.ecf.presence.im.XHTMLChatMessage;
import org.eclipse.ecf.presence.im.XHTMLChatMessageEvent;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Message.Type;

/**
 * Chat manager for XMPP container
 */
public class XMPPChatManager implements IChatManager {

	protected Vector messageListeners = new Vector();

	protected XMPPContainerPresenceHelper presenceHelper;

	protected IChatMessageSender chatMessageSender = new IChatMessageSender() {

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.im.IChatMessageSender#sendChatMessage(org.eclipse.ecf.core.identity.ID,
		 *      org.eclipse.ecf.core.identity.ID,
		 *      org.eclipse.ecf.presence.im.IChatMessage.Type, java.lang.String,
		 *      java.lang.String)
		 */
		public void sendChatMessage(ID toID, ID threadID,
				org.eclipse.ecf.presence.im.IChatMessage.Type type,
				String subject, String body, Map properties)
				throws ECFException {
			if (toID == null)
				throw new ECFException("receiver cannot be null");
			try {
				presenceHelper.getConnectionOrThrowIfNull().sendMessage(toID,
						threadID, XMPPChatManager.this.createMessageType(type),
						subject, body, properties);
			} catch (Exception e) {
				throw new ECFException("sendChatMessage exception", e);
			}

		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.presence.im.IChatMessageSender#sendChatMessage(org.eclipse.ecf.core.identity.ID,
		 *      java.lang.String)
		 */
		public void sendChatMessage(ID toID, String body) throws ECFException {
			sendChatMessage(toID, null, IChatMessage.Type.CHAT, null, body,
					null);
		}

	};

	protected ITypingMessageSender typingMessageSender = new ITypingMessageSender() {

		public void sendTypingMessage(ID toID, boolean isTyping, String body)
				throws ECFException {
			if (toID == null)
				throw new ECFException("receiver cannot be null");
			try {
				presenceHelper.sendTypingMessage(toID, isTyping, body);
			} catch (Exception e) {
				throw new ECFException("sendChatMessage exception", e);
			}
		}

	};

	protected IHistoryManager historyManager = new IHistoryManager() {

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.presence.im.IChatHistoryManager#getHistory(org.eclipse.ecf.core.identity.ID, java.util.Map)
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

		public void setActive(boolean active) {
			// TODO Auto-generated method stub
			
		}
	};
	

	public XMPPChatManager(XMPPContainerPresenceHelper presenceHelper) {
		this.presenceHelper = presenceHelper;
	}

	protected IChatMessage.Type createMessageType(Message.Type type) {
		if (type == null)
			return IChatMessage.Type.CHAT;
		if (type == Message.Type.CHAT) {
			return IChatMessage.Type.CHAT;
		} else if (type == Message.Type.HEADLINE) {
			return IChatMessage.Type.SYSTEM;
		} else
			return IChatMessage.Type.CHAT;
	}

	protected Message.Type createMessageType(IChatMessage.Type type) {
		if (type == null)
			return Message.Type.NORMAL;
		if (type == IChatMessage.Type.CHAT) {
			return Message.Type.CHAT;
		} else if (type == IChatMessage.Type.SYSTEM) {
			return Message.Type.HEADLINE;
		} else
			return Message.Type.NORMAL;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.im.IChatManager#addChatMessageListener(org.eclipse.ecf.presence.im.IIMMessageListener)
	 */
	public void addMessageListener(IIMMessageListener listener) {
		messageListeners.add(listener);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.im.IChatManager#getChatMessageSender()
	 */
	public IChatMessageSender getChatMessageSender() {
		return chatMessageSender;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.im.IChatManager#removeChatMessageListener(org.eclipse.ecf.presence.im.IIMMessageListener)
	 */
	public void removeMessageListener(IIMMessageListener listener) {
		messageListeners.remove(listener);
	}

	private void fireMessageEvent(IIMMessageEvent event) {
		for (Iterator i = messageListeners.iterator(); i.hasNext();) {
			IIMMessageListener l = (IIMMessageListener) i.next();
			l.handleMessageEvent(event);
		}
	}

	protected void fireChatMessage(ID fromID, ID threadID, Type type,
			String subject, String body, Map properties) {
		fireMessageEvent(new ChatMessageEvent(fromID, new ChatMessage(fromID,
				threadID, createMessageType(type), subject, body, properties)));
	}

	protected void fireTypingMessage(ID fromID, ITypingMessage typingMessage) {
		fireMessageEvent(new TypingMessageEvent(fromID, typingMessage));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.im.IChatManager#getTypingMessageSender()
	 */
	public ITypingMessageSender getTypingMessageSender() {
		return typingMessageSender;
	}

	protected void fireXHTMLChatMessage(ID fromID, ID threadID, Type type,
			String subject, String body, Map properties, List xhtmlbodylist) {
		fireMessageEvent(new XHTMLChatMessageEvent(fromID,
				new XHTMLChatMessage(fromID, threadID, createMessageType(type),
						subject, body, properties, xhtmlbodylist)));

	}

	public IHistoryManager getHistoryManager() {
		return historyManager;
	}
	
	public void disconnect() {
		messageListeners.clear();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.im.IChatManager#createChat(org.eclipse.ecf.core.identity.ID)
	 */
	public IChat createChat(ID targetUser) throws ECFException {
		// TODO Auto-generated method stub
		return null;
	}
}