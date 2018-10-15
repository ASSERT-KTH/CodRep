String str = endpointDescription.getContainerID().getName();

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import java.net.InetAddress;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.discovery.IDiscoveryAdvertiser;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;

public abstract class AbstractServiceInfoFactory extends
		AbstractMetadataFactory implements IServiceInfoFactory {

	protected Map<ServiceInfoKey, IServiceInfo> serviceInfos = new HashMap();

	protected class ServiceInfoKey {
		private EndpointDescription endpointDescription;
		private Namespace discoveryNamespace;
		private int hashCode = 7;

		public ServiceInfoKey(EndpointDescription endpointDescription,
				Namespace discoveryNamespace) {
			this.endpointDescription = endpointDescription;
			this.discoveryNamespace = discoveryNamespace;
			this.hashCode = 31 * this.hashCode + endpointDescription.hashCode();
			this.hashCode = 31 * this.hashCode + discoveryNamespace.hashCode();
		}

		public boolean equals(Object other) {
			if (other == null)
				return false;
			if (!(other instanceof ServiceInfoKey))
				return false;
			ServiceInfoKey otherKey = (ServiceInfoKey) other;
			return (this.endpointDescription
					.equals(otherKey.endpointDescription) && this.discoveryNamespace
					.equals(otherKey.discoveryNamespace));
		}

		public int hashCode() {
			return hashCode;
		}
	}

	public IServiceInfo createServiceInfoForDiscovery(
			IDiscoveryAdvertiser advertiser,
			EndpointDescription endpointDescription) {
		try {
			Namespace advertiserNamespace = advertiser.getServicesNamespace();
			ServiceInfoKey key = new ServiceInfoKey(endpointDescription,
					advertiserNamespace);
			IServiceInfo existingServiceInfo = null;
			synchronized (serviceInfos) {
				existingServiceInfo = serviceInfos.get(key);
				// If it's already there, then we return null
				if (existingServiceInfo != null)
					return null;
				IServiceTypeID serviceTypeID = createServiceTypeID(
						endpointDescription, advertiser);
				String serviceName = createServiceName(endpointDescription,
						advertiser, serviceTypeID);
				URI uri = createURI(endpointDescription, advertiser,
						serviceTypeID, serviceName);
				IServiceProperties serviceProperties = createServiceProperties(
						endpointDescription, advertiser, serviceTypeID,
						serviceName, uri);
				IServiceInfo newServiceInfo = createServiceInfo(uri, serviceName, serviceTypeID, serviceProperties);
				// put into map using key
				serviceInfos.put(key, newServiceInfo);
				return newServiceInfo;
			}
		} catch (Exception e) {
			logError(
					"createServiceInfoForDiscovery",
					"Exception creating service info for endpointDescription="
							+ endpointDescription + ",advertiser=" + advertiser,
					e);
			return null;
		}
	}

	protected IServiceInfo createServiceInfo(URI uri, String serviceName, IServiceTypeID serviceTypeID, IServiceProperties serviceProperties) {
		return new ServiceInfo(uri, serviceName,
				serviceTypeID, serviceProperties);
	}
	
	protected IServiceProperties createServiceProperties(
			EndpointDescription endpointDescription,
			IDiscoveryAdvertiser advertiser, IServiceTypeID serviceTypeID,
			String serviceName, URI uri) {
		ServiceProperties result = new ServiceProperties();
		encodeServiceProperties(endpointDescription, result);
		return result;
	}

	protected URI createURI(EndpointDescription endpointDescription,
			IDiscoveryAdvertiser advertiser, IServiceTypeID serviceTypeID,
			String serviceName) throws URISyntaxException {
		String path = "/" + serviceName;
		String str = endpointDescription.getID().getName();
		URI uri = null;
		while (true) {
			try {
				uri = new URI(str);
				if (uri.getHost() != null) {
					break;
				} else {
					final String rawSchemeSpecificPart = uri
							.getRawSchemeSpecificPart();
					// make sure we break eventually
					if (str.equals(rawSchemeSpecificPart)) {
						uri = null;
						break;
					} else {
						str = rawSchemeSpecificPart;
					}
				}
			} catch (URISyntaxException e) {
				uri = null;
				break;
			}
		}
		String scheme = RemoteConstants.SERVICE_TYPE;
		int port = 32565;
		if (uri != null) {
			port = uri.getPort();
			if (port == -1)
				port = 32565;
		}
		String host = null;
		if (uri != null) {
			host = uri.getHost();
		} else {
			try {
				host = InetAddress.getLocalHost().getHostAddress();
			} catch (Exception e) {
				logInfo("createURI", //$NON-NLS-1$
						"failed to get local host adress, falling back to \'localhost\'.", e); //$NON-NLS-1$
				host = "localhost"; //$NON-NLS-1$
			}
		}
		return new URI(scheme, null, host, port, path, null, null);
	}

	protected String createServiceName(EndpointDescription endpointDescription,
			IDiscoveryAdvertiser advertiser, IServiceTypeID serviceTypeID) {
		// First create unique default name
		String defaultServiceName = createDefaultServiceName(
				endpointDescription, advertiser, serviceTypeID);
		// Look for service name that was explicitly set
		String serviceName = getStringWithDefault(
				endpointDescription.getProperties(),
				RemoteConstants.DISCOVERY_SERVICE_NAME, defaultServiceName);
		return serviceName;
	}

	protected String createDefaultServiceName(
			EndpointDescription endpointDescription,
			IDiscoveryAdvertiser advertiser, IServiceTypeID serviceTypeID) {
		return RemoteConstants.DISCOVERY_DEFAULT_SERVICE_NAME_PREFIX
				+ IDFactory.getDefault().createGUID().getName();
	}

	protected IServiceTypeID createServiceTypeID(
			EndpointDescription endpointDescription,
			IDiscoveryAdvertiser advertiser) {
		Map props = endpointDescription.getProperties();
		String[] scopes = getStringArrayWithDefault(props,
				RemoteConstants.DISCOVERY_SCOPE, IServiceTypeID.DEFAULT_SCOPE);
		String[] protocols = getStringArrayWithDefault(props,
				RemoteConstants.DISCOVERY_PROTOCOLS,
				IServiceTypeID.DEFAULT_SCOPE);
		String namingAuthority = getStringWithDefault(props,
				RemoteConstants.DISCOVERY_NAMING_AUTHORITY,
				IServiceTypeID.DEFAULT_NA);
		return ServiceIDFactory.getDefault().createServiceTypeID(
				advertiser.getServicesNamespace(),
				new String[] { RemoteConstants.SERVICE_TYPE }, scopes,
				protocols, namingAuthority);
	}

	public IServiceInfo removeServiceInfoForUndiscovery(
			IDiscoveryAdvertiser advertiser,
			EndpointDescription endpointDescription) {
		Namespace advertiserNamespace = advertiser.getServicesNamespace();
		ServiceInfoKey key = new ServiceInfoKey(endpointDescription,
				advertiserNamespace);
		synchronized (serviceInfos) {
			return serviceInfos.remove(key);
		}
	}

	public void close() {
		synchronized (serviceInfos) {
			serviceInfos.clear();
		}
		super.close();
	}
}