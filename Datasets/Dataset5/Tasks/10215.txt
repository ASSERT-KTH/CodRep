public interface IChannelDisconnectEvent extends IChannelEvent {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc., Peter Nehrer, Boris Bokowski. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.datashare.events;

import org.eclipse.ecf.core.identity.ID;

/**
 * Event delivered to IChannelListener when the container for channel
 * departs from group
 *
 */
public interface IChannelGroupDepartEvent extends IChannelEvent {
	/**
	 * Get ID of target group that departed
	 * @return ID of target group that departed
	 */
	public ID getTargetID();
}