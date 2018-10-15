IAbstractChannelContainerAdapter {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.datashare;

import java.util.Map;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;

/**
 * Channel container entry point adapter. This interface is an adapter to allow
 * providers to expose channels to clients. It may be used in the following way:
 * <p>
 * 
 * <pre>
 *  IChannelContainerAdapter channelcontainer = (IChannelContainerAdapter) container.getAdapter(IChannelContainerAdapter.class);
 *  if (channelcontainer != null) {
 *     // use channelcontainer
 *     ...
 *  } else {
 *     // container does not support channel container functionality
 *  }
 * </pre>
 * 
 */
public interface IChannelContainerAdapter extends
		IAbstractChannelContainerAdaper {
	/**
	 * Create a new channel within this container
	 * 
	 * @param channelID
	 *            the ID of the new channel. Must not be null
	 * @param listener
	 *            a listener for receiving messages from remotes for this
	 *            channel. Must not be null
	 * @param properties
	 *            a Map of properties to provide to the channel.
	 * @return IChannel the new IChannel instance
	 * @throws ECFException
	 *             if some problem creating IChannel instance
	 */
	public IChannel createChannel(ID channelID, IChannelListener listener,
			Map properties) throws ECFException;

	/**
	 * Create a new channel within this container
	 * 
	 * @param newChannelConfig
	 *            the configuration for the newly created channel. Must not be
	 *            null
	 * @return IChannel the new IChannel instance
	 * @throws ECFException
	 *             if some problem creating IChannel instance
	 */
	public IChannel createChannel(IChannelConfig newChannelConfig)
			throws ECFException;
}