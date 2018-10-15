List invitationsReceived = new ArrayList();

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

package org.eclipse.ecf.tests.presence;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomInvitationListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomInvitationSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;

/**
 * 
 */
public abstract class AbstractChatRoomInvitationTest extends AbstractPresenceTestCase {

	IChatRoomManager chat0, chat1 = null;
	public static final int WAITTIME = 20000;
	public static final String CHAT_ROOM_NAME = System.getProperty("chat.room.name");

	List<ID> invitationsReceived = new ArrayList<ID>();

	Object synchObject = new Object();

	IChatRoomInvitationListener invitationListener = new IChatRoomInvitationListener() {
		public void handleInvitationReceived(ID roomID, ID from, String subject, String body) {
			System.out.println("handleInvitationReceived(" + roomID + "," + from + "," + subject + "," + body + ")");
			invitationsReceived.add(roomID);
			synchronized (synchObject) {
				synchObject.notify();
			}
		}
	};

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.tests.presence.AbstractPresenceTestCase#setUp()
	 */
	protected void setUp() throws Exception {
		setClientCount(2);
		clients = createClients();
		chat0 = getPresenceAdapter(0).getChatRoomManager();
		chat1 = getPresenceAdapter(1).getChatRoomManager();
		chat1.addInvitationListener(invitationListener);
		for (int i = 0; i < 2; i++) {
			connectClient(i);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		invitationsReceived.clear();
		disconnectClients();
	}

	public void testSendInvitation() throws Exception {
		final IChatRoomInvitationSender invitationSender = chat0.getInvitationSender();
		assertNotNull(invitationSender);
		final IChatRoomInfo roomInfo = chat0.getChatRoomInfo(CHAT_ROOM_NAME);
		final IChatRoomContainer chatRoomContainer = roomInfo.createChatRoomContainer();
		chatRoomContainer.connect(roomInfo.getRoomID(), null);
		invitationSender.sendInvitation(roomInfo.getRoomID(), getClient(1).getConnectedID(), null, "this is an invitation");
		try {
			synchronized (synchObject) {
				synchObject.wait(WAITTIME);
			}
		} catch (final Exception e) {
			throw e;
		}
		assertHasEvent(invitationsReceived, ID.class);
	}

}