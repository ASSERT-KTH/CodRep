Assert.isTrue(transformedRemote.getRemoteOperationsCount() == localOp.getLocalOperationsCount());

/****************************************************************************
 * Copyright (c) 2008 Mustafa K. Isik and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Mustafa K. Isik - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.docshare.cola;

import java.util.*;
import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.docshare.DocShare;
import org.eclipse.ecf.docshare.SynchronizationStrategy;
import org.eclipse.ecf.docshare.messages.UpdateMessage;
import org.eclipse.ecf.internal.docshare.Activator;
import org.eclipse.ecf.internal.docshare.DocshareDebugOptions;
import org.eclipse.osgi.util.NLS;

public class ColaSynchronizer implements SynchronizationStrategy {

	// <ColaUpdateMessage>
	private final LinkedList unacknowledgedLocalOperations;
	private final boolean isInitiator;
	private long localOperationsCount;
	private long remoteOperationsCount;

	// <DocShare, ColaSynchronizer>
	private static Map sessionStrategies = new HashMap();

	private ColaSynchronizer(DocShare docshare) {
		this.isInitiator = docshare.isInitiator();
		unacknowledgedLocalOperations = new LinkedList();
		localOperationsCount = 0;
		remoteOperationsCount = 0;
	}

	public static ColaSynchronizer getInstanceFor(DocShare docshare) {
		if (sessionStrategies.get(docshare) == null) {
			sessionStrategies.put(docshare, new ColaSynchronizer(docshare));
		}
		return (ColaSynchronizer) sessionStrategies.get(docshare);
	}

	public static void cleanUpFor(DocShare docshare) {
		sessionStrategies.remove(docshare);
	}

	public UpdateMessage registerOutgoingMessage(UpdateMessage localMsg) {
		Trace.entering(Activator.PLUGIN_ID, DocshareDebugOptions.METHODS_ENTERING, this.getClass(), "registerOutgoingMessage", localMsg); //$NON-NLS-1$
		final ColaUpdateMessage colaMsg = new ColaUpdateMessage(localMsg, localOperationsCount, remoteOperationsCount);
		unacknowledgedLocalOperations.add(colaMsg);
		localOperationsCount++;
		Trace.exiting(Activator.PLUGIN_ID, DocshareDebugOptions.METHODS_EXITING, this.getClass(), "registerOutgoingMessage", colaMsg); //$NON-NLS-1$
		return colaMsg;
	}

	/**
	 * Handles proper transformation of incoming <code>ColaUpdateMessage</code>s.
	 * Returned <code>UpdateMessage</code>s can be applied directly to the
	 * shared document. The method implements the concurrency algorithm described
	 * in <code>http://wiki.eclipse.org/RT_Shared_Editing</code>
	 * @param remoteMsg 
	 * @return UpdateMessage
	 */
	public UpdateMessage transformIncomingMessage(final UpdateMessage remoteMsg) {
		if (!(remoteMsg instanceof ColaUpdateMessage)) {
			throw new IllegalArgumentException("UpdateMessage is incompatible with Cola SynchronizationStrategy"); //$NON-NLS-1$
		}
		Trace.entering(Activator.PLUGIN_ID, DocshareDebugOptions.METHODS_ENTERING, this.getClass(), "transformIncomingMessage", remoteMsg); //$NON-NLS-1$
		ColaUpdateMessage transformedRemote = (ColaUpdateMessage) remoteMsg;
		remoteOperationsCount++;
		// TODO this is where the concurrency algorithm is executed
		if (!unacknowledgedLocalOperations.isEmpty()) {
			// remove operations from queue that have been implicitly
			// acknowledged as received on the remote site by the reception of
			// this message
			for (final Iterator it = unacknowledgedLocalOperations.iterator(); it.hasNext();) {
				ColaUpdateMessage unackedLocalOp = (ColaUpdateMessage) it.next();
				if (transformedRemote.getRemoteOperationsCount() > unackedLocalOp.getLocalOperationsCount()) {
					Trace.trace(Activator.PLUGIN_ID, NLS.bind("transformIncomingMessage.removing {0}", unackedLocalOp)); //$NON-NLS-1$
					it.remove();
				} else {
					// the unackowledgedLocalOperations queue is ordered and
					// sorted
					// due to sequential insertion of local ops, thus once a
					// local op with a higher
					// or equal local op count (i.e. remote op count from the
					// remote operation's view)
					// is reached, we can abandon the check for the remaining
					// queue items
					Trace.trace(Activator.PLUGIN_ID, "breaking out of unackedLocalOperations loop"); //$NON-NLS-1$
					break;// exits for-loop
				}
			}
			// at this point the queue has been freed of operations that
			// don't require to be transformed against

			// TODO this is where the BUG is - I am not adapting/modifying the
			// queued up operations!!! 2008-06-08
			if (!unacknowledgedLocalOperations.isEmpty()) {
				ColaUpdateMessage localOp = (ColaUpdateMessage) unacknowledgedLocalOperations.getFirst();
				Assert.isTrue(transformedRemote.getRemoteOperationsCount() == localOp.localOperationsCount);
				for (final Iterator it = unacknowledgedLocalOperations.iterator(); it.hasNext();) {
					// returns new instance
					// clarify operation preference, owner/docshare initiator
					// consistently comes first

					transformedRemote = transformedRemote.transformAgainst((ColaUpdateMessage) it.next(), isInitiator);

				}
			}

		}
		Trace.exiting(Activator.PLUGIN_ID, DocshareDebugOptions.METHODS_EXITING, this.getClass(), "transformIncomingMessage", transformedRemote); //$NON-NLS-1$
		return transformedRemote;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("ColaSynchronizer"); //$NON-NLS-1$
		return buf.toString();
	}
}
 No newline at end of file