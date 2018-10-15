public IDocumentChange deserializeRemoteChange(byte[] bytes) throws SerializationException {

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.sync.doc.identity;

import org.eclipse.ecf.sync.doc.IDocumentChange;
import org.eclipse.ecf.sync.doc.IDocumentChangeMessage;
import org.eclipse.ecf.sync.doc.IDocumentSynchronizationStrategy;
import org.eclipse.ecf.sync.doc.SerializationException;
import org.eclipse.ecf.sync.doc.messages.DocumentChangeMessage;

/**
 *
 */
public class IdentitySynchronizationStrategy implements IDocumentSynchronizationStrategy {

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.sync.doc.IDocumentSynchronizationStrategy#deserializeToDocumentChange(byte[])
	 */
	public IDocumentChange deserializeToDocumentChange(byte[] bytes) throws SerializationException {
		return DocumentChangeMessage.deserialize(bytes);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.sync.doc.IDocumentSynchronizationStrategy#registerLocalChange(org.eclipse.ecf.sync.doc.IDocumentChange)
	 */
	public IDocumentChangeMessage[] registerLocalChange(IDocumentChange localChange) {
		return new IDocumentChangeMessage[] {new DocumentChangeMessage(localChange.getOffset(), localChange.getLengthOfReplacedText(), localChange.getText())};
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.sync.doc.IDocumentSynchronizationStrategy#transformRemoteChange(org.eclipse.ecf.sync.doc.IDocumentChange)
	 */
	public IDocumentChange[] transformRemoteChange(IDocumentChange remoteChange) {
		return new IDocumentChange[] {remoteChange};
	}

}