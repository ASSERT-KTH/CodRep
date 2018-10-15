package org.eclipse.ecf.provider.comm;

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
package org.eclipse.ecf.core.comm;

import java.io.Serializable;
import java.net.Socket;

/**
 * Connection request handler
 * 
 */
public interface IConnectRequestHandler {
	/**
	 * Handle a connect request from remote client
	 * 
	 * @param aSocket
	 *            the Socket that the request came in on
	 * @param target
	 *            the target that the request is intended for
	 * @param data
	 *            any data that was sent along with request (e.g. password or
	 *            other authentication data)
	 * @param conn
	 *            the connection instance that received the request
	 * @return any data intended as a response. If null is returned, this
	 *         typically means refusal of connect request
	 */
	public Serializable handleConnectRequest(Socket aSocket, String target,
			Serializable data, ISynchAsynchConnection conn);
}
 No newline at end of file