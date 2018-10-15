package org.eclipse.ecf.core.status;

/*******************************************************************************
 * Copyright (c) 2008 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.util;

import java.io.*;
import org.eclipse.core.runtime.*;
import org.eclipse.ecf.internal.core.ECFPlugin;
import org.eclipse.osgi.util.NLS;

public class SerializableStatus implements IStatus, Serializable {

	private static final long serialVersionUID = -1874392357776889683L;

	public static final IStatus OK_STATUS = new SerializableStatus(OK, ECFPlugin.PLUGIN_ID, OK, "ok", null); //$NON-NLS-1$
	public static final IStatus CANCEL_STATUS = new SerializableStatus(CANCEL, ECFPlugin.PLUGIN_ID, 1, "", null); //$NON-NLS-1$

	/**
	 * The severity. One of
	 * <ul>
	 * <li><code>CANCEL</code></li>
	 * <li><code>ERROR</code></li>
	 * <li><code>WARNING</code></li>
	 * <li><code>INFO</code></li>
	 * <li>or <code>OK</code> (0)</li>
	 * </ul>
	 */
	private int severity = OK;

	/**
	 * Unique identifier of plug-in.
	 */
	private String pluginId;

	/**
	 * Plug-in-specific status code.
	 */
	private int code;

	/**
	 * Message, localized to the current locale.
	 */
	private String message;

	/**
	 * Wrapped exception, or <code>null</code> if none.
	 */
	private Throwable exception = null;

	/**
	 * Constant to avoid generating garbage.
	 */
	private static final IStatus[] theEmptyStatusArray = new IStatus[0];

	public SerializableStatus(IStatus status) {
		setSeverity(status.getSeverity());
		setPlugin(status.getPlugin());
		setCode(status.getCode());
		setMessage(status.getMessage());
		setException(status.getException());
	}

	public SerializableStatus(int severity, String pluginId, int code, String message, Throwable exception) {
		setSeverity(severity);
		setPlugin(pluginId);
		setCode(code);
		setMessage(message);
		setException(exception);
	}

	public SerializableStatus(int severity, String pluginId, String message, Throwable exception) {
		setSeverity(severity);
		setPlugin(pluginId);
		setMessage(message);
		setException(exception);
		setCode(OK);
	}

	public SerializableStatus(int severity, String pluginId, String message) {
		setSeverity(severity);
		setPlugin(pluginId);
		setMessage(message);
		setCode(OK);
		setException(null);
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public IStatus[] getChildren() {
		return theEmptyStatusArray;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public int getCode() {
		return code;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public Throwable getException() {
		return exception;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public String getMessage() {
		return message;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public String getPlugin() {
		return pluginId;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public int getSeverity() {
		return severity;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public boolean isMultiStatus() {
		return false;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public boolean isOK() {
		return severity == OK;
	}

	/*
	 * (Intentionally not javadoc'd) Implements the corresponding method on
	 * <code>IStatus</code>.
	 */
	public boolean matches(int severityMask) {
		return (severity & severityMask) != 0;
	}

	/**
	 * Sets the status code.
	 * 
	 * @param code
	 *            the plug-in-specific status code, or <code>OK</code>
	 */
	protected void setCode(int code) {
		this.code = code;
	}

	/**
	 * Sets the exception.
	 * 
	 * @param exception
	 *            a low-level exception, or <code>null</code> if not applicable
	 */
	protected void setException(Throwable exception) {
		this.exception = checkForSerializable(exception);
	}

	private Throwable checkForSerializable(Throwable exception2) {
		ObjectOutputStream oos = null;
		try {
			oos = new ObjectOutputStream(new ByteArrayOutputStream());
			oos.writeObject(exception2);
		} catch (IOException e) {
			ECFPlugin.getDefault().log(new Status(IStatus.WARNING, ECFPlugin.PLUGIN_ID, IStatus.WARNING, NLS.bind("Exception {0} could not be serialized for SerializableStatus", exception2), e)); //$NON-NLS-1$
			// In this case, we'll create a new exception that can be serialized
			return createNewExceptionFor(exception2);
		} finally {
			try {
				if (oos != null)
					oos.close();
			} catch (IOException e) {
				// do nothing
			}
		}
		return exception2;
	}

	private Throwable createNewExceptionFor(Throwable exception2) {
		Exception re = new Exception(exception2.getMessage());
		// setStackTrace not in Foundation 1.1 as per
		// bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=261781
		// re.setStackTrace(exception2.getStackTrace());
		return re;
	}

	/**
	 * Sets the message. If null is passed, message is set to an empty string.
	 * 
	 * @param message
	 *            a human-readable message, localized to the current locale
	 */
	protected void setMessage(String message) {
		if (message == null)
			this.message = ""; //$NON-NLS-1$
		else
			this.message = message;
	}

	/**
	 * Sets the plug-in id.
	 * 
	 * @param pluginId
	 *            the unique identifier of the relevant plug-in
	 */
	protected void setPlugin(String pluginId) {
		Assert.isLegal(pluginId != null && pluginId.length() > 0);
		this.pluginId = pluginId;
	}

	/**
	 * Sets the severity.
	 * 
	 * @param severity
	 *            the severity; one of <code>OK</code>, <code>ERROR</code>,
	 *            <code>INFO</code>, <code>WARNING</code>, or
	 *            <code>CANCEL</code>
	 */
	protected void setSeverity(int severity) {
		Assert.isLegal(severity == OK || severity == ERROR || severity == WARNING || severity == INFO || severity == CANCEL);
		this.severity = severity;
	}

	/**
	 * Returns a string representation of the status, suitable for debugging
	 * purposes only.
	 */
	public String toString() {
		StringBuffer buf = new StringBuffer();
		buf.append("SerializableStatus "); //$NON-NLS-1$
		if (severity == OK) {
			buf.append("OK"); //$NON-NLS-1$
		} else if (severity == ERROR) {
			buf.append("ERROR"); //$NON-NLS-1$
		} else if (severity == WARNING) {
			buf.append("WARNING"); //$NON-NLS-1$
		} else if (severity == INFO) {
			buf.append("INFO"); //$NON-NLS-1$
		} else if (severity == CANCEL) {
			buf.append("CANCEL"); //$NON-NLS-1$
		} else {
			buf.append("severity="); //$NON-NLS-1$
			buf.append(severity);
		}
		buf.append(": "); //$NON-NLS-1$
		buf.append(pluginId);
		buf.append(" code="); //$NON-NLS-1$
		buf.append(code);
		buf.append(' ');
		buf.append(message);
		buf.append(' ');
		buf.append(exception);
		return buf.toString();
	}
}