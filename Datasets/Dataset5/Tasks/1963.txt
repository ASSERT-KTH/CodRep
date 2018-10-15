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

/**
 * Callback interface for handling asynchronous connection events
 * 
 */
public interface IAsynchEventHandler extends IConnectionListener {
	/**
	 * Handle asynchronous connection event
	 * 
	 * @param event
	 *            the asynchronous connection event to handle
	 * @throws IOException
	 *             if connection event cannot be handled
	 */
	public void handleAsynchEvent(AsynchEvent event) throws IOException;
}
 No newline at end of file