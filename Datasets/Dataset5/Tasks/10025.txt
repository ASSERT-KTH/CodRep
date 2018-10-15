import org.eclipse.ecf.sync.doc.DocumentChangeMessage;

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

package org.eclipse.ecf.internal.sync.doc.cola;

import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.sync.Activator;
import org.eclipse.ecf.internal.sync.SyncDebugOptions;
import org.eclipse.ecf.sync.doc.messages.DocumentChangeMessage;

public class ColaInsertionTransformationStategy implements ColaTransformationStrategy {

	private static final long serialVersionUID = 5192625383622519749L;
	private static ColaInsertionTransformationStategy INSTANCE;

	private ColaInsertionTransformationStategy() {
		// default constructor is private to enforce singleton property via
		// static factory method
	}

	public static ColaTransformationStrategy getInstance() {
		if (INSTANCE == null) {
			INSTANCE = new ColaInsertionTransformationStategy();
		}
		return INSTANCE;
	}

	/**
	 * Resolves two conflicting <code>ColaDocumentChangeMessage</code>s by applying an appropriate operational transform.
	 * 
	 * If necessary, modifies <code>localAppliedMsg</code> as well to reflect knowledge of <code>remoteIncomingMsg</code> 
	 * in case more conflicting/further diverging remote messages arrive.  
	 * 
	 * @param remoteIncomingMsg message originating from remote site, generated on same document state as <code>localAppliedMsg</code>
	 * @param localAppliedMsg message already applied to local document, generation state corresponds to that of <code>remoteIncomingMsg</code>
	 * @param localMsgHighPrio determines insertion preference for same offsets, if true localAppliedMsg comes first
	 * @return operational transform of remote message, not conflicting with applied local message
	 */
	public ColaDocumentChangeMessage getOperationalTransform(ColaDocumentChangeMessage remoteIncomingMsg, ColaDocumentChangeMessage localAppliedMsg, boolean localMsgHighPrio) {

		Trace.entering(Activator.PLUGIN_ID, SyncDebugOptions.METHODS_ENTERING, this.getClass(), "getOperationalTransform", new Object[] {remoteIncomingMsg, localAppliedMsg, new Boolean(localMsgHighPrio)}); //$NON-NLS-1$

		final ColaDocumentChangeMessage remoteTransformedMsg = remoteIncomingMsg;

		if (localAppliedMsg.isInsertion()) {

			if (remoteTransformedMsg.getOffset() < localAppliedMsg.getOffset()) {
				//coopt(remote(low),local(high)) --> (remote(low),local(low + high))
				localAppliedMsg.setOffset(localAppliedMsg.getOffset() + remoteTransformedMsg.getOffset());
			} else if (remoteTransformedMsg.getOffset() == localAppliedMsg.getOffset()) {
				//coopt(remote(same),local(same))
				if (localMsgHighPrio) {
					//at owner --> (remote(high),local(same))
					remoteTransformedMsg.setOffset(remoteTransformedMsg.getOffset() + localAppliedMsg.getText().length());
				} else {
					//at participant --> (remote(same),local(high))
					localAppliedMsg.setOffset(localAppliedMsg.getOffset() + remoteTransformedMsg.getText().length());
				}
			} else if (remoteTransformedMsg.getOffset() > localAppliedMsg.getOffset()) {
				//coopt(remote(high),local(low)) --> (remote(low + high),local(low))
				remoteTransformedMsg.setOffset(remoteTransformedMsg.getOffset() + localAppliedMsg.getText().length());
			}

		} else if (localAppliedMsg.isDeletion()) {

			if (remoteTransformedMsg.getOffset() <= localAppliedMsg.getOffset()) {

				localAppliedMsg.setOffset(localAppliedMsg.getOffset() + remoteTransformedMsg.getLengthOfInsertedText());

			} else if (remoteTransformedMsg.getOffset() > localAppliedMsg.getOffset()) {

				if (remoteTransformedMsg.getOffset() > (localAppliedMsg.getOffset() + localAppliedMsg.getLengthOfReplacedText())) {

					remoteTransformedMsg.setOffset(remoteTransformedMsg.getOffset() - localAppliedMsg.getLengthOfReplacedText());
				} else if (remoteTransformedMsg.getOffset() <= (localAppliedMsg.getOffset() + localAppliedMsg.getLengthOfReplacedText())) {

					//TODO test this ^#$%^#$ case
					final DocumentChangeMessage deletionFirstMessage = new DocumentChangeMessage(localAppliedMsg.getOffset(), remoteTransformedMsg.getOffset() - localAppliedMsg.getOffset(), localAppliedMsg.getText());
					final ColaDocumentChangeMessage deletionFirstPart = new ColaDocumentChangeMessage(deletionFirstMessage, localAppliedMsg.getLocalOperationsCount(), localAppliedMsg.getRemoteOperationsCount());
					localAppliedMsg.addToSplitUpRepresentation(deletionFirstPart);

					final DocumentChangeMessage deletionSecondMessage = new DocumentChangeMessage(localAppliedMsg.getOffset() + remoteTransformedMsg.getLengthOfInsertedText(), localAppliedMsg.getLengthOfReplacedText() - deletionFirstPart.getLengthOfReplacedText(), localAppliedMsg.getText());
					final ColaDocumentChangeMessage deletionSecondPart = new ColaDocumentChangeMessage(deletionSecondMessage, localAppliedMsg.getLocalOperationsCount(), localAppliedMsg.getRemoteOperationsCount());
					localAppliedMsg.addToSplitUpRepresentation(deletionSecondPart);

					localAppliedMsg.setSplitUp(true);

					remoteTransformedMsg.setOffset(localAppliedMsg.getOffset());

				}
			}
		}

		Trace.exiting(Activator.PLUGIN_ID, SyncDebugOptions.METHODS_EXITING, this.getClass(), "getOperationalTransform", remoteTransformedMsg); //$NON-NLS-1$
		return remoteTransformedMsg;
	}
}