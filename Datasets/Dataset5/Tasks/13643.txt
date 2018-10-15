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

import org.eclipse.ecf.core.identity.ID;

/**
 * Invitation listener for handling asynchronous chat room invitation events.
 * Instances implementing this interface must be registered via the
 * {@link IChatRoomManager#addInvitationListener(IChatRoomInvitationListener)}
 * 
 * @see IChatRoomManager#addInvitationListener(IChatRoomInvitationListener)
 */
public interface IChatRoomInvitationListener {

	/**
	 * Handle notification of a received invitation to join chat room. This
	 * method will be called by some thread when an invitiation is received by
	 * this user account to join a chat room
	 * 
	 * @param roomID
	 *            the room id associated with the invitation
	 * @param from
	 *            the id of the sender
	 * @param subject
	 *            a subject for the invitation
	 * @param body
	 *            a message body for the invitation
	 */
	public void handleInvitationReceived(ID roomID, ID from, String subject,
			String body);
}