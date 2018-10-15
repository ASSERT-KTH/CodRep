discovery = Boolean.valueOf(discoveryString).booleanValue();

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

package org.eclipse.ecf.server.generic;

import java.io.IOException;
import java.io.InputStream;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtensionPoint;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.ecf.discovery.service.IDiscoveryService;
import org.eclipse.ecf.internal.server.generic.Activator;
import org.eclipse.ecf.internal.server.generic.Messages;
import org.eclipse.ecf.provider.generic.SOContainerConfig;
import org.eclipse.ecf.provider.generic.TCPServerSOContainer;
import org.eclipse.ecf.provider.generic.TCPServerSOContainerGroup;
import org.eclipse.ecf.server.generic.app.Connector;
import org.eclipse.ecf.server.generic.app.NamedGroup;
import org.eclipse.ecf.server.generic.app.ServerConfigParser;
import org.eclipse.osgi.util.NLS;

public class ServerManager {

	/**
	 * 
	 */
	private static final String ECF_NAMESPACE_JMDNS = "ecf.namespace.jmdns";

	private static final String GROUP_PROPERTY_NAME = "group"; //$NON-NLS-1$

	private static final String PWREQUIRED_PROPERTY_NAME = "pwrequired"; //$NON-NLS-1$

	private static final String PROTOCOL_PROPERTY_NAME = "protocol"; //$NON-NLS-1$

	private static final String SERVICE_TYPE = Messages.ServerManager_SERVICE_TYPE;

	static TCPServerSOContainerGroup serverGroups[] = null;

	static Map servers = new HashMap();

	public static final String EXTENSION_POINT_NAME = "configuration"; //$NON-NLS-1$

	public static final String EXTENSION_POINT = Activator.PLUGIN_ID + "." //$NON-NLS-1$
			+ EXTENSION_POINT_NAME;

	public static final String CONFIGURATION_ELEMENT = "configuration"; //$NON-NLS-1$
	public static final String CONNECTOR_ELEMENT = "connector"; //$NON-NLS-1$
	public static final String GROUP_ELEMENT = GROUP_PROPERTY_NAME;

	public static final String HOSTNAME_ATTR = "hostname"; //$NON-NLS-1$
	public static final String PORT_ATTR = "port"; //$NON-NLS-1$
	public static final String KEEPALIVE_ATTR = "keepAlive"; //$NON-NLS-1$
	public static final String NAME_ATTR = "name"; //$NON-NLS-1$

	public static final String DISCOVERY_ATTR = "discovery"; //$NON-NLS-1$

	public ServerManager() {
		final IExtensionRegistry reg = Activator.getDefault().getExtensionRegistry();
		try {
			if (reg != null) {
				createServersFromExtensionRegistry(reg);
			} else {
				createServersFromConfigurationFile(Activator.getDefault().getBundle().getEntry(Messages.Activator_SERVER_XML).openStream());
			}
		} catch (final Exception e) {
			Activator.log(Messages.ServerStarter_EXCEPTION_CREATING_SERVER, e);
		}
	}

	public synchronized ISharedObjectContainer getServer(ID id) {
		if (id == null)
			return null;
		return (ISharedObjectContainer) servers.get(id);
	}

	private void createServersFromExtensionRegistry(IExtensionRegistry registry) throws Exception {
		final IExtensionPoint extensionPoint = registry.getExtensionPoint(EXTENSION_POINT);
		if (extensionPoint == null)
			return;
		final IConfigurationElement[] elements = extensionPoint.getConfigurationElements();
		final List connectors = new ArrayList();
		for (int i = 0; i < elements.length; i++) {
			final IConfigurationElement element = elements[i];
			final String portString = element.getAttribute(PORT_ATTR);
			int port = TCPServerSOContainer.DEFAULT_PORT;
			if (portString != null)
				port = Integer.parseInt(portString);
			int keepAlive = TCPServerSOContainer.DEFAULT_KEEPALIVE;
			final String keepAliveString = element.getAttribute(KEEPALIVE_ATTR);
			if (keepAliveString != null)
				keepAlive = Integer.parseInt(keepAliveString);
			boolean discovery = false;
			final String discoveryString = element.getAttribute(DISCOVERY_ATTR);
			if (discoveryString != null)
				discovery = Boolean.parseBoolean(discoveryString);
			final Connector connector = new Connector(null, element.getAttribute(HOSTNAME_ATTR), port, keepAlive, discovery);
			final IConfigurationElement[] groupElements = element.getChildren(GROUP_ELEMENT);
			for (int j = 0; j < groupElements.length; j++) {
				final String groupName = groupElements[i].getAttribute(NAME_ATTR);
				if (groupName != null)
					connector.addGroup(new NamedGroup(groupName));
			}
			connectors.add(connector);
		}
		createServersFromConnectorList(connectors);
	}

