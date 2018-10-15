public long getLookupTimeout() {

/*******************************************************************************
 * Copyright (c) 2009 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.discovery;

import org.eclipse.ecf.discovery.ServiceProperties;

import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.ECFServicePublication;

import org.eclipse.ecf.core.identity.IDCreateException;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.discovery.IServiceInfo;

import org.eclipse.ecf.osgi.services.discovery.ECFServiceEndpointDescription;

public class ECFServiceEndpointDescriptionImpl extends
		ECFServiceEndpointDescription {

	private static final long DEFAULT_FUTURE_TIMEOUT = new Long(System
			.getProperty("ecf.rs.lookup.timeout", new Long(30000).toString()))
			.longValue();

	private final ID endpointId;
	private final IServiceID serviceId;
	
	public ECFServiceEndpointDescriptionImpl(IServiceInfo serviceInfo) {
		super(((ServiceProperties)serviceInfo.getServiceProperties()).asProperties());
		this.serviceId = serviceInfo.getServiceID();

		// create the endpoint id
		IServiceProperties serviceProperties = serviceInfo.getServiceProperties();
		final byte[] endpointBytes = 
			serviceProperties.getPropertyBytes(ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID);
		if (endpointBytes == null)
			throw new IDCreateException(
					"ServiceEndpointDescription endpointBytes cannot be null");
		final String endpointStr = new String(endpointBytes);
		final String namespaceStr = 
			serviceProperties.getPropertyString(ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID_NAMESPACE);
		if (namespaceStr == null) {
			throw new IDCreateException(
			"ServiceEndpointDescription namespaceStr cannot be null");
		}
		endpointId = IDFactory.getDefault().createID(namespaceStr,
				endpointStr);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.osgi.services.discovery.ECFServiceEndpointDescription#getECFEndpointID()
	 */
	public ID getECFEndpointID() throws IDCreateException {
		return endpointId;
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.osgi.services.discovery.ECFServiceEndpointDescription#getFutureTimeout()
	 */
	public long getFutureTimeout() {
		//TODO get from service properties?
		return DEFAULT_FUTURE_TIMEOUT;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#hashCode()
	 */
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((serviceId == null) ? 0 : serviceId.hashCode());
		return result;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#equals(java.lang.Object)
	 */
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		ECFServiceEndpointDescriptionImpl other = (ECFServiceEndpointDescriptionImpl) obj;
		if (serviceId == null) {
			if (other.serviceId != null)
				return false;
		} else if (!serviceId.equals(other.serviceId))
			return false;
		return true;
	}
}