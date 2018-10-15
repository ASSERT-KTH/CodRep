public String prepareEndpointAddress(IRemoteCall call, IRemoteCallable callable) {

/******************************************************************************* 
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.remoteservice.rest.client;

import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.client.*;
import org.eclipse.ecf.remoteservice.rest.identity.RestID;
import org.eclipse.ecf.remoteservice.rest.identity.RestNamespace;

/**
 * A container for REST services. 
 */
public class RestClientContainer extends AbstractClientContainer implements IRemoteServiceClientContainerAdapter {

	public RestClientContainer(RestID id) {
		super(id);
		// Set serializers
		setParameterSerializer(new StringParameterSerializer());
		setResponseDeserializer(new XMLRemoteResponseDeserializer());
	}

	protected IRemoteService createRemoteService(RemoteServiceClientRegistration registration) {
		return new RestClientService(this, registration);
	}

	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(RestNamespace.NAME);
	}

	public String prepareEndpoint(IRemoteCall call, IRemoteCallable callable) {
		String resourcePath = callable.getResourcePath();
		if (resourcePath == null || "".equals(resourcePath)) //$NON-NLS-1$
			return null;
		// if resourcePath startswith http then we use it unmodified
		if (resourcePath.startsWith("http://")) //$NON-NLS-1$
			return resourcePath;

		RestID targetContainerID = (RestID) getRemoteCallTargetID();
		String baseUriString = targetContainerID.toURI().toString();
		int length = baseUriString.length();
		char[] lastChar = new char[1];
		baseUriString.getChars(length - 1, length, lastChar, 0);
		char[] firstMethodChar = new char[1];
		resourcePath.getChars(0, 1, firstMethodChar, 0);
		if ((lastChar[0] == '/' && firstMethodChar[0] != '/') || (lastChar[0] != '/' && firstMethodChar[0] == '/'))
			return baseUriString + resourcePath;
		else if (lastChar[0] == '/' && firstMethodChar[0] == '/') {
			String tempurl = baseUriString.substring(0, length - 1);
			return tempurl + resourcePath;
		} else if (lastChar[0] != '/' && firstMethodChar[0] != '/')
			return baseUriString + "/" + resourcePath; //$NON-NLS-1$
		return null;
	}

}