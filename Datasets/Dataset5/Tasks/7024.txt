}, "ServerApplication(" + getLocalPort() + ")");

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

package org.eclipse.ecf.provider.comm.tcp;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import org.eclipse.ecf.provider.Trace;

public class Server extends ServerSocket {
    public static Trace debug = Trace.create("connection");
    ISocketAcceptHandler acceptHandler;
    Thread listenerThread;
    ThreadGroup threadGroup;

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

    public Server(ThreadGroup group, int port, ISocketAcceptHandler handler)
            throws IOException {
        super(port);
        if (handler == null)
            throw new InstantiationError("Listener cannot be null");
        acceptHandler = handler;
        threadGroup = group;
        listenerThread = setupListener();
        listenerThread.start();
    }

    public Server(int port, ISocketAcceptHandler handler) throws IOException {
        this(null, port, handler);
    }

    protected Thread setupListener() {
        return new Thread(threadGroup, new Runnable() {
            public void run() {
                while (true) {
                    try {
                        handleAccept(accept());
                    } catch (Exception e) {
                        if (Trace.ON && debug != null) {
                            debug.dumpStack(e, "Exception in accept");
                        }
                        // If we get an exception on accept(), we should just
                        // exit
                        break;
                    }
                }
                if (Trace.ON && debug != null) {
                    debug.msg("Closing listener normally.");
                }
            }
        }, "Server(" + getLocalPort() + ")");
    }

    protected void handleAccept(final Socket aSocket) {
        new Thread(threadGroup, new Runnable() {
            public void run() {
                try {
                    debug("accept:" + aSocket.getInetAddress());
                    acceptHandler.handleAccept(aSocket);
                } catch (Exception e) {
                    dumpStack("Unexpected exception in handleAccept...closing",
                            e);
                    try {
                        aSocket.close();
                    } catch (IOException e1) {
                    }
                } finally {
                }
            }
        }).start();
    }

    public synchronized void close() throws IOException {
        super.close();
        if (listenerThread != null) {
            listenerThread.interrupt();
            listenerThread = null;
        }
        if (threadGroup != null) {
            threadGroup.interrupt();
            threadGroup = null;
        }
        acceptHandler = null;
    }
}
 No newline at end of file