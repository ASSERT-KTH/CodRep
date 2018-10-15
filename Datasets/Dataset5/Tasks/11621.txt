public static final int DEFAULT_KEEPALIVE = 30000;

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
import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.comm.ConnectionRequestHandler;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;

public class TCPServerSOContainer extends ServerSOContainer implements
        ConnectionRequestHandler {
    public static final String DEFAULT_PROTOCOL = "ecftcp";
    public static final int DEFAULT_PORT = 3282;
    public static final int DEFAULT_KEEPALIVE = 10000;
    public static final String DEFAULT_NAME = "/server";
    public static final String DEFAULT_HOST = "localhost";
    
    // Keep alive value
    protected int keepAlive;
    protected TCPServerSOContainerGroup group;
    protected boolean isSingle = false;
    
    protected int getKeepAlive() {
        return keepAlive;
    }

    public static String getServerURL(String host, String name) {
        return DEFAULT_PROTOCOL + "://" + host + ":" + DEFAULT_PORT + name;
    }

    public static String getDefaultServerURL() {
        return getServerURL("localhost", DEFAULT_NAME);
    }

    public TCPServerSOContainer(ISharedObjectContainerConfig config,
            TCPServerSOContainerGroup grp, int keepAlive) throws IOException,
            URISyntaxException {
        super(config);
        this.keepAlive = keepAlive;
        // Make sure URI syntax is followed.
        URI aURI = new URI(config.getID().getName());
        int urlPort = aURI.getPort();
        if (group == null) {
            isSingle = true;
            this.group = new TCPServerSOContainerGroup(urlPort);
            this.group.putOnTheAir();
        } else
            this.group = grp;
        String path = aURI.getPath();
        group.add(path, this);
    }

    public TCPServerSOContainer(ISharedObjectContainerConfig config,
            TCPServerSOContainerGroup listener, String path, int keepAlive) {
        super(config);
        initialize(listener, path, keepAlive);
    }

    protected void initialize(TCPServerSOContainerGroup listener, String path,
            int keepAlive) {
        this.keepAlive = keepAlive;
        this.group = listener;
        this.group.add(path, this);
    }

    public void dispose(long timeout) {
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
        super.dispose(timeout);
    }

    public TCPServerSOContainer(ISharedObjectContainerConfig config)
            throws IOException, URISyntaxException {
        this(config, null, DEFAULT_KEEPALIVE);
    }
    public TCPServerSOContainer(ISharedObjectContainerConfig config, int keepAlive) throws IOException, URISyntaxException {
        this(config,null,keepAlive);
    }
    public Serializable checkConnect(Socket socket, String target,
            Serializable data, ISynchAsynchConnection conn) {
        return acceptNewClient(socket, target, data, conn);
    }

    protected Serializable getConnectDataFromInput(Serializable input)
            throws Exception {
        return input;
    }

    public static void main(String[] args) throws Exception {
        ID server = IDFactory.makeStringID(getDefaultServerURL());
        TCPServerSOContainer cont = new TCPServerSOContainer(
                new SOContainerConfig(server));
        Thread.sleep(3000000);
    }
}
 No newline at end of file