package org.eclipse.ecf.internal.example.collab;

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
package org.eclipse.ecf.example.collab;

import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.provider.app.Connector;
import org.eclipse.ecf.provider.app.NamedGroup;
import org.eclipse.ecf.provider.app.ServerConfigParser;
import org.eclipse.ecf.provider.generic.SOContainerConfig;
import org.eclipse.ecf.provider.generic.TCPServerSOContainer;
import org.eclipse.ecf.provider.generic.TCPServerSOContainerGroup;

public class ServerStartup {
	static TCPServerSOContainerGroup serverGroups[] = null;
	static final String SERVER_FILE_NAME = "ServerStartup.xml";
	static List servers = new ArrayList();
	public ServerStartup() throws Exception {
		InputStream ins = this.getClass().getResourceAsStream(SERVER_FILE_NAME);
		if (ins != null) {
			createServers(ins);
		}
	}
	protected boolean isActive() {
		return (servers.size() > 0);
	}
	public void dispose() {
		destroyServers();
	}
	protected synchronized void destroyServers() {
		for (Iterator i = servers.iterator(); i.hasNext();) {
			TCPServerSOContainer s = (TCPServerSOContainer) i.next();
			DiscoveryStartup.unregisterServer(s);
			if (s != null) {
				try {
					s.dispose();
				} catch (Exception e) {
					ClientPlugin.log("Exception destroying server "
							+ s.getConfig().getID());
				}
			}
		}
		servers.clear();
		if (serverGroups != null) {
			for (int i = 0; i < serverGroups.length; i++) {
				serverGroups[i].takeOffTheAir();
			}
			serverGroups = null;
		}
	}
	protected synchronized void createServers(InputStream ins) throws Exception {
		ServerConfigParser scp = new ServerConfigParser();
		List connectors = scp.load(ins);
		if (connectors != null) {
			serverGroups = new TCPServerSOContainerGroup[connectors.size()];
			int j = 0;
			for (Iterator i = connectors.iterator(); i.hasNext();) {
				Connector connect = (Connector) i.next();
				serverGroups[j] = createServerGroup(connect.getHostname(),
						connect.getPort());
				List groups = connect.getGroups();
				for (Iterator g = groups.iterator(); g.hasNext();) {
					NamedGroup group = (NamedGroup) g.next();
					TCPServerSOContainer cont = createServerContainer(group
							.getIDForGroup(), serverGroups[j], group.getName(),
							connect.getTimeout());
					servers.add(cont);
					ClientPlugin.log("ECF group server created: "
							+ cont.getConfig().getID().getName());
				}
				serverGroups[j].putOnTheAir();
				j++;
			}
		}
	}
	protected void registerServers() {
		for (Iterator i = servers.iterator(); i.hasNext();) {
			ISharedObjectContainer cont = (ISharedObjectContainer) i.next();
			try {
				registerServer(cont);
			} catch (Exception e) {
				ClientPlugin.log("Exception registering server "
						+ cont.getID().getName() + " for discovery", e);
			}
		}
	}
	protected void registerServer(ISharedObjectContainer cont)
			throws URISyntaxException {
		DiscoveryStartup.registerService(new URI(cont.getID().getName()));
	}
	protected TCPServerSOContainerGroup createServerGroup(String name, int port) {
		TCPServerSOContainerGroup group = new TCPServerSOContainerGroup(name,
				port);
		return group;
	}
	protected TCPServerSOContainer createServerContainer(String id,
			TCPServerSOContainerGroup group, String path, int keepAlive)
			throws IDCreateException {
		ID newServerID = IDFactory.getDefault().createStringID(id);
		SOContainerConfig config = new SOContainerConfig(newServerID);
		return new TCPServerSOContainer(config, group, path, keepAlive);
	}
}