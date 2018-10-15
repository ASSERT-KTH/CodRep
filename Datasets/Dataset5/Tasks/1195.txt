serviceName = serviceID.getServiceName();

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
/**
 * 
 */
package org.eclipse.ecf.internal.osgi.services.distribution;

import java.util.Collection;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.ECFServicePublication;
import org.eclipse.ecf.osgi.services.discovery.ServiceEndpointDescriptionImpl;

class ServiceEndpointDescriptionHelper {
	private static final long DEFAULT_FUTURE_TIMEOUT = 30000;

	private final ServiceEndpointDescriptionImpl description;
	private final ID localDiscoveryContainerID;
	private final ID originalLocalDiscoveryContainerID;
	private final IServiceID serviceID;
	private final String serviceName;
	private ID endpointID;

	public ServiceEndpointDescriptionHelper(ServiceEndpointDescriptionImpl d)
			throws NullPointerException {
		description = d;
		// Get ECF discovery container ID...if not found there is a problem
		localDiscoveryContainerID = description.getLocalDiscoveryContainerID();
		if (localDiscoveryContainerID == null)
			throw new NullPointerException(
					"ServiceEndpointDescription localDiscoveryContainerID cannot be null");
		originalLocalDiscoveryContainerID = description
				.getOriginalLocalDiscoveryContainerID();
		if (originalLocalDiscoveryContainerID == null)
			throw new NullPointerException(
					"ServiceEndpointDescription originalLocalDiscoveryContainerID cannot be null");
		// Get serviceName from description
		serviceID = description.getServiceID();
		if (serviceID == null)
			throw new NullPointerException(
					"ServiceEndpointDescription serviceID cannot be null");
		serviceName = serviceID.getName();
		if (serviceName == null)
			throw new NullPointerException(
					"ServiceEndpointDescription serviceName is null");
	}

	public ServiceEndpointDescriptionImpl getDescription() {
		return description;
	}

	public ID getLocalDiscoveryContainerID() {
		return localDiscoveryContainerID;
	}

	public IServiceID getServiceID() {
		return serviceID;
	}

	public String getServiceName() {
		return serviceName;
	}

	public Collection getProvidedInterfaces() {
		Collection c = description.getProvidedInterfaces();
		if (c == null)
			throw new NullPointerException(
					"ServiceEndpointDescription providedInterfaces cannot be null");
		return c;
	}

	public Long getRemoteServiceID() throws NullPointerException {
		String longStr = (String) description
				.getProperty(org.eclipse.ecf.remoteservice.Constants.SERVICE_ID);
		if (longStr == null)
			throw new NullPointerException(
					"ServiceEndpointDescriptoin remote service ID cannot be null");
		return new Long(longStr);
	}

	public synchronized ID getEndpointID() throws IDCreateException {
		if (endpointID == null) {
			byte[] endpointBytes = description
					.getPropertyBytes(ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID);
			if (endpointBytes == null)
				throw new IDCreateException(
						"ServiceEndpointDescription endpointBytes cannot be null");
			String endpointStr = new String(endpointBytes);
			String namespaceStr = description
					.getPropertyString(ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID_NAMESPACE);
			if (namespaceStr == null)
				throw new IDCreateException(
						"ServiceEndpointDescription namespaceStr cannot be null");
			endpointID = IDFactory.getDefault().createID(namespaceStr,
					endpointStr);
		}
		return endpointID;
	}

	public long getFutureTimeout() {
		return DEFAULT_FUTURE_TIMEOUT;
	}

}
 No newline at end of file