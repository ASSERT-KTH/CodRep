public class ChatRoomMessageHandler implements IChatRoomMessageHandler {

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

package org.eclipse.ecf.presence.bot.impl;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.presence.bot.IChatRoomBotEntry;
import org.eclipse.ecf.presence.bot.IChatRoomMessageHandler;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;

/**
 * Default chat room message handler that does nothing in response to
 * notifications.
 */
public class DefaultChatRoomMessageHandler implements IChatRoomMessageHandler {

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.bot.handler.IChatRoomMessageHandler#handleRoomMessage(org.eclipse.ecf.presence.chatroom.IChatRoomMessage)
	 */
	public void handleRoomMessage(IChatRoomMessage message) {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.bot.handler.IChatRoomContainerAdvisor#preChatRoomConnect(org.eclipse.ecf.presence.chatroom.IChatRoomContainer,
	 *      org.eclipse.ecf.core.identity.ID)
	 */
	public void preChatRoomConnect(IChatRoomContainer roomContainer, ID roomID) {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.bot.handler.IContainerAdvisor#init(org.eclipse.ecf.core.IContainer)
	 */
	public void init(IContainer container) {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.bot.handler.IContainerAdvisor#preContainerConnect(org.eclipse.ecf.core.identity.ID)
	 */
	public void preContainerConnect(ID targetID) {
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.bot.IChatRoomMessageHandler#initRobot(org.eclipse.ecf.presence.bot.IChatRoomBotEntry)
	 */
	public void initRobot(IChatRoomBotEntry robot) {
	}

}