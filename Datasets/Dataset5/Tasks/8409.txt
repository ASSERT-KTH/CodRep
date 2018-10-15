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
public class SharedObjectManagerRemoveEvent implements
		ISharedObjectManagerEvent {
	private static final long serialVersionUID = 3256728389754106931L;
	ID sharedObjectID = null;
	ID localContainerID = null;

	public SharedObjectManagerRemoveEvent(ID localContainerID, ID sharedObjectID) {
		this.localContainerID = localContainerID;
		this.sharedObjectID = sharedObjectID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.events.IContainerEvent#getLocalContainerID()
	 */
	public ID getLocalContainerID() {
		return localContainerID;
	}

	public ID getSharedObjectID() {
		return sharedObjectID;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("SharedObjectManagerRemoveEvent[");
		buf.append(getLocalContainerID()).append(";");
		buf.append(getSharedObjectID()).append("]");
		return buf.toString();
	}
}