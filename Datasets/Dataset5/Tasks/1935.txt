package org.eclipse.ecf.remoteservice.client;

/*******************************************************************************
* Copyright (c) 2009 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.remoteservice;

import java.util.Arrays;
import org.eclipse.core.runtime.Assert;

/**
 * @since 3.3
 */
public class RemoteCallable implements IRemoteCallable {

	protected String method;
	protected String resourcePath;
	protected IRemoteCallParameter[] defaultParameters;
	protected long defaultTimeout;
	protected IRemoteCallableRequestType requestType;

	public RemoteCallable(String method, String resourcePath, IRemoteCallParameter[] defaultParameters, IRemoteCallableRequestType requestType, long defaultTimeout) {
		this.method = method;
		Assert.isNotNull(method);
		this.resourcePath = resourcePath;
		Assert.isNotNull(resourcePath);
		this.defaultParameters = defaultParameters;
		this.requestType = requestType;
		this.defaultTimeout = defaultTimeout;
	}

	public RemoteCallable(String method, String resourcePath, IRemoteCallParameter[] defaultParameters, IRemoteCallableRequestType requestType) {
		this(method, resourcePath, defaultParameters, requestType, DEFAULT_TIMEOUT);
	}

	public String getMethod() {
		return method;
	}

	public String getResourcePath() {
		return resourcePath;
	}

	public IRemoteCallParameter[] getDefaultParameters() {
		return defaultParameters;
	}

	public IRemoteCallableRequestType getRequestType() {
		return requestType;
	}

	public long getDefaultTimeout() {
		return defaultTimeout;
	}

	public String toString() {
		StringBuffer buffer = new StringBuffer();
		buffer.append("RemoteCallable[defaultParameters="); //$NON-NLS-1$
		buffer.append(defaultParameters != null ? Arrays.asList(defaultParameters) : null);
		buffer.append(", defaultTimeout="); //$NON-NLS-1$
		buffer.append(defaultTimeout);
		buffer.append(", method="); //$NON-NLS-1$
		buffer.append(method);
		buffer.append(", requestType="); //$NON-NLS-1$
		buffer.append(requestType);
		buffer.append(", resourcePath="); //$NON-NLS-1$
		buffer.append(resourcePath);
		buffer.append("]"); //$NON-NLS-1$
		return buffer.toString();
	}
}