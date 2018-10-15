package org.eclipse.ecf.provider.comm;

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
package org.eclipse.ecf.core.comm;

/**
 * Asynchronous connection event class. Extends ConnectionEvent
 * 
 */
public class AsynchEvent extends ConnectionEvent {
	private static final long serialVersionUID = 3618136762325873465L;

	public AsynchEvent(IAsynchConnection conn, Object data) {
		super(conn, data);
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("AsynchEvent[");
		buf.append("conn=").append(getConnection()).append(";");
		buf.append("data=").append(getData()).append("]");
		return buf.toString();
	}

}
 No newline at end of file