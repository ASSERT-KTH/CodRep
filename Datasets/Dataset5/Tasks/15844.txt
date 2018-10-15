return ContainerFactory.getDefault().createContainer(getServerContainerName(), new Object[] {serverID});

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

package org.eclipse.ecf.tests;

import java.net.Socket;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.internal.tests.Activator;
import org.eclipse.osgi.util.NLS;

public abstract class ContainerAbstractTestCase extends ECFAbstractTestCase {

	protected String genericServerName = "ecf.generic.server";

	protected String genericClientName = "ecf.generic.client";

	protected int genericServerPort = 30000;

	protected String genericServerIdentity = "ecftcp://localhost:{0}/server";

	protected IContainer server;

	protected IContainer[] clients;

	protected int clientCount = 1;

	protected ID serverID;

	protected String[] usernames = null;

	protected String[] passwords = null;

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		findEmptySocket();
		loadUsernamesAndPasswords();
	}

	/**
	 * 
	 */
	private void findEmptySocket() {
		final boolean done = false;
		while (!done) {
			try {
				final Socket s = new Socket("localhost", genericServerPort);
				// If this connects, the port is in use...so move onto next won
				genericServerPort++;
				try {
					s.close();
				} catch (final Exception e) {
				};
			} catch (final Exception e) {
				// found it...we're done
				return;
			}
		}
	}

	protected String getUsername(int client) {
		if (usernames == null || usernames.length <= client || usernames[client] == null)
			throw new NullPointerException("System property -username" + client + " is not set and must be set to run this test");
		return usernames[client];
	}

	protected String getPassword(int client) {
		if (passwords == null || passwords.length <= client || passwords[client] == null)
			throw new NullPointerException("System property -password" + client + " is not set and must be set to run this test");
		return passwords[client];
	}

	protected IConnectContext createUsernamePasswordConnectContext(String username, String password) {
		return ConnectContextFactory.createUsernamePasswordConnectContext(username, password);
	}

	protected IConnectContext createPasswordConnectContext(String password) {
		return ConnectContextFactory.createPasswordConnectContext(password);
	}

	protected void setClientCount(int count) {
		this.clientCount = count;
	}

	protected IContainer getServer() {
		return server;
	}

	protected IContainer[] getClients() {
		return clients;
	}

	protected IContainer getClient(int index) {
		if (clients == null || clients.length <= index)
			return null;
		return clients[index];
	}

	protected String getServerContainerName() {
		return genericServerName;
	}

	protected String getClientContainerName() {
		return genericClientName;
	}

	protected String getServerIdentity() {
		return NLS.bind(genericServerIdentity, new Integer(genericServerPort));
	}

	protected ID getServerConnectID(int client) {
		return serverID;
	}

	protected ID getServerCreateID() {
		return serverID;
	}

	protected int getClientCount() {
		return clientCount;
	}

	protected ID createServerID() throws Exception {
		return IDFactory.getDefault().createStringID(getServerIdentity());
	}

	protected IContainer createServer() throws Exception {
		return ContainerFactory.getDefault().createContainer(getServerContainerName(), new Object[] {getServerCreateID()});
	}

	protected IContainer[] createClients() throws Exception {
		final IContainer[] result = new IContainer[getClientCount()];
		for (int i = 0; i < result.length; i++) {
			result[i] = createClient(i);
		}
		return result;
	}
	
	protected void loadUsernamesAndPasswords() {
		// Default behavior is to look for system properties
		int i = 0;
		boolean done = false;
		List us = new ArrayList();
		List ps = new ArrayList();
		while (!done) {
			String uname = System.getProperty("username"+i);
			String pword = System.getProperty("password"+i);
			if (uname == null && i==0) {
				uname = System.getProperty("username");
				pword = System.getProperty("password");
			}
			if (uname == null) {
				done = true;
			} else {
				us.add(uname);
				ps.add(pword);
			}
			i++;
		}
		if (us.size() > 0) {
			usernames = (String []) us.toArray(new String [] {});
			passwords = (String []) ps.toArray(new String [] {});
		}
	}

	protected IContainer createClient(int index) throws Exception {
		return ContainerFactory.getDefault().createContainer(getClientContainerName());
	}

	protected void createServerAndClients() throws Exception {
		serverID = createServerID();
		server = createServer();
		clients = createClients();
	}

	protected void removeFromContainerManager(IContainer container) {
		IContainerManager manager = Activator.getDefault().getContainerManager();
		if (manager != null) manager.removeContainer(container);
	}
	
	protected void cleanUpClients() {
		if (clients != null) {
			for (int i = 0; i < clients.length; i++) {
				clients[i].disconnect();
				clients[i].dispose();
				removeFromContainerManager(clients[i]);
				clients[i] = null;
			}
			clients = null;
		}
	}

	protected void cleanUpServerAndClients() {
		cleanUpClients();
		serverID = null;
		server.disconnect();
		server.dispose();
		removeFromContainerManager(server);
		server = null;
	}

	protected void connectClients() throws Exception {
		final IContainer[] clients = getClients();
		for (int i = 0; i < clients.length; i++)
			connectClient(clients[i], getServerConnectID(i), getConnectContext(i));
	}

	protected IConnectContext getConnectContext(int client) {
		if (usernames == null) return null;
		return createUsernamePasswordConnectContext(getUsername(client), getPassword(client));
	}

	protected void connectClient(IContainer containerToConnect, ID connectID, IConnectContext context) throws ContainerConnectException {
		containerToConnect.connect(connectID, context);
	}

	protected void connectClient(int client) throws ContainerConnectException {
		connectClient(getClient(client), getServerConnectID(client), getConnectContext(client));
	}

	protected void disconnectClients() throws Exception {
		final IContainer[] clients = getClients();
		for (int i = 0; i < clients.length; i++) {
			clients[i].disconnect();
		}
	}

	protected void assertHasEvent(Collection collection, Class eventType) {
		assertHasEventCount(collection, eventType, 1);
	}

	protected void assertHasEventCount(Collection collection, Class eventType, int eventCount) {
		int count = 0;
		for (final Iterator i = collection.iterator(); i.hasNext();) {
			final Object o = i.next();
			if (eventType.isInstance(o))
				count++;
		}
		assertTrue(count == eventCount);
	}

	protected void assertHasMoreThanEventCount(Collection collection, Class eventType, int eventCount) {
		int count = 0;
		for (final Iterator i = collection.iterator(); i.hasNext();) {
			final Object o = i.next();
			if (eventType.isInstance(o))
				count++;
		}
		assertTrue(count > eventCount);
	}

}