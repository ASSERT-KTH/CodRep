ID serverID = IDFactory.getDefault().createStringID("ecftcp://localhost:3282/server"); //$NON-NLS-1$

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

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerConfig;
import org.eclipse.ecf.provider.comm.ConnectionCreateException;
import org.eclipse.ecf.provider.comm.ISynchAsynchConnection;
import org.eclipse.ecf.provider.comm.tcp.Client;

public class TCPClientSOContainer extends ClientSOContainer {
	int keepAlive = 0;

	public static final int DEFAULT_TCP_CONNECT_TIMEOUT = 30000;

	public static final String DEFAULT_COMM_NAME = org.eclipse.ecf.provider.comm.tcp.Client.class.getName();

	public TCPClientSOContainer(ISharedObjectContainerConfig config) {
		super(config);
	}

	public TCPClientSOContainer(ISharedObjectContainerConfig config, int ka) {
		super(config);
		keepAlive = ka;
	}

	protected int getConnectTimeout() {
		return DEFAULT_TCP_CONNECT_TIMEOUT;
	}

	/**
	 * @param remoteSpace
	 * @param data
	 * @return ISynchAsynchConnection a non-<code>null</code> instance.
	 * @throws ConnectionCreateException not thrown by this implementation.
	 */
	protected ISynchAsynchConnection createConnection(ID remoteSpace, Object data) throws ConnectionCreateException {
		debug("createClientConnection:" + remoteSpace + ":" + data); //$NON-NLS-1$ //$NON-NLS-2$
		ISynchAsynchConnection conn = new Client(receiver, keepAlive);
		return conn;
	}

	public static final void main(String[] args) throws Exception {
		ISharedObjectContainerConfig config = new SOContainerConfig(IDFactory.getDefault().createGUID());
		TCPClientSOContainer container = new TCPClientSOContainer(config);
		// now join group
		ID serverID = IDFactory.getDefault().createStringID(TCPServerSOContainer.getDefaultServerURL());
		container.connect(serverID, null);
		Thread.sleep(200000);
	}

}
 No newline at end of file