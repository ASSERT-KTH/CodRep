throw new IllegalArgumentException("UpdateMessage is incompatible with Cola SynchronizationStrategy"); //$NON-NLS-1$

package org.eclipse.ecf.docshare.cola;

import java.util.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.docshare.SynchronizationStrategy;
import org.eclipse.ecf.docshare.messages.UpdateMessage;
import org.eclipse.ecf.internal.docshare.Activator;

public class ColaSynchronizer implements SynchronizationStrategy {

	private List unacknowledgedLocalOperations;
	private final boolean isInitiator;
	private double localOperationsCount;
	private double remoteOperationsCount;

	private static Map sessionStrategies = new HashMap();

	private ColaSynchronizer(ID docshareID) {
		this.isInitiator = Activator.getDefault().getDocShare(docshareID).isInitiator();
		unacknowledgedLocalOperations = new LinkedList();
		localOperationsCount = 0;
		remoteOperationsCount = 0;
	}

	public static ColaSynchronizer getInstanceFor(ID docshareID) {
		if (sessionStrategies.get(docshareID) == null) {
			sessionStrategies.put(docshareID, new ColaSynchronizer(docshareID));
		}
		return (ColaSynchronizer) sessionStrategies.get(docshareID);
	}

	public static void cleanUpFor(ID docshareID) {
		sessionStrategies.remove(docshareID);
	}

	public UpdateMessage registerOutgoingMessage(UpdateMessage localMsg) {
		ColaUpdateMessage colaMsg = new ColaUpdateMessage(localMsg, localOperationsCount, remoteOperationsCount);
		unacknowledgedLocalOperations.add(colaMsg);
		localOperationsCount++;
		return colaMsg;
	}

	/**
	 * Handles proper transformation of incoming <code>ColaUpdateMessage</code>s.
	 * Returned <code>UpdateMessage</code>s can be applied directly to the
	 * shared document. The method implements the concurreny algorithm described
	 * in <code>http://wiki.eclipse.org/RT_Shared_Editing</code>
	 */
	public UpdateMessage transformIncomingMessage(final UpdateMessage remoteMsg) {
		if (!(remoteMsg instanceof ColaUpdateMessage)) {
			throw new IllegalArgumentException("UpdateMessage is incompatible with Cola SynchronizationStrategy");
		}
		ColaUpdateMessage transformedRemote = (ColaUpdateMessage) remoteMsg;
		// TODO this is where the concurrency algorithm is executed
		if (!unacknowledgedLocalOperations.isEmpty()) {
			// remove operations from queue that have been implicitly
			// acknowledged as received on the remote site by the reception of
			// this message
			Iterator queueIterator = unacknowledgedLocalOperations.iterator();
			ColaUpdateMessage localOperation = (ColaUpdateMessage) queueIterator.next();
			while (!unacknowledgedLocalOperations.isEmpty() && transformedRemote.getRemoteOperationsCount() > localOperation.getLocalOperationsCount()) {
				queueIterator.remove();
				if (queueIterator.hasNext()) {
					localOperation = (ColaUpdateMessage) queueIterator.next();
				}
			}// at this point the queue has been freed of operations that
			// don't require to be transformed against
			if (!unacknowledgedLocalOperations.isEmpty()) {
				Iterator queueModIterator = unacknowledgedLocalOperations.iterator();
				while (queueModIterator.hasNext()) {
					// returns new instance
					// clarify operation preference, owner/docshare initiator
					// consistently comes first
					if (this.isInitiator) {
						transformedRemote = transformedRemote.transformForApplicationAtOwnerAgainst(localOperation);
					} else {
						transformedRemote = transformedRemote.transformForApplicationAtParticipantAgainst(localOperation);
					}
					localOperation = (ColaUpdateMessage) queueModIterator.next();
				}
				// TODO unsure whether this is needed or not, need to test
				// transform against last element in the queue
				if (this.isInitiator) {
					transformedRemote = transformedRemote.transformForApplicationAtOwnerAgainst(localOperation);
				} else {
					transformedRemote = transformedRemote.transformForApplicationAtParticipantAgainst(localOperation);
				}
			}
		}
		return transformedRemote;

	}
}
 No newline at end of file