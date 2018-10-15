((message == null) ? "" : message), cause)); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.util;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.ecf.internal.core.identity.Activator;

public class ECFException extends CoreException {
	private static final long serialVersionUID = 3256440309134406707L;

	public ECFException() {
		this(null, null);
	}

	/**
	 * @param message
	 *            message associated with exception
	 */
	public ECFException(String message) {
		this(message, null);
	}

	/**
	 * @param cause
	 *            the cause of the new exception
	 */
	public ECFException(Throwable cause) {
		this(null, cause);
	}

	/**
	 * @param message
	 * @param cause
	 */
	public ECFException(String message, Throwable cause) {
		this(new Status(IStatus.ERROR, Activator.PLUGIN_ID, 0,
				((message == null) ? "" : message), cause));
	}

	/**
	 * @param status
	 *            the status for th
	 */
	public ECFException(IStatus status) {
		super(status);
	}
}
 No newline at end of file