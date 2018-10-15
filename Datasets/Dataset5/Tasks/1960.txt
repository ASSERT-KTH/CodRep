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

import org.eclipse.ecf.core.util.Event;

/**
 * Connection event super class.
 * 
 */
public class ConnectionEvent implements Event {
	private static final long serialVersionUID = 3257290214476362291L;

	Object data = null;

	IConnection connection = null;

	public ConnectionEvent(IConnection source, Object data) {
		this.connection = source;
		this.data = data;
	}

	public IConnection getConnection() {
		return connection;
	}

	public Object getData() {
		return data;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("ConnectionEvent[");
		buf.append("conn=").append(getConnection()).append(";").append("data=")
				.append(getData());
		buf.append("]");
		return buf.toString();
	}

}
 No newline at end of file