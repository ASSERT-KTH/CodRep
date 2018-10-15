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

import org.eclipse.ecf.core.util.ECFException;

/**
 * Chat message sender. Interface for sending chat messages within an
 * {@link IChatRoomContainer}. Access to instances implementing this interface
 * is provided via the {@link IChatRoomContainer#getChatMessageSender()}
 * 
 * @see IChatRoomContainer
 */
public interface IChatRoomMessageSender {
	/**
	 * Send a message to chat room
	 * 
	 * @param message
	 *            the message to send
	 * @throws ECFException
	 *             thrown if message cannot be sent (e.g. because of previous
	 *             disconnect)
	 */
	public void sendMessage(String message) throws ECFException;
}