private final long duration;

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

/**
 * Timeout exception thrown when timeout occurs
 * 
 */
public class TimeoutException extends Exception {

	private static final long serialVersionUID = -3198307514925924297L;

	public final long duration;

	public TimeoutException(long time) {
		duration = time;
	}

	public TimeoutException(String message, long time) {
		super(message);
		this.duration = time;
	}

	public long getDuration() {
		return duration;
	}
}
 No newline at end of file