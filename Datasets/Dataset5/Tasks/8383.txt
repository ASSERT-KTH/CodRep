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


/**
 * Transaction configuration information
 * 
 */
public interface ISharedObjectTransactionConfig {
	public static final int DEFAULT_TIMEOUT = 30000;
	/**
	 * Called by transaction implementation to specify transaction timeout
	 */
	int getTimeout();
	/**
	 * Called by transaction implementation to specify filter for determining
	 * transaction participants
	 * 
	 * @return {@link ISharedObjectTransactionParticipantsFilter}. If this method returns a
	 *         non-null instance, that instance's
	 *         {@link ISharedObjectTransactionParticipantsFilter#filterParticipants(org.eclipse.ecf.core.identity.ID[]) }
	 *         method will be called
	 */
	ISharedObjectTransactionParticipantsFilter getParticipantsFilter();
}
 No newline at end of file