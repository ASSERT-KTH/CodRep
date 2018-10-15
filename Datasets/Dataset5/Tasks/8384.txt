package org.eclipse.ecf.core.sharedobject;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.core;

import org.eclipse.ecf.core.identity.ID;

/**
 * Filter for determining transaction participants
 * 
 */
public interface ISharedObjectTransactionParticipantsFilter {
	/**
	 * Return ID[] of participants to participate in transacton.
	 * 
	 * @param currentGroup
	 *            the current set of container group members
	 * @return intended participants in transaction. If null is returned, all
	 *         group members will be included in transaction.
	 */
	ID[] filterParticipants(ID[] currentGroup);
}