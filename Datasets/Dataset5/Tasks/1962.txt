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
 * Asynchronous connection
 * 
 */
public interface IAsynchConnection extends IConnection {
	/**
	 * Send data asynchronously. Implementing classes should not block on
	 * sending the given data and return immediately.
	 * 
	 * @param receiver
	 *            the ID of the intended receiver
	 * @param data
	 *            the data to send
	 * @throws IOException
	 *             thrown if data cannot be sent (e.g. disconnected)
	 */
	public void sendAsynch(ID receiver, byte[] data) throws IOException;
}
 No newline at end of file