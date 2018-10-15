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

import java.io.IOException;
import org.eclipse.ecf.core.identity.ID;

/**
 * Synchronous connection
 * 
 */
public interface ISynchConnection extends IConnection {
	/**
	 * Send data synchronously, blocking until a result is received
	 * 
	 * @param receiver
	 *            the receiver to receive the synchronous request
	 * @param data
	 *            the data to send
	 * @return the data received. The return type will be specific to the
	 *         provider implementation.
	 * @throws IOException
	 *             thrown if sending cannot occur (e.g. not connected)
	 */
	public Object sendSynch(ID receiver, byte[] data) throws IOException;
}
 No newline at end of file