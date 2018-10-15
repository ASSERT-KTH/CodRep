package org.eclipse.ecf.core.sharedobject;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core;

import org.eclipse.ecf.core.util.ECFException;

public class SharedObjectConnectException extends ECFException {
	private static final long serialVersionUID = 3256440287659570228L;

	public SharedObjectConnectException() {
		super();
	}

	public SharedObjectConnectException(String arg0) {
		super(arg0);
	}

	public SharedObjectConnectException(String msg, Throwable cause) {
		super(msg, cause);
	}

	public SharedObjectConnectException(Throwable cause) {
		super(cause);
	}
}
 No newline at end of file