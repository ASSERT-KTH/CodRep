public interface IAbstractChannelContainerAdapter {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.datashare;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;

/**
 * Abstract channel container adapter
 * 
 */
public interface IAbstractChannelContainerAdaper {
	/**
	 * Add listener for IChannelContainerAdapter events.
	 * 
	 * @param listener
	 *            to be added
	 */
	public void addListener(IChannelContainerListener listener);

	/**
	 * Remove listener for IChannelContainerAdapter events
	 * 
	 * @param listener
	 *            to be removed.
	 */
	public void removeListener(IChannelContainerListener listener);

	/**
	 * Get expected Namespace for channel ID creation
	 * 
	 * @return Namespace that can be used to create channel ID instances for
	 *         this channel container
	 */
	public Namespace getChannelNamespace();

	/**
	 * Get IChannel with given channelID.
	 * 
	 * @param channelID
	 *            the ID of the channel to get
	 * @return IChannel of channel within container with given ID. Returns null
	 *         if channel not found.
	 */
	public IChannel getChannel(ID channelID);

	/**
	 * Remove channel with given ID
	 * 
	 * @param channelID
	 *            the ID of the channel to Remove within this container
	 * @return true if channel found and Removed. False if channel not found
	 *         within container.
	 */
	public boolean removeChannel(ID channelID);
}