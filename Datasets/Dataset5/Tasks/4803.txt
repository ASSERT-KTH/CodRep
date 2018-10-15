package org.eclipse.ecf.internal.provider.xmpp.deprecated;

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

package org.eclipse.ecf.provider.xmpp.container;

import java.io.IOException;
import java.util.Iterator;
import java.util.Vector;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.im.ChatMessage;
import org.eclipse.ecf.presence.im.ChatMessageEvent;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.im.IChatMessage;
import org.eclipse.ecf.presence.im.IChatMessageEvent;
import org.eclipse.ecf.presence.im.IChatMessageListener;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Message.Type;

/**
 * Chat manager for XMPP container
 */
public class XMPPChatManager implements IChatManager {

	protected Vector messageListeners = new Vector();

	protected XMPPPresenceSharedObject presenceHelper;

	protected IChatMessageSender chatMessageSender = new IChatMessageSender() {

		public void sendChatMessage(ID toID, IChatMessage message)
				throws ECFException {
			XMPPChatManager.this.sendChatMessage(toID, message);
		}

	};

	public XMPPChatManager(XMPPPresenceSharedObject presenceHelper) {
		this.presenceHelper = presenceHelper;
	}

	/**
	 * @param toID
	 * @param message
	 */
	protected void sendChatMessage(ID toID, IChatMessage message)
			throws ECFException {
		if (toID == null)
			throw new ECFException("receiver cannot be null");
		if (message == null)
			throw new ECFException("message cannot be null");
		try {
			presenceHelper.getConnectionOrThrowIfNull().sendMessage(toID,
					message.getThreadID(),
					createMessageType(message.getType()), message.getSubject(),
					message.getBody());
		} catch (IOException e) {
			throw new ECFException("sendChatMessage exception", e);
		}
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
	 * @see org.eclipse.ecf.presence.im.IChatManager#addChatMessageListener(org.eclipse.ecf.presence.im.IChatMessageListener)
	 */
	public void addChatMessageListener(IChatMessageListener listener) {
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
	 * @see org.eclipse.ecf.presence.im.IChatManager#removeChatMessageListener(org.eclipse.ecf.presence.im.IChatMessageListener)
	 */
	public void removeChatMessageListener(IChatMessageListener listener) {
		messageListeners.remove(listener);
	}

	private void fireChatMessageEvent(IChatMessageEvent event) {
		for (Iterator i = messageListeners.iterator(); i.hasNext();) {
			IChatMessageListener l = (IChatMessageListener) i.next();
			l.handleChatMessageEvent(event);
		}
	}

	protected void fireChatMessage(ID fromID, ID threadID, Type type,
			String subject, String body) {
		fireChatMessageEvent(new ChatMessageEvent(fromID, new ChatMessage(
				threadID, createMessageType(type), subject, body)));
	}

}