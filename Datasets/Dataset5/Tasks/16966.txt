final StringBuffer buf = new StringBuffer("Response[");

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.remoteservice.generic;

import java.io.Serializable;

public class Response implements Serializable {

	private static final long serialVersionUID = 634820397523983872L;

	long requestId;

	Object response;

	Throwable exception;

	public Response(long requestId, Object response) {
		this.requestId = requestId;
		this.response = response;
	}

	public Response(long requestId, Throwable exception) {
		this.requestId = requestId;
		this.exception = exception;
	}

	public long getRequestId() {
		return requestId;
	}

	public Object getResponse() {
		return response;
	}

	public boolean hadException() {
		return (exception != null);
	}

	public Throwable getException() {
		return exception;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("Response[");
		buf.append("requestId=").append(requestId).append(";response=").append(
				response).append(";exception=").append(exception).append("]");
		return buf.toString();
	}
}