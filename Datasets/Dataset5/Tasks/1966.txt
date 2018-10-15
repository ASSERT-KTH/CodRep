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

import org.eclipse.ecf.core.identity.ID;

/**
 * Connection listener
 * 
 * @see IConnection#addListener(IConnectionListener)
 * 
 */
public interface IConnectionListener {
	/**
	 * Get ID of event handler
	 * 
	 * @return ID of event handler
	 */
	public ID getEventHandlerID();

	/**
	 * Handle disconnect event
	 * 
	 * @param event
	 *            the disconnect event
	 */
	public void handleDisconnectEvent(DisconnectEvent event);

}
 No newline at end of file