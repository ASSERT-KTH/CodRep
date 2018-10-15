debug.msg("Taking " + getName() + " off the air.");

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

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InvalidObjectException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.net.Socket;
import java.net.URI;
import org.eclipse.ecf.provider.Trace;
import org.eclipse.ecf.core.comm.ConnectionRequestHandler;
import org.eclipse.ecf.provider.comm.tcp.Client;
import org.eclipse.ecf.provider.comm.tcp.ConnectRequestMessage;
import org.eclipse.ecf.provider.comm.tcp.ConnectResultMessage;
import org.eclipse.ecf.provider.comm.tcp.ExObjectInputStream;
import org.eclipse.ecf.provider.comm.tcp.ExObjectOutputStream;
import org.eclipse.ecf.provider.comm.tcp.ISocketAcceptHandler;
import org.eclipse.ecf.provider.comm.tcp.Server;

public class TCPServerSOContainerGroup extends SOContainerGroup implements
        ISocketAcceptHandler {
    public static final String INVALID_CONNECT = "Invalid connect request.  ";
    public static final Trace debug = Trace.create("connection");
    public static final String DEFAULT_GROUP_NAME = TCPServerSOContainerGroup.class
            .getName();
    protected int port;
    Server listener;
    boolean isOnTheAir = false;
    ThreadGroup threadGroup;

    public TCPServerSOContainerGroup(String name, ThreadGroup group, int port) {
        super(name);
        threadGroup = group;
        this.port = port;
    }

    public TCPServerSOContainerGroup(String name, int port) {
        this(name, null, port);
    }

    public TCPServerSOContainerGroup(int port) {
        this(DEFAULT_GROUP_NAME, null, port);
    }

    protected void debug(String msg) {
        if (Trace.ON && debug != null) {
            debug.msg(msg);
        }
    }

    protected void dumpStack(String msg, Throwable e) {
        if (Trace.ON && debug != null) {
            debug.dumpStack(e, msg);
        }
    }

    public synchronized void putOnTheAir() throws IOException {
        debug("group at port " + port + " on the air");
        listener = new Server(threadGroup, port, this);
        port = listener.getLocalPort();
        isOnTheAir = true;
    }

    public synchronized boolean isOnTheAir() {
        return isOnTheAir;
    }

    public void handleAccept(Socket aSocket) throws Exception {
        ObjectOutputStream oStream = new ExObjectOutputStream(
                new BufferedOutputStream(aSocket.getOutputStream()));
        oStream.flush();
        ObjectInputStream iStream = new ExObjectInputStream(aSocket
                .getInputStream());
        ConnectRequestMessage req = (ConnectRequestMessage) iStream
                .readObject();
        if (Trace.ON && debug != null) {
            debug.msg("serverrecv:" + req);
        }
        if (req == null)
            throw new InvalidObjectException(INVALID_CONNECT
                    + "ConnectRequestMessage is null");
        URI uri = req.getTarget();
        if (uri == null)
            throw new InvalidObjectException(INVALID_CONNECT
                    + "Target URI is null");
        String path = uri.getPath();
        if (path == null)
            throw new InvalidObjectException(INVALID_CONNECT
                    + "Target path is null");
        TCPServerSOContainer srs = (TCPServerSOContainer) get(path);
        if (srs == null)
            throw new InvalidObjectException("Container for target " + path
                    + " not found!");
        debug("found container:" + srs.getID().getName() + " for target " + uri);
        // Create our local messaging interface
        Client newClient = new Client(aSocket, iStream, oStream, srs
                .getReceiver(), srs.keepAlive);
        // No other threads can access messaging interface until space has
        // accepted/rejected
        // connect request
        synchronized (newClient) {
            // Call checkConnect
            Serializable resp = (Serializable) ((ConnectionRequestHandler) srs)
                    .checkConnect(aSocket, path, req.getData(), newClient);
            // Create connect response wrapper and send it back
            oStream.writeObject(new ConnectResultMessage(resp));
            oStream.flush();
        }
    }

    public synchronized void takeOffTheAir() {
        if (listener != null) {
            if (Trace.ON && debug != null) {
                debug.msg("Taking " + getName() + " on the air.");
            }
            try {
                listener.close();
            } catch (IOException e) {
                if (Trace.ON && debug != null) {
                    debug.dumpStack(e, "Exception in closeListener");
                }
            }
            listener = null;
        }
        isOnTheAir = false;
    }

    public int getPort() {
        return port;
    }

    public String toString() {
        return super.toString() + ";port:" + port;
    }
}
 No newline at end of file