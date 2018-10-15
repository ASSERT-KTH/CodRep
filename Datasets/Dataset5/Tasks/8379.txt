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

import java.io.Serializable;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.IConnectPolicy;

/**
 * Contract for shared object container group manager (e.g. servers)
 */
public interface ISharedObjectContainerGroupManager {
	/**
	 * Set the join policy for this group manager. If the policy is set to null,
	 * the implementing container is not obligated to consult the policy. If
	 * non-null, the given policy's checkJoin method is called before the
	 * manager agrees to the join of a given group participant.
	 * 
	 * @param policy
	 */
	public void setConnectPolicy(IConnectPolicy policy);

	/**
	 * Eject the given groupMemberID from the current group of containers, for
	 * the given reason.
	 * 
	 * @param groupMemberID
	 *            the ID of the group member to eject. If null, or if group
	 *            member is not in group managed by this object, the method has
	 *            no effect
	 * @param reason
	 *            a reason for the ejection
	 */
	public void ejectGroupMember(ID groupMemberID, Serializable reason);

	/**
	 * Eject all, for the given reason.
	 * 
	 * @param reason
	 *            a reason for the ejection
	 */
	public void ejectAllGroupMembers(Serializable reason);
}