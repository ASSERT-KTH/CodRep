package org.eclipse.ecf.presence.im;

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

/**
 * Adapter interface for chatIDs. The typical usage of this adapter is as
 * follows:
 * 
 * <pre>
 *     ID myID = ...
 *     IChatID chatID = (IChatID) myID.getAdapter(IChatID.class);
 *     if (chatID != null) {
 *       ...use chatID here
 *     }
 * </pre>
 * 
 */
public interface IChatID {
	/**
	 * Get username for this IChatID
	 * 
	 * @return String username for the implementing IChatID. May return null.
	 */
	public String getUsername();
}