	protected boolean isActive() {
		return (servers.size() > 0);
	}

	public synchronized void closeServers() {
		for (final Iterator i = servers.keySet().iterator(); i.hasNext();) {
			final ID serverID = (ID) i.next();
			final TCPServerSOContainer server = (TCPServerSOContainer) servers.get(serverID);
			if (server != null) {
				try {
					server.dispose();
				} catch (final Exception e) {
					Activator.log(Messages.ServerStarter_EXCEPTION_DISPOSING_SERVER, e);
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

	private synchronized void createServersFromConnectorList(List connectors) throws IDCreateException, IOException {
		serverGroups = new TCPServerSOContainerGroup[connectors.size()];
		int j = 0;
		for (final Iterator i = connectors.iterator(); i.hasNext();) {
			final Connector connect = (Connector) i.next();
			serverGroups[j] = createServerGroup(connect);
			final List groups = connect.getGroups();
			for (final Iterator g = groups.iterator(); g.hasNext();) {
				final NamedGroup group = (NamedGroup) g.next();
				final TCPServerSOContainer cont = createServerContainer(group.getIDForGroup(), serverGroups[j], group.getName(), connect.getTimeout());
				if (connect.shouldRegisterForDiscovery())
					registerServerForDiscovery(group, false);
				servers.put(cont.getID(), cont);
				final String msg = NLS.bind(Messages.ServerStarter_STARTING_SERVER, cont.getID().getName());
				System.out.println(msg);
				Activator.log(msg);
			}
			serverGroups[j].putOnTheAir();
			j++;
		}
	}

	private void createServersFromConfigurationFile(InputStream ins) throws Exception {
		final ServerConfigParser scp = new ServerConfigParser();
		final List connectors = scp.load(ins);
		if (connectors != null)
			createServersFromConnectorList(connectors);
	}

	private TCPServerSOContainerGroup createServerGroup(Connector connector) {
		final TCPServerSOContainerGroup group = new TCPServerSOContainerGroup(connector.getHostname(), connector.getPort());
		return group;
	}

	private TCPServerSOContainer createServerContainer(String id, TCPServerSOContainerGroup group, String path, int keepAlive) throws IDCreateException {
		final ID newServerID = IDFactory.getDefault().createStringID(id);
		return new TCPServerSOContainer(new SOContainerConfig(newServerID), group, path, keepAlive);
	}

	private void registerServerForDiscovery(NamedGroup group, boolean pwrequired) {
		final IDiscoveryService discovery = Activator.getDefault().getDiscovery();
		if (discovery != null) {
			try {
				final IServiceID sID = ServiceIDFactory.getDefault().createServiceID(discovery.getServicesNamespace(), SERVICE_TYPE);
				discovery.registerServiceType(sID.getServiceTypeID());
				final String rawGroupName = group.getRawName();
				final Connector connector = group.getConnector();
				final Properties props = new Properties();
				props.put(PROTOCOL_PROPERTY_NAME, TCPServerSOContainer.DEFAULT_PROTOCOL);
				props.put(PWREQUIRED_PROPERTY_NAME, new Boolean(pwrequired).toString());
				props.put(GROUP_PROPERTY_NAME, rawGroupName);
				final Namespace ns = IDFactory.getDefault().getNamespaceByName(ECF_NAMESPACE_JMDNS);
				final IServiceID serviceID = (IServiceID) IDFactory.getDefault().createID(ns, new Object[] {SERVICE_TYPE, rawGroupName});
				final InetAddress host = InetAddress.getByName(connector.getHostname());
				final ServiceInfo svcInfo = new ServiceInfo(host, serviceID, connector.getPort(), 0, 0, new ServiceProperties(props));
				discovery.registerService(svcInfo);
			} catch (final Exception e) {
				Activator.log(Messages.ServerManager_EXCEPTION_DISCOVERY_REGISTRATION, e);
			}
		}
	}
}