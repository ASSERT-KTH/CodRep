ECFServicePublication.DISCOVERY_CONTAINER_ID_PROP, localContainerID);

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

import java.net.MalformedURLException;
import java.net.URL;
import java.util.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.osgi.services.discovery.ECFServicePublication;
import org.osgi.service.discovery.ServiceEndpointDescription;
import org.osgi.service.discovery.ServicePublication;

public class ServiceEndpointDescriptionImpl implements
		ServiceEndpointDescription {

	private final IServiceInfo serviceInfo;

	public ServiceEndpointDescriptionImpl(ID localContainerID,
			IServiceInfo serviceInfo) {
		this.serviceInfo = serviceInfo;
		// add localContainerID to set of service properties exposed by this
		this.serviceInfo.getServiceProperties().setProperty(
				ECFServicePublication.CONTAINER_ID_PROP, localContainerID);
	}

	public String getEndpointID() {
		return ServicePropertyUtils.getStringProperty(serviceInfo
				.getServiceProperties(),
				ServicePublication.PROP_KEY_ENDPOINT_ID);
	}

	public String getEndpointInterfaceName(String interfaceName) {
		if (interfaceName == null)
			return null;
		String intfNames = serviceInfo.getServiceProperties()
				.getPropertyString(
						ServicePublication.PROP_KEY_ENDPOINT_INTERFACE_NAME);
		if (intfNames == null)
			return null;
		Collection c = ServicePropertyUtils
				.createCollectionFromString(intfNames);
		if (c == null)
			return null;
		// 
		for (Iterator i = c.iterator(); i.hasNext();) {
			String intfName = (String) i.next();
			if (intfName != null && intfName.startsWith(interfaceName)) {
				// return just endpointInterfaceName
				return intfName
						.substring(
								intfName.length()
										+ ServicePropertyUtils.ENDPOINT_INTERFACE_NAME_SEPARATOR
												.length()).trim();
			}
		}
		return null;
	}

	public URL getLocation() {
		String urlExternalForm = ServicePropertyUtils.getStringProperty(
				serviceInfo.getServiceProperties(),
				ServicePublication.PROP_KEY_ENDPOINT_LOCATION);
		if (urlExternalForm == null)
			return null;
		URL url = null;
		try {
			url = new URL(urlExternalForm);
		} catch (MalformedURLException e) {
			// XXX log to error
		}
		return url;
	}

	public Map getProperties() {
		Map result = new HashMap();
		IServiceProperties serviceProperties = serviceInfo
				.getServiceProperties();
		if (serviceProperties != null) {
			for (Enumeration e = serviceProperties.getPropertyNames(); e
					.hasMoreElements();) {
				String propName = (String) e.nextElement();
				Object val = serviceProperties.getProperty(propName);
				result.put(propName, val);
			}
		}
		return result;
	}

	public Object getProperty(String key) {
		IServiceProperties serviceProperties = serviceInfo
				.getServiceProperties();
		if (key == null)
			return null;
		return serviceProperties.getProperty(key);
	}

	public Collection getPropertyKeys() {
		IServiceProperties serviceProperties = serviceInfo
				.getServiceProperties();
		List result = new ArrayList();
		for (Enumeration e = serviceProperties.getPropertyNames(); e
				.hasMoreElements();) {
			String name = (String) e.nextElement();
			result.add(name);
		}
		return result;
	}

	public Collection getProvidedInterfaces() {
		String providedInterfacesStr = serviceInfo.getServiceProperties()
				.getPropertyString(
						ServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME);
		return ServicePropertyUtils
				.createCollectionFromString(providedInterfacesStr);
	}

	public String getVersion(String interfaceName) {
		String intfNames = serviceInfo.getServiceProperties()
				.getPropertyString(
						ServicePublication.PROP_KEY_SERVICE_INTERFACE_VERSION);
		if (intfNames == null)
			return null;
		Collection c = ServicePropertyUtils
				.createCollectionFromString(intfNames);
		if (c == null)
			return null;
		// 
		for (Iterator i = c.iterator(); i.hasNext();) {
			String intfName = (String) i.next();
			if (intfName != null && intfName.startsWith(interfaceName)) {
				// return just version string
				return intfName
						.substring(
								intfName.length()
										+ ServicePropertyUtils.INTERFACE_VERSION_SEPARATOR
												.length()).trim();
			}
		}
		return null;
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("ServiceEndpointDescriptionImpl[");
		sb.append("providedinterfaces=").append(getProvidedInterfaces());
		sb.append(";location=").append(getLocation());
		sb.append(";props=").append(getProperties()).append("]");
		return sb.toString();
	}

}