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

public class SharedObjectAddException extends ECFException {
	private static final long serialVersionUID = 3257853198755705913L;

	public SharedObjectAddException() {
		super();
	}

	public SharedObjectAddException(String arg0) {
		super(arg0);
	}

	public SharedObjectAddException(String msg, Throwable cause) {
		super(msg, cause);
	}

	public SharedObjectAddException(Throwable cause) {
		super(cause);
	}
}
 No newline at end of file