import org.eclipse.ecf.core.identity.IIdentifiable;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.datashare;

import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.IIdentifiable;

/**
 * Abstract channel
 *
 */
public interface IAbstractChannel extends IAdaptable, IIdentifiable {
	/**
	 * Get IChannelListener instance for this IAbstractChannel
	 * 
	 * @return IChannelListener for this IAbstractChannel instance.  If null, the channel has no listener
	 */
	public IChannelListener getListener();
	
	/**
	 * Set listener to new IChannelListener instance
	 * 
	 * @return IChannelListener that was previously the listener.  If null, then then channel had no previous listener
	 */
	public IChannelListener setListener(IChannelListener listener);
}