package org.eclipse.ecf.internal.provisional.docshare.messages;

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.docshare.messages;

import org.eclipse.ecf.core.identity.ID;

/**
 *
 */
public class StartMessage extends Message {

	private static final long serialVersionUID = 4712028336072890912L;

	private final ID senderID;
	private final ID receiverID;
	private final String fromUsername;
	private final String fileName;
	private final String documentContent;

	public StartMessage(ID senderID, String fromUser, ID receiverID, String content, String file) {
		this.senderID = senderID;
		this.receiverID = receiverID;
		this.fromUsername = fromUser;
		this.fileName = file;
		this.documentContent = content;
	}

	public ID getSenderID() {
		return senderID;
	}

	public ID getReceiverID() {
		return receiverID;
	}

	public String getSenderUsername() {
		return fromUsername;
	}

	public String getFilename() {
		return fileName;
	}

	public String getDocumentContent() {
		return documentContent;
	}
}