import org.eclipse.ecf.core.sharedobject.events.ISharedObjectMessageEvent;

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
package org.eclipse.ecf.presence;

import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;

/**
 * Listener for receiving shared object messages
 * 
 */
public interface ISharedObjectMessageListener {
	/**
	 * Receive shared object message via shared object message event.
	 * 
	 * @param event
	 *            the shared object message event holding the shared object
	 *            message
	 */
	public void handleSharedObjectMessage(ISharedObjectMessageEvent event);
}