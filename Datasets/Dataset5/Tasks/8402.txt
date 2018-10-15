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

import java.io.Serializable;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;

public class RemoteSharedObjectEvent implements ISharedObjectMessageEvent,
		Serializable {
	private static final long serialVersionUID = 3257572797621680182L;
	private final ID senderSharedObjectID;
	private final ID remoteContainerID;
	private final Object data;

	public RemoteSharedObjectEvent(ID senderObj, ID remoteCont, Object data) {
		super();
		this.senderSharedObjectID = senderObj;
		this.remoteContainerID = remoteCont;
		this.data = data;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.api.events.ISharedObjectEvent#getSenderSharedObject()
	 */
	public ID getSenderSharedObjectID() {
		return senderSharedObjectID;
	}

	public ID getRemoteContainerID() {
		return remoteContainerID;
	}

	public Event getEvent() {
		return this;
	}

	public Object getData() {
		return data;
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("RemoteSharedObjectEvent[");
		sb.append(getSenderSharedObjectID()).append(";");
		sb.append(getRemoteContainerID()).append(";");
		sb.append(getData()).append("]");
		return sb.toString();
	}
}
 No newline at end of file