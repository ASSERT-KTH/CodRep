package org.eclipse.ecf.sync;

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

package org.eclipse.ecf.sync.doc;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.sync.Activator;

/**
 *
 */
public class SerializationException extends ECFException {

	private static final long serialVersionUID = -8702959540799683251L;

	/**
	 * @param message
	 *            message associated with exception
	 */
	public SerializationException(String message) {
		this(message, null);
	}

	/**
	 * @param cause
	 *            the cause of the new exception
	 */
	public SerializationException(Throwable cause) {
		this(null, cause);
	}

	/**
	 * @param message
	 * @param cause
	 */
	public SerializationException(String message, Throwable cause) {
		this(new Status(IStatus.ERROR, Activator.PLUGIN_ID, 0, ((message == null) ? "" : message), cause)); //$NON-NLS-1$
	}

	/**
	 * @param status
	 *            the status for th
	 */
	public SerializationException(IStatus status) {
		super(status);
	}

}