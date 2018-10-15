package org.eclipse.ecf.presence.chatroom;

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
package org.eclipse.ecf.presence.chat;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.presence.IMessageListener;

/**
 * Chat room container
 */
public interface IChatRoomContainer extends IContainer {

	/**
	 * Setup listener for handling IM messages
	 * 
	 * @param msgListener
	 *            the listener to add
	 */
	public void addMessageListener(IMessageListener msgListener);

	/**
	 * @param msgListener
	 */
	public void removeMessageListener(IMessageListener msgListener);

	/**
	 * Get interface for sending messages
	 * 
	 * @return IChatRoomMessageSender. Null if no message sender available
	 */
	public IChatRoomMessageSender getChatMessageSender();

	/**
	 * Add participant listener. The given listener will be notified if/when
	 * participants are added or removed from given room
	 * 
	 * @param participantListener
	 */
	public void addChatParticipantListener(
			IChatRoomParticipantListener participantListener);

	/**
	 * Remove chat participant listener
	 * 
	 * @param participantListener
	 *            the participant listener to remove
	 */
	public void removeChatParticipantListener(
			IChatRoomParticipantListener participantListener);
}