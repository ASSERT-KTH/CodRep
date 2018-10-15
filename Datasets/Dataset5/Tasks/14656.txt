final String targetStr = new String(targetBytes);

/*******************************************************************************
 * Copyright (c) 2009 Markus Alexander Kuppe, Composent, Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.discovery;

import java.net.URI;
import java.util.Arrays;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription;
import org.eclipse.ecf.osgi.services.discovery.RemoteServicePublication;

public class RemoteServiceEndpointDescriptionImpl extends
		RemoteServiceEndpointDescription {

	private final ID endpointId;
	private final IServiceID serviceId;
	private ID targetId = null;
	private int hashCode = 7;

	public RemoteServiceEndpointDescriptionImpl(IServiceInfo serviceInfo) {
		super(((ServiceProperties) serviceInfo.getServiceProperties())
				.asProperties());
		this.serviceId = serviceInfo.getServiceID();

		// create the endpoint id
		IServiceProperties serviceProperties = serviceInfo
				.getServiceProperties();
		final byte[] endpointBytes = serviceProperties
				.getPropertyBytes(RemoteServicePublication.ENDPOINT_CONTAINERID);
		if (endpointBytes == null)
			throw new IDCreateException(
					"ServiceEndpointDescription endpointBytes cannot be null");
		final String endpointStr = new String(endpointBytes);
		final String namespaceStr = serviceProperties
				.getPropertyString(RemoteServicePublication.ENDPOINT_CONTAINERID_NAMESPACE);
		if (namespaceStr == null) {
			throw new IDCreateException(
					"ServiceEndpointDescription namespaceStr cannot be null");
		}
		endpointId = IDFactory.getDefault().createID(namespaceStr, endpointStr);

		// create the target id, if it's there
		final byte[] targetBytes = serviceProperties
				.getPropertyBytes(RemoteServicePublication.TARGET_CONTAINERID);
		// If this is null, we're ok with it
		if (targetBytes != null) {
			final String targetStr = new String(endpointBytes);
			String targetNamespaceStr = serviceProperties
					.getPropertyString(RemoteServicePublication.TARGET_CONTAINERID_NAMESPACE);
			if (targetNamespaceStr == null)
				targetNamespaceStr = namespaceStr;
			targetId = IDFactory.getDefault().createID(targetNamespaceStr,
					targetStr);
		}

		// Get location and compute hashCode
		URI serviceLocation = this.serviceId.getLocation();
		long rsId = this.getRemoteServiceId();
		hashCode = 31 * hashCode + (int) (rsId ^ (rsId >>> 32));
		hashCode = 31 * hashCode + serviceLocation.hashCode();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getECFEndpointID()
	 */
	public ID getEndpointAsID() throws IDCreateException {
		return endpointId;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.osgi.services.discovery.RemoteServiceEndpointDescription
	 * #getECFTargetID()
	 */
	public ID getConnectTargetID() {
		return targetId;
	}

	public int hashCode() {
		return hashCode;
	}

	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		RemoteServiceEndpointDescriptionImpl other = (RemoteServiceEndpointDescriptionImpl) obj;
		return this.serviceId.getLocation().equals(
				other.serviceId.getLocation())
				&& getRemoteServiceId() == other.getRemoteServiceId();
	}

	public IServiceID getServiceID() {
		return serviceId;
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("ServiceEndpointDescriptionImpl["); //$NON-NLS-1$
		sb.append(";providedInterfaces=").append(getProvidedInterfaces()); //$NON-NLS-1$
		String[] supportedConfigs = getSupportedConfigs();
		sb.append(";supportedConfigTypes").append(
				(supportedConfigs == null) ? "null" : Arrays.asList(
						supportedConfigs).toString());
		String[] serviceIntents = getServiceIntents();
		sb.append(";serviceIntents").append(
				(serviceIntents == null) ? "null" : Arrays.asList(
						serviceIntents).toString());
		sb.append(";location=").append(getLocation()); //$NON-NLS-1$
		sb.append(";remoteServiceId=").append(getRemoteServiceId()); //$NON-NLS-1$
		sb.append(";discoveryServiceID=").append(getServiceID()); //$NON-NLS-1$
		sb.append(";endpointID=").append(getEndpointID()); //$NON-NLS-1$
		sb.append(";endpointAsID=").append(getEndpointAsID()); //$NON-NLS-1$
		sb.append(";connectTargetID=").append(getConnectTargetID()); //$NON-NLS-1$
		sb.append(";remoteServicesFilter=").append(getRemoteServicesFilter()); //$NON-NLS-1$
		sb.append(";props=").append(getProperties()).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
		return sb.toString();
	}

}