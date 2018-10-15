public static final String SERVICE_TYPE = "_" + DEFAULT_PROTOCOL + "._tcp.local."; //$NON-NLS-1$ //$NON-NLS-2$

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

package org.eclipse.ecf.provider.generic;

import java.io.IOException;
import java.io.Serializable;
import java.net.Socket;
import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerConfig;
import org.eclipse.ecf.provider.comm.IConnectRequestHandler;
import org.eclipse.ecf.provider.comm.ISynchAsynchConnection;

public class TCPServerSOContainer extends ServerSOContainer implements
		IConnectRequestHandler {
	public static final String DEFAULT_PROTOCOL = "ecftcp"; //$NON-NLS-1$

	public static final int DEFAULT_PORT = 3282;

	public static final int DEFAULT_KEEPALIVE = 30000;

	public static final String DEFAULT_NAME = "/server"; //$NON-NLS-1$

	public static final String DEFAULT_HOST = "localhost"; //$NON-NLS-1$

	public static final String SERVICE_TYPE = "_" + DEFAULT_PROTOCOL + "._tcp.local.";
	
	// Keep alive value
	protected int keepAlive;

	protected TCPServerSOContainerGroup group;

	protected boolean isSingle = false;

	protected int getKeepAlive() {
		return keepAlive;
	}

	public static String getServerURL(String host, String name) {
		return DEFAULT_PROTOCOL + "://" + host + ":" + DEFAULT_PORT + name; //$NON-NLS-1$ //$NON-NLS-2$
	}

	public static String getDefaultServerURL() {
		return getServerURL("localhost", DEFAULT_NAME); //$NON-NLS-1$
	}

	public TCPServerSOContainer(ISharedObjectContainerConfig config,
			TCPServerSOContainerGroup grp, int keepAlive) throws IOException,
			URISyntaxException {
		super(config);
		this.keepAlive = keepAlive;
		// Make sure URI syntax is followed.
		URI actualURI = new URI(getID().getName());
		int urlPort = actualURI.getPort();
		if (group == null) {
			isSingle = true;
			this.group = new TCPServerSOContainerGroup(urlPort);
			this.group.putOnTheAir();
		} else
			this.group = grp;
		String path = actualURI.getPath();
		group.add(path, this);
	}

	public TCPServerSOContainer(ISharedObjectContainerConfig config,
			TCPServerSOContainerGroup listener, String path, int keepAlive) {
		super(config);
		initialize(listener, path, keepAlive);
	}

	protected void initialize(TCPServerSOContainerGroup listener, String path,
			int ka) {
		this.keepAlive = ka;
		this.group = listener;
		this.group.add(path, this);
	}

	public void dispose() {
		URI aURI = null;
		try {
			aURI = new URI(getID().getName());
		} catch (Exception e) {
			// Should never happen
		}
		if (aURI != null)
			group.remove(aURI.getPath());
		if (isSingle) {
			group.takeOffTheAir();
		}
		group = null;
		super.dispose();
	}

	public TCPServerSOContainer(ISharedObjectContainerConfig config)
			throws IOException, URISyntaxException {
		this(config, null, DEFAULT_KEEPALIVE);
	}

	public TCPServerSOContainer(ISharedObjectContainerConfig config,
			int keepAlive) throws IOException, URISyntaxException {
		this(config, null, keepAlive);
	}

	public Serializable handleConnectRequest(Socket socket, String target,
			Serializable data, ISynchAsynchConnection conn) {
		return acceptNewClient(socket, target, data, conn);
	}

	protected Serializable getConnectDataFromInput(Serializable input)
			throws Exception {
		return input;
	}

}
 No newline at end of file