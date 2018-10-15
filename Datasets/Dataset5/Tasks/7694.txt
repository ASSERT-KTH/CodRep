public interface IChatRoomParticipantListener extends IParticipantListener {

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

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.presence.IParticipantListener;

/**
 * Listener interface for receiving participant arrive and departed
 * notifications
 * 
 */
public interface IChatParticipantListener extends IParticipantListener {
	/**
	 * Notification that participant arrived in associated chat room
	 * 
	 * @param participant
	 *            the ID of the arrived participant
	 */
	public void handleArrivedInChat(ID participant);

	/**
	 * Notification that participant departed the associated chat room
	 * 
	 * @param participant
	 *            the ID of the departed participant
	 */
	public void handleDepartedFromChat(ID participant);
}