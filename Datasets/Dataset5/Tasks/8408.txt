package org.eclipse.ecf.core.sharedobject.events;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.events;

import org.eclipse.ecf.core.identity.ID;

/**
 * @author slewis
 * 
 */
public class SharedObjectManagerDisconnectEvent implements
		ISharedObjectManagerEvent {
	private static final long serialVersionUID = 3257008743777448761L;
	ID localContainerID = null;
	ID sharedObjectSenderID = null;

	public SharedObjectManagerDisconnectEvent(ID localContainerID,
			ID sharedObjectSenderID) {
		this.localContainerID = localContainerID;
		this.sharedObjectSenderID = sharedObjectSenderID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.events.IContainerEvent#getLocalContainerID()
	 */
	public ID getLocalContainerID() {
		return localContainerID;
	}

	public ID getSharedObjectSenderID() {
		return sharedObjectSenderID;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer(
				"SharedObjectManagerDisconnectEvent[");
		buf.append(getLocalContainerID()).append(";");
		buf.append(getSharedObjectSenderID()).append(";");
		return buf.toString();
	}
}