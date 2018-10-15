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

import java.util.Map;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.util.ECFException;

/**
 * Channel container entry point interface.  This interface is an adapter to allow
 * providers to expose channels to clients.  It may be used in the following
 * way:
 * <p>
 * <pre>
 * IChannelContainer channelcontainer = (IChannelContainer) container.getAdapter(IChannelContainer.class);
 * if (channelcontainer != null) {
 *    // use channelcontainer
 *    ...
 * } else {
 *    // container does not support channel container functionality
 * }
 * </pre>
 * 
 */
public interface IChannelContainer {
	/**
	 * Get expected Namespace for channel ID creation
	 * @return Namespace that can be used to create channel ID instances
	 * for this channel container
	 */
	public Namespace getChannelNamespace();
	
	/**
	 * Create a new channel within this container
	 * @param channelID the ID of the new channel.  Must not be null
	 * @param listener a listener for receiving messages from remotes for this channel.  Must not be null
	 * @param properties a Map of properties to provide to the channel.
	 * @return IChannel the new IChannel instance
	 * @throws ECFException if some problem creating IChannel instance
	 */
	public IChannel createChannel(ID channelID, IChannelListener listener, Map properties) throws ECFException;
	/**
	 * Create a new channel within this container
	 * @param newChannelConfig the configuration for the newly created channel.  Must not be null
	 * @return IChannel the new IChannel instance
	 * @throws ECFException if some problem creating IChannel instance
	 */
	public IChannel createChannel(IChannelConfig newChannelConfig) throws ECFException;
	/**
	 * Get IChannel with given channelID.  
	 * @param channelID the ID of the channel to get
	 * @return IChannel of channel within container with given ID.  Returns null if channel not found.
	 */
	public IChannel getChannel(ID channelID);
	/**
	 * Remove channel with given ID
	 * @param channelID the ID of the channel to Remove within this container
	 * @return true if channel found and Removed.  False if channel not found within container.
	 */
	public boolean removeChannel(ID channelID);
}