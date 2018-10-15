Trace.trace(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.CONNECTION, msg);

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
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.provider.*;

public class Server extends ServerSocket {

	public static final int DEFAULT_BACKLOG = 50;

	ISocketAcceptHandler acceptHandler;
	Thread listenerThread;
	ThreadGroup threadGroup;

	protected void debug(String msg) {
		Trace.trace(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.DEBUG, msg);
	}

	protected void traceStack(String msg, Throwable e) {
		Trace.catching(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.EXCEPTIONS_CATCHING, Server.class, msg, e);
	}

	public Server(ThreadGroup group, int port, ISocketAcceptHandler handler) throws IOException {
		super(port, DEFAULT_BACKLOG);
		if (handler == null)
			throw new InstantiationError(Messages.Server_Listener_Not_Null);
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
						traceStack("Exception in accept", e); //$NON-NLS-1$
						// If we get an exception on accept(), we should just
						// exit
						break;
					}
				}
				debug("Closing listener normally."); //$NON-NLS-1$
			}
		}, "ServerApplication(" + getLocalPort() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
	}

	protected void handleAccept(final Socket aSocket) {
		new Thread(threadGroup, new Runnable() {
			public void run() {
				try {
					debug("accept:" + aSocket.getInetAddress()); //$NON-NLS-1$
					acceptHandler.handleAccept(aSocket);
				} catch (Exception e) {
					traceStack("Unexpected exception in handleAccept...closing", //$NON-NLS-1$
							e);
					try {
						aSocket.close();
					} catch (IOException e1) {
						ProviderPlugin.getDefault().log(new Status(IStatus.ERROR, ProviderPlugin.PLUGIN_ID, IStatus.ERROR, "accept.close", e1)); //$NON-NLS-1$
					}
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