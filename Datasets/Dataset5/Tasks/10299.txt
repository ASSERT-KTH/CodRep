public class ServicePublicationHandler implements ServiceTrackerCustomizer, Discovery {

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.discovery;

import java.io.Serializable;
import java.net.*;
import java.util.*;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.util.ECFRuntimeException;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.discovery.*;
import org.eclipse.ecf.discovery.identity.*;
import org.eclipse.ecf.osgi.services.discovery.ECFServicePublication;
import org.eclipse.ecf.remoteservice.Constants;
import org.osgi.framework.ServiceReference;
import org.osgi.service.discovery.*;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public class ServicePublicationHandler implements ServiceTrackerCustomizer {

	private Map serviceInfos = Collections.synchronizedMap(new HashMap());

	private final IServiceListener serviceListener = new IServiceListener() {
		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceListener#serviceDiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceDiscovered(IServiceEvent anEvent) {
			handleServiceDiscovered(anEvent);
		}

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceListener#serviceUndiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceUndiscovered(IServiceEvent anEvent) {
			handleServiceUndiscovered(anEvent);
		}
	};

	private void handleServiceDiscovered(IServiceEvent event) {
		IServiceInfo serviceInfo = event.getServiceInfo();
		IServiceID serviceID = serviceInfo.getServiceID();
		trace("handleOSGIServiceDiscovered", " serviceInfo=" + serviceInfo); //$NON-NLS-1$ //$NON-NLS-2$
		if (matchServiceID(serviceID)) {
			trace("handleOSGIServiceDiscovered matched", " serviceInfo=" + serviceInfo); //$NON-NLS-1$ //$NON-NLS-2$
			DiscoveredServiceTracker[] discoveredTrackers = findMatchingDiscoveredServiceTrackers(serviceInfo);
			if (discoveredTrackers != null) {
				for (int i = 0; i < discoveredTrackers.length; i++) {
					discoveredTrackers[i]
							.serviceChanged(new DiscoveredServiceNotificationImpl(
									DiscoveredServiceNotification.AVAILABLE,
									serviceInfo));
				}
			}
		}
	}

	private void handleServiceUndiscovered(IServiceEvent event) {
		IServiceInfo serviceInfo = event.getServiceInfo();
		IServiceID serviceID = serviceInfo.getServiceID();
		if (matchServiceID(serviceID)) {
			trace("handleOSGIServiceUndiscovered", " serviceInfo=" + serviceInfo); //$NON-NLS-1$ //$NON-NLS-2$
			DiscoveredServiceTracker[] discoveredTrackers = findMatchingDiscoveredServiceTrackers(serviceInfo);
			if (discoveredTrackers != null) {
				for (int i = 0; i < discoveredTrackers.length; i++) {
					discoveredTrackers[i]
							.serviceChanged(new DiscoveredServiceNotificationImpl(
									DiscoveredServiceNotification.UNAVAILABLE,
									serviceInfo));
				}
			}
		}
	}

	private DiscoveredServiceTracker[] findMatchingDiscoveredServiceTrackers(
			IServiceInfo serviceInfo) {
		ServiceReference[] sourceTrackers = Activator.getDefault()
				.getDiscoveredServiceTrackerReferences();
		if (sourceTrackers == null)
			return null;
		List matchingTrackers = new ArrayList();
		for (int i = 0; i < sourceTrackers.length; i++) {
			if (matchWithDiscoveredServiceInfo(sourceTrackers[i], serviceInfo))
				matchingTrackers.add(Activator.getDefault().getContext()
						.getService(sourceTrackers[i]));
		}
		return (DiscoveredServiceTracker[]) matchingTrackers
				.toArray(new DiscoveredServiceTracker[] {});
	}

	private boolean matchWithDiscoveredServiceInfo(
			ServiceReference serviceReference, IServiceInfo serviceInfo) {
		// TODO Auto-generated method stub
		// XXX for now match everything. See RFC119
		return true;
	}

	private boolean matchServiceID(IServiceID serviceId) {
		if (Arrays.asList(serviceId.getServiceTypeID().getServices()).contains(
				ECFServicePublication.SERVICE_TYPE))
			return true;
		return false;
	}

	private IServiceInfo addServiceInfo(ServiceReference sr, IServiceInfo si) {
		return (IServiceInfo) serviceInfos.put(sr, si);
	}

	private IServiceInfo removeServiceInfo(ServiceReference sr) {
		return (IServiceInfo) serviceInfos.remove(sr);
	}

	/* (non-Javadoc)
	 * @see org.osgi.util.tracker.ServiceTrackerCustomizer#addingService(org.osgi.framework.ServiceReference)
	 */
	public Object addingService(ServiceReference reference) {
		handleServicePublication(reference);
		return Activator.getDefault().getContext().getService(reference);
	}

	/**
	 * @param reference
	 */
	private void handleServicePublication(ServiceReference reference) {

		// Get required service RFC 119 property "service.interface", which
		// should be a
		// Collection of Strings
		Collection svcInterfaces = ServicePropertyUtils.getCollectionProperty(
				reference, ServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME);
		// If it's not there, then we ignore this ServicePublication and return
		if (svcInterfaces == null) {
			logError(
					"handleServicePublication", //$NON-NLS-1$
					"ignoring " //$NON-NLS-1$
							+ reference
							+ ". ServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME not set", //$NON-NLS-1$
					null);
			return;
		}
		IServiceProperties discoveryServiceProperties = new ServiceProperties();
		discoveryServiceProperties.setPropertyString(
				ServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME,
				ServicePropertyUtils.createStringFromCollection(svcInterfaces));

		// We also use the optional RFC 119 property PROP_KEY_SERVICE_PROPERTIES
		Map servicePublicationServiceProperties = ServicePropertyUtils
				.getMapProperty(reference,
						ServicePublication.PROP_KEY_SERVICE_PROPERTIES);
		if (servicePublicationServiceProperties == null) {
			logError(
					"handleServicePublication", //$NON-NLS-1$
					"ignoring " //$NON-NLS-1$
							+ reference
							+ ". ServicePublication.PROP_KEY_SERVICE_PROPERTIES not set", //$NON-NLS-1$
					null);
			return;
		}
		// Add them

		addPropertiesToDiscoveryServiceProperties(discoveryServiceProperties,
				servicePublicationServiceProperties);

		// See EventHookImpl.getServicePublicationProperties()
		// Get and then serialize and set
		// ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID
		ID endpointContainerID = (ID) reference
				.getProperty(ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID);
		if (endpointContainerID == null) {
			logError(
					"handleServicePublication", //$NON-NLS-1$
					"ignoring " //$NON-NLS-1$
							+ reference
							+ ". ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID not set", //$NON-NLS-1$
					null);
			return;
		}
		// Add endpoint container id.toExternalForm().getBytes...so AS byte []
		discoveryServiceProperties.setPropertyBytes(
				ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID,
				endpointContainerID.toExternalForm().getBytes());

		// Add container id namespace name
		String namespace = endpointContainerID.getNamespace().getName();
		discoveryServiceProperties.setPropertyString(
				ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID_NAMESPACE,
				namespace);

		// remote service namespace
		String rsnamespace = ServicePropertyUtils.getStringProperty(reference,
				Constants.SERVICE_NAMESPACE);
		if (rsnamespace == null) {
			logError("handleServicePublication", "ignoring " + reference //$NON-NLS-1$ //$NON-NLS-2$
					+ ". Constants.SERVICE_NAMESPACE not set", null); //$NON-NLS-1$
			return;
		}
		discoveryServiceProperties.setPropertyString(
				Constants.SERVICE_NAMESPACE, rsnamespace);

		// remote service id

		Long remoteServiceID = (Long) reference
				.getProperty(Constants.SERVICE_ID);
		if (remoteServiceID == null) {
			logError("handleServicePublication", "ignoring " + reference //$NON-NLS-1$ //$NON-NLS-2$
					+ ". Constants.SERVICE_ID not set", null); //$NON-NLS-1$
			return;
		}
		discoveryServiceProperties.setProperty(Constants.SERVICE_ID,
				remoteServiceID);

		IServiceInfo svcInfo = null;
		try {
			IServiceTypeID serviceTypeID = createServiceTypeID(servicePublicationServiceProperties);
			URI uri = createURI(endpointContainerID);

			String serviceName = getPropertyWithDefault(
					servicePublicationServiceProperties,
					ECFServicePublication.SERVICE_NAME_PROP,
					(ECFServicePublication.DEFAULT_SERVICE_NAME_PREFIX + remoteServiceID));

			svcInfo = new ServiceInfo(uri, serviceName, serviceTypeID,
					discoveryServiceProperties);

		} catch (IDCreateException e) {
			logError("handleServicePublication", //$NON-NLS-1$
					"Exception creating serviceID", e); //$NON-NLS-1$
			return;
		} catch (URISyntaxException e) {
			logError("handleServicePublication", "Exception creating URI", e); //$NON-NLS-1$ //$NON-NLS-2$
			return;
		}
		synchronized (serviceInfos) {
			try {
				trace("publishService", "publishing serviceReference=" //$NON-NLS-1$ //$NON-NLS-2$
						+ reference + ", svcInfo=" + svcInfo); //$NON-NLS-1$
				getAdvertiser().registerService(svcInfo);
				addServiceInfo(reference, svcInfo);
			} catch (ECFRuntimeException e) {
				logError("publishService", "cannot register service", e); //$NON-NLS-1$ //$NON-NLS-2$
			}
		}
	}

	private void logError(String method, String message, Throwable t) {
		Activator.getDefault().log(
				new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR,
						method + ":" + message, t)); //$NON-NLS-1$
		Trace.catching(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_CATCHING,
				this.getClass(), method + ":" + message, t); //$NON-NLS-1$
	}

	private URI createURI(ID endpointContainerID) throws URISyntaxException {
		boolean done = false;
		URI uri = null;
		String str = endpointContainerID.getName();
		while (!done) {
			try {
				uri = new URI(str);
				if (!uri.isOpaque()) {
					done = true;
				} else {
					str = uri.getRawSchemeSpecificPart();
				}
			} catch (URISyntaxException e) {
				done = true;
			}
		}
		String scheme = ECFServicePublication.SERVICE_TYPE;
		int port = 32565;
		if (uri != null) {
			port = uri.getPort();
			if (port == -1)
				port = 32565;
		}
		String host = null;
		try {
			host = InetAddress.getLocalHost().getHostAddress();
		} catch (Exception e) {
			host = "localhost"; //$NON-NLS-1$
		}
		return new URI(scheme, null, host, port, null, null, null);
	}

	private void addPropertiesToDiscoveryServiceProperties(
			IServiceProperties discoveryServiceProperties,
			Map servicePublicationServiceProperties) {
		for (Iterator i = servicePublicationServiceProperties.keySet()
				.iterator(); i.hasNext();) {
			Object key = i.next();
			if (!(key instanceof String)) {
				trace("addPropertiesToDiscoveryServiceProperties", //$NON-NLS-1$
						"skipping non-string key " + key); //$NON-NLS-1$
				continue;
			}
			String keyStr = (String) key;
			Object val = servicePublicationServiceProperties.get(keyStr);
			if (val instanceof String) {
				discoveryServiceProperties.setPropertyString(keyStr,
						(String) val);
			} else if (val instanceof byte[]) {
				discoveryServiceProperties.setPropertyBytes(keyStr,
						(byte[]) val);
			} else if (val instanceof Serializable) {
				discoveryServiceProperties.setProperty(keyStr, val);
			}
		}
	}

	private IDiscoveryLocator locator;
	private IDiscoveryAdvertiser advertiser;

	private synchronized IDiscoveryLocator getLocator() {
		try {
			if (locator == null) {
				locator = Activator.getDefault().getLocator();
				locator.addServiceListener(serviceListener);
			}
		} catch (InterruptedException e) {
			logError("getLocator", "Cannot get IDiscoveryLocator service", e); //$NON-NLS-1$ //$NON-NLS-2$
		}
		return locator;
	}

	private synchronized IDiscoveryAdvertiser getAdvertiser() {
		try {
			if (advertiser == null) {
				advertiser = Activator.getDefault().getAdvertiser();
			}
		} catch (InterruptedException e) {
			logError("getAdvertiser", "Cannot get IDiscoveryAdvertiser", e); //$NON-NLS-1$ //$NON-NLS-2$
		}
		return advertiser;
	}

	private String getPropertyWithDefault(Map properties, String key, String def) {
		String val = (String) properties.get(key);
		return (val == null) ? def : val;
	}

	protected IServiceTypeID createServiceTypeID(
			Map servicePublicationProperties) throws IDCreateException {
		IDiscoveryLocator l = getLocator();
		if (l == null)
			return null;
		String namingAuthority = getPropertyWithDefault(
				servicePublicationProperties,
				ECFServicePublication.NAMING_AUTHORITY_PROP,
				IServiceTypeID.DEFAULT_NA);
		String scope = getPropertyWithDefault(servicePublicationProperties,
				ECFServicePublication.SCOPE_PROP,
				IServiceTypeID.DEFAULT_SCOPE[0]);
		String protocol = getPropertyWithDefault(servicePublicationProperties,
				ECFServicePublication.SERVICE_PROTOCOL_PROP,
				IServiceTypeID.DEFAULT_PROTO[0]);

		return ServiceIDFactory.getDefault().createServiceTypeID(
				l.getServicesNamespace(),
				new String[] { ECFServicePublication.SERVICE_TYPE },
				new String[] { scope }, new String[] { protocol },
				namingAuthority);
	}

	/* (non-Javadoc)
	 * @see org.osgi.util.tracker.ServiceTrackerCustomizer#modifiedService(org.osgi.framework.ServiceReference, java.lang.Object)
	 */
	public void modifiedService(ServiceReference reference, Object service) {
		unpublishService(reference);
		handleServicePublication(reference);
	}

	/* (non-Javadoc)
	 * @see org.osgi.util.tracker.ServiceTrackerCustomizer#removedService(org.osgi.framework.ServiceReference, java.lang.Object)
	 */
	public void removedService(ServiceReference reference, Object service) {
		unpublishService(reference);
	}

	private void unpublishService(ServiceReference reference) {
		IServiceInfo svcInfo = null;
		synchronized (serviceInfos) {
			try {
				svcInfo = removeServiceInfo(reference);
				if (svcInfo != null)
					getAdvertiser().unregisterService(svcInfo);
			} catch (ECFRuntimeException e) {
				logError("publishService", "Cannot unregister serviceInfo=" //$NON-NLS-1$ //$NON-NLS-2$
						+ svcInfo, e);
			}
		}
	}

	protected void trace(String methodName, String message) {
		Trace.trace(Activator.PLUGIN_ID, DebugOptions.SVCPUBHANDLERDEBUG, this
				.getClass(), methodName, message);
	}

	/*
	 * protected void traceException(String string, Throwable e) {
	 * Trace.catching(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_CATCHING,
	 * this.getClass(), string, e); }
	 */
	public void dispose() {
		if (locator != null) {
			locator.removeServiceListener(serviceListener);
			for (Iterator i = serviceInfos.keySet().iterator(); i.hasNext();) {
				ServiceReference sr = (ServiceReference) i.next();
				unpublishService(sr);
			}
			serviceInfos.clear();
			locator = null;
		}
		if (advertiser != null) {
			advertiser = null;
		}
	}
}