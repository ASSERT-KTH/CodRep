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

public class SharedObjectContainerInitException extends ECFException {
	private static final long serialVersionUID = 3690189958417888565L;

	public SharedObjectContainerInitException() {
		super();
	}

	public SharedObjectContainerInitException(String message) {
		super(message);
	}

	public SharedObjectContainerInitException(Throwable cause) {
		super(cause);
	}

	public SharedObjectContainerInitException(String message, Throwable cause) {
		super(message, cause);
	}
}
 No newline at end of file