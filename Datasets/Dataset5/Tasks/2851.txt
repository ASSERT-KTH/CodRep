private TPCommitEventProcessor eventProcessor = null;

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
package org.eclipse.ecf.provider.generic.sobject;

import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.SharedObjectAddAbortException;
import org.eclipse.ecf.core.identity.ID;

/**
 * @author slewis
 *
 */
public class SharedObjectReplication implements
		ISharedObjectContainerTransaction {

	TPCommitEventProcessor eventProcessor = null;
	public SharedObjectReplication(ISharedObjectInternal so, int transactionTimeout, ID [] exceptions) {
		eventProcessor = new TPCommitEventProcessor(so,transactionTimeout,exceptions);
		so.addEventProcessor(eventProcessor);
	}
	public SharedObjectReplication(ISharedObjectInternal so,int transactionTimeout) {
		eventProcessor = new TPCommitEventProcessor(so,transactionTimeout);
		so.addEventProcessor(eventProcessor);
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerTransaction#waitToCommit()
	 */
	public void waitToCommit() throws SharedObjectAddAbortException {
		eventProcessor.waitToCommit();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObjectContainerTransaction#getTransactionState()
	 */
	public byte getTransactionState() {
		return eventProcessor.getTransactionState();
	}

}