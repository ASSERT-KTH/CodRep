entry.execute(message, sender);

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
package org.eclipse.ecf.presence.bot;

import java.util.List;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.presence.bot.IChatBotEntry;
import org.eclipse.ecf.internal.presence.bot.ICommandEntry;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageEvent;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;

public class ChatBot implements IIMMessageListener {

	private IChatBotEntry bot;
	private IContainer container;
	private IChatRoomManager manager;
	private Namespace namespace;
	private IChatRoomMessageSender sender;

	public ChatBot(IChatBotEntry bot) {
		this.bot = bot;
		start();
	}

	private void start() {
		try {
			setup();

		} catch (ECFException e) {
			e.printStackTrace();
		}

	}

	protected void setup() throws ECFException {
		if (container == null) {
			container = ContainerFactory.getDefault().createContainer(bot.getContainerFactoryName());
			namespace = container.getConnectNamespace();
		}
		manager = (IChatRoomManager) container.getAdapter(IChatRoomManager.class);

		ID targetID = IDFactory.getDefault().createID(
				namespace,bot.getConnectID());
		container.connect(targetID, ConnectContextFactory.createPasswordConnectContext(bot.getPassword()));
		IChatRoomInfo room = manager.getChatRoomInfo(bot.getChatRoom());
		IChatRoomContainer roomContainer = room.createChatRoomContainer();
		roomContainer.connect(room.getRoomID(), null);
		roomContainer.addMessageListener(this);
		sender = roomContainer.getChatRoomMessageSender();
	}

	public void handleMessageEvent(IIMMessageEvent event) {
		if (event instanceof IChatRoomMessageEvent) {
			IChatRoomMessageEvent roomEvent = (IChatRoomMessageEvent) event;
			IChatRoomMessage message = roomEvent.getChatRoomMessage();
			List commands = bot.getCommands();
			for(int i = 0; i < commands.size(); i++) {
				ICommandEntry entry = (ICommandEntry) commands.get(i);
				entry.execute(message.getMessage(), sender);
			}
		}
	}
	
}