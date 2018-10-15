public class IMMessageHandler implements IIMMessageHandler {

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
import org.eclipse.ecf.presence.bot.IIMBotEntry;
import org.eclipse.ecf.presence.bot.IIMMessageHandler;
import org.eclipse.ecf.presence.im.IChatMessage;

/**
 * Default im message handler that does nothing in response to
 * notifications.
 */
public class DefaultIMMessageHandler implements IIMMessageHandler {

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.bot.handler.IIMMessageHandler#handleRoomMessage(org.eclipse.ecf.presence.im.IChatMessage)
	 */
	public void handleIMMessage(IChatMessage message) {
		System.out.println("handleIMMessage("+message+")");
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
	 * @see org.eclipse.ecf.presence.bot.IIMMessageHandler#initRobot(org.eclipse.ecf.presence.bot.IIMBotEntry)
	 */
	public void initRobot(IIMBotEntry robot) {
	}

}