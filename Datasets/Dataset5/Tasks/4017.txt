client.sendChat(targetIMUser, "Hi, I'm an IM robot");

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.example.clients.applications;

import org.eclipse.core.runtime.IPlatformRunnable;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.example.clients.IMessageReceiver;
import org.eclipse.ecf.example.clients.XMPPChatClient;
import org.eclipse.ecf.presence.im.IChatMessage;

public class ChatSORobotApplication implements IPlatformRunnable,
		IMessageReceiver {

	private boolean running = false;
	private String userName;
	private XMPPChatClient client;
	private String targetIMUser;
	private TrivialSharedObject sharedObject = null;

	public synchronized Object run(Object args) throws Exception {
		if (args instanceof Object[]) {
			Object[] arguments = (Object[]) args;
			int l = arguments.length;
			if (arguments[l-1] instanceof String
					&& arguments[l-2] instanceof String
					&& arguments[l-3] instanceof String
					&& arguments[l-4] instanceof String) {
				userName = (String) arguments[l-4];
				String hostName = (String) arguments[l-3];
				String password = (String) arguments[l-2];
				String targetName = (String) arguments[l-1];
				runRobot(hostName, password, targetName);
				return new Integer(0);
			}
		}

		System.out
				.println("Usage: pass in four arguments (username, hostname, password, targetIMUser)");
		return new Integer(-1);
	}

	private void runRobot(String hostName, String password, String targetIMUser)
			throws ECFException, Exception, InterruptedException {
		// Create client and connect to host
		client = new XMPPChatClient(this);
		client.setupContainer();
		client.setupPresence();

		// Get ISharedObjectContainer adapter
		ISharedObjectContainer socontainer = (ISharedObjectContainer) client
				.getContainer().getAdapter(ISharedObjectContainer.class);
		// Create TrivialSharedObject instance and add to container
		createTrivialSharedObjectForContainer(socontainer);

		// Then connect
		client.doConnect(userName + "@" + hostName, password);

		this.targetIMUser = targetIMUser;
		// Send initial message to target user
		client.sendChatMessage(targetIMUser, "Hi, I'm an IM robot");

		running = true;
		int count = 0;
		// Loop ten times and send ten 'hello there' so messages to targetIMUser
		while (running && count++ < 10) {
			sendSOMessage(count + " hello there");
			wait(10000);
		}
	}

	protected void sendSOMessage(String msg) {
		if (sharedObject != null) {
			sharedObject.sendMessageTo(client.createID(targetIMUser), msg);
		}
	}

	protected void createTrivialSharedObjectForContainer(
			ISharedObjectContainer soContainer) throws ECFException {
		if (soContainer != null) {
			// Create a new GUID for new TrivialSharedObject instance
			ID newID = IDFactory.getDefault().createStringID(
					TrivialSharedObject.class.getName());
			// Create TrivialSharedObject
			sharedObject = new TrivialSharedObject();
			// Add shared object to container
			soContainer.getSharedObjectManager().addSharedObject(newID,
					sharedObject, null);
		}
	}

	public synchronized void handleMessage(IChatMessage chatMessage) {
		// direct message
		// client.sendMessage(from,"gotta run");
		// running = false;
		notifyAll();
	}

}