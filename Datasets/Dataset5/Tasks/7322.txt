container.connect(serverID, null);

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

import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.comm.ConnectionFactory;
import org.eclipse.ecf.core.comm.ConnectionInstantiationException;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;

public class TCPClientSOContainer extends ClientSOContainer {
    int keepAlive = 0;
    public static final String DEFAULT_COMM_NAME = org.eclipse.ecf.provider.comm.tcp.Client.class
            .getName();

    public TCPClientSOContainer(ISharedObjectContainerConfig config) {
        super(config);
    }

    public TCPClientSOContainer(ISharedObjectContainerConfig config, int ka) {
        super(config);
        keepAlive = ka;
    }

    protected ISynchAsynchConnection makeConnection(ID remoteSpace,
            Object data) throws ConnectionInstantiationException {
        debug("getClientConnection:" + remoteSpace + ":" + data);
        Object[] args = { new Integer(keepAlive) };
        ISynchAsynchConnection conn = null;
        conn = ConnectionFactory.makeSynchAsynchConnection(receiver,
                DEFAULT_COMM_NAME, args);
        return conn;
    }

    public static final void main(String[] args) throws Exception {
        ISharedObjectContainerConfig config = new SOContainerConfig(IDFactory
                .getDefault().makeGUID());
        TCPClientSOContainer container = new TCPClientSOContainer(config);
        // now join group
        ID serverID = IDFactory.getDefault().makeStringID(TCPServerSOContainer
                .getDefaultServerURL());
        container.joinGroup(serverID, null);
        Thread.sleep(200000);
    }

}
 No newline at end of file