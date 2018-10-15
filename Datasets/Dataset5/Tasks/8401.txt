package org.eclipse.ecf.core.sharedobject.events;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.events;

import org.eclipse.ecf.core.identity.ID;

public class RemoteSharedObjectCreateResponseEvent extends
		RemoteSharedObjectEvent implements ISharedObjectCreateResponseEvent {
	private static final long serialVersionUID = 3618421544527738673L;
	long sequence = 0;

	public RemoteSharedObjectCreateResponseEvent(ID senderObj, ID remoteCont,
			long seq, Throwable exception) {
		super(senderObj, remoteCont, exception);
		this.sequence = seq;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.events.ISharedObjectCreateResponseEvent#getSequence()
	 */
	public long getSequence() {
		return sequence;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.events.ISharedObjectCreateResponseEvent#getException()
	 */
	public Throwable getException() {
		return (Throwable) getData();
	}

	public String toString() {
		StringBuffer sb = new StringBuffer(
				"RemoteSharedObjectCreateResponseEvent[");
		sb.append(getSenderSharedObjectID()).append(";");
		sb.append(getRemoteContainerID()).append(";");
		sb.append(getSequence()).append(";");
		sb.append(getException()).append("]");
		return sb.toString();
	}
}
 No newline at end of file