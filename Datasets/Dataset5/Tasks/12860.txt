targetString = new URI(svcInfo.getServiceID().getName()).toString();

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

import java.io.IOException;
import java.net.InetAddress;
import java.net.URI;
import java.util.Properties;
import org.eclipse.core.resources.IResource;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.ServiceID;
import org.eclipse.ecf.example.collab.actions.URIClientConnectAction;

public class DiscoveryStartup {
	public static final String DISCOVERY_CONTAINER = "ecf.discovery.jmdns";
	public static final String PROP_PROTOCOL_NAME = "protocol";
	public static final String PROP_CONTAINER_TYPE_NAME = "containertype";
	public static final String PROP_CONTAINER_TYPE_VALUE = CollabClient.GENERIC_CONTAINER_CLIENT_NAME;
	public static final String PROP_PW_REQ_NAME = "pwrequired";
	public static final String PROP_PW_REQ_VALUE = "false";
	public static final String PROP_DEF_USER_NAME = "defaultuser";
	public static final String PROP_DEF_USER_VALUE = "guest";
	public static final String PROP_PATH_NAME = "path";
	public static final int SVC_DEF_WEIGHT = 0;
	public static final int SVC_DEF_PRIORITY = 0;
	
	static IDiscoveryContainerAdapter discovery = null;
	static IContainer container = null;
	
	public DiscoveryStartup() throws Exception {
		setupDiscovery();
	}
	protected IDiscoveryContainerAdapter getDiscoveryContainer() {
		return discovery;
	}
	protected IContainer getContainer() {
		return container;
	}
	public void dispose() {
		if (container != null) {
			container.dispose();
			container = null;
		}
		discovery = null;
	}
	protected boolean isActive() {
		return discovery != null;
	}
	protected void setupDiscovery() throws Exception {
		try {
			container = ContainerFactory.getDefault().createContainer(
					DISCOVERY_CONTAINER);
			discovery = (IDiscoveryContainerAdapter) container
					.getAdapter(IDiscoveryContainerAdapter.class);
			if (discovery != null) {
				container.connect(null, null);
			} else {
				dispose();
				ClientPlugin.log("No discovery container available");
			}
		} catch (ContainerCreateException e1) {
			container = null;
			discovery = null;
			ClientPlugin.log("No discovery container available", e1);
			return;
		} catch (Exception e) {
			dispose();
			throw e;
		}
	}
	protected void connectToServiceFromInfo(IServiceInfo svcInfo) {
		IServiceProperties props = svcInfo.getServiceProperties();
		String type = (String) props.getPropertyString(PROP_CONTAINER_TYPE_NAME);
		if (type == null || type.equals("")) {
			type = CollabClient.GENERIC_CONTAINER_CLIENT_NAME;
		}
		String username = System.getProperty("user.name");
		String targetString = null;
		IResource workspace = null;
		try {
			targetString = svcInfo.getServiceURI().toString();
			workspace = CollabClient.getWorkspace();
		} catch (Exception e) {
			ClientPlugin.log("Exception connecting to service with info "
					+ svcInfo, e);
			return;
		}
		URIClientConnectAction action = new URIClientConnectAction(type,
				targetString, username, null, workspace,false);
		// do it
		action.run(null);
	}
	public static void registerService(URI uri) {
		if (discovery != null) {
			try {
				String path = uri.getPath();
				Properties props = new Properties();
				String protocol = uri.getScheme();
				props.setProperty(PROP_CONTAINER_TYPE_NAME,
						PROP_CONTAINER_TYPE_VALUE);
				props.setProperty(PROP_PROTOCOL_NAME, protocol);
				props.setProperty(PROP_PW_REQ_NAME, PROP_PW_REQ_VALUE);
				props.setProperty(PROP_DEF_USER_NAME, PROP_DEF_USER_VALUE);
				props.setProperty(PROP_PATH_NAME, path);
				InetAddress host = InetAddress.getByName(uri.getHost());
				int port = uri.getPort();
				String svcName = System.getProperty("user.name") + "."
						+ protocol;
				ServiceInfo svcInfo = new ServiceInfo(host, new ServiceID(
						ClientPlugin.TCPSERVER_DISCOVERY_TYPE, svcName), port,
						SVC_DEF_PRIORITY, SVC_DEF_WEIGHT, new ServiceProperties(props));
				discovery.registerService(svcInfo);
			} catch (IOException e) {
				ClientPlugin.log("Exception registering service " + uri);
			}
		} else {
			ClientPlugin.log("Cannot register service " + uri
					+ " because no discovery service is available");
		}
	}
	public static void unregisterServer(ISharedObjectContainer container) {
	}
	public static void registerServiceTypes() {
		if (discovery != null) {
			for (int i = 0; i < ClientPlugin.serviceTypes.length; i++) {
				discovery.registerServiceType(ClientPlugin.serviceTypes[i]);
			}
		}
	}
}