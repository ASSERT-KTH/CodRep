roomContainer = room.createChatRoomContainer();

/*******************************************************************************
 * Copyright (c) 2007 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.presence.bot.impl;

import java.util.List;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.presence.bot.Messages;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.bot.IChatRoomBotEntry;
import org.eclipse.ecf.presence.bot.IChatRoomMessageHandlerEntry;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageEvent;

/**
 * Default chat room robot implementation class.
 */
public class ChatRoomBot implements IIMMessageListener {

	protected IChatRoomBotEntry bot;
	protected IContainer container;
	protected ID targetID;
	protected IChatRoomContainer roomContainer;
	protected ID roomID;

	public ChatRoomBot(IChatRoomBotEntry bot) {
		this.bot = bot;
	}

	protected void fireInitBot() {
		List commands = bot.getCommands();
		for (int i = 0; i < commands.size(); i++) {
			IChatRoomMessageHandlerEntry entry = (IChatRoomMessageHandlerEntry) commands
					.get(i);
			entry.getHandler().init(bot);
		}
	}

	protected void firePreConnect() {
		List commands = bot.getCommands();
		for (int i = 0; i < commands.size(); i++) {
			IChatRoomMessageHandlerEntry entry = (IChatRoomMessageHandlerEntry) commands
					.get(i);
			entry.getHandler().preContainerConnect(container, targetID);
		}
	}

	protected void firePreRoomConnect() {
		List commands = bot.getCommands();
		for (int i = 0; i < commands.size(); i++) {
			IChatRoomMessageHandlerEntry entry = (IChatRoomMessageHandlerEntry) commands
					.get(i);
			entry.getHandler().preChatRoomConnect(roomContainer, roomID);
		}
	}

	public synchronized void connect() throws ECFException {

		fireInitBot();

		try {
			Namespace namespace = null;

			if (container == null) {
				container = ContainerFactory.getDefault().createContainer(
						bot.getContainerFactoryName());
				namespace = container.getConnectNamespace();
			} else
				throw new ContainerConnectException(
						Messages.DefaultChatRoomBot_EXCEPTION_ALREADY_CONNECTED);

			targetID = IDFactory.getDefault().createID(namespace,
					bot.getConnectID());

			IChatRoomManager manager = (IChatRoomManager) container
					.getAdapter(IChatRoomManager.class);

			if (manager == null)
				throw new ECFException(
						Messages.DefaultChatRoomBot_EXCEPTION_NO_CHAT_ROOM);

			firePreConnect();

			String password = bot.getPassword();
			IConnectContext context = (password == null) ? null
					: ConnectContextFactory
							.createPasswordConnectContext(password);

			container.connect(targetID, context);

			IChatRoomInfo room = manager.getChatRoomInfo(bot.getChatRoom());
			IChatRoomContainer roomContainer = room.createChatRoomContainer();

			roomID = room.getRoomID();

			firePreRoomConnect();

			roomContainer.addMessageListener(this);

			String roomPassword = bot.getChatRoomPassword();
			IConnectContext roomContext = (roomPassword == null) ? null
					: ConnectContextFactory
							.createPasswordConnectContext(roomPassword);
			roomContainer.connect(roomID, roomContext);

		} catch (ECFException e) {
			if (container != null) {
				if (container.getConnectedID() != null) {
					container.disconnect();
				}
				container.dispose();
			}
			container = null;
			throw e;
		}

	}

	public void handleMessageEvent(IIMMessageEvent event) {
		if (event instanceof IChatRoomMessageEvent) {
			IChatRoomMessageEvent roomEvent = (IChatRoomMessageEvent) event;
			IChatRoomMessage message = roomEvent.getChatRoomMessage();
			List commands = bot.getCommands();
			for (int i = 0; i < commands.size(); i++) {
				IChatRoomMessageHandlerEntry entry = (IChatRoomMessageHandlerEntry) commands
						.get(i);
				entry.handleRoomMessage(message);
			}
		}
	}

}