package org.eclipse.ecf.core.sharedobject;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core;

import org.eclipse.ecf.core.identity.ID;

public interface IReplicaSharedObjectDescriptionFactory {
	/**
	 * Create new ReplicaSharedObjectDescription instance for delivery to remote
	 * container identified by containerID parameter.  The containerID parameter ID
	 * provided must not be null
	 * 
	 * @param containerID
	 * @return ReplicaSharedObjectDescription.  Must not return null, but rather a valid
	 * ReplicaSharedObjectDescription instance
	 */
	public ReplicaSharedObjectDescription createDescriptionForContainer(ID containerID, ISharedObjectConfig config);
}