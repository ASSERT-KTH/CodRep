package org.eclipse.ecf.datashare;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.ds;

import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.IIdentifiable;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;

/**
 * Channel for sending messages
 * 
 */
public interface IChannel extends IAdaptable, IIdentifiable {
	/**
	 * Send message to remote instances of this channel
	 * 
	 * @param message
	 *            the byte [] message to send
	 * @throws ECFException
	 *             if some problem sending message
	 */
	public void sendMessage(byte[] message) throws ECFException;
	/**
	 * Send message to remote instances of this channel
	 * 
	 * @param receiver
	 *            the ID of the container to receive message. If null, message
	 *            sent to all current members of group
	 * @param message
	 *            the byte [] message to send
	 * @throws ECFException
	 *             if some problem sending message
	 */
	public void sendMessage(ID receiver, byte[] message) throws ECFException;
}