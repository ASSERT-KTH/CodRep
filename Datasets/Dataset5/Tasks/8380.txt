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

/**
 * Implementers represent a transaction associated with the creation of a
 * SharedObject within the scope of a given SharedObjectContainer
 * 
 */
public interface ISharedObjectContainerTransaction {
	public static final byte ACTIVE = 0;
	public static final byte VOTING = 1;
	public static final byte PREPARED = 2;
	public static final byte COMMITTED = 3;
	public static final byte ABORTED = 4;

	/**
	 * Method called to wait for a transaction to complete.
	 * 
	 * @throws SharedObjectAddAbortException
	 */
	public void waitToCommit() throws SharedObjectAddAbortException;

	/**
	 * Get state of transaction. Returns one of 'ACTIVE', 'VOTING', 'PREPARED',
	 * 'COMMITTED', or 'ABORTED'.
	 * 
	 * @return byte code. Returns one of 'ACTIVE', 'VOTING', 'PREPARED',
	 *         'COMMITTED', or 'ABORTED'.
	 */
	public byte getTransactionState();
}
 No newline at end of file