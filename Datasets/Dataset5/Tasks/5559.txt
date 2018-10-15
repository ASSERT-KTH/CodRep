idFilter[i].getName());

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

import java.util.ArrayList;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.DebugOptions;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.IDUtil;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.LogUtility;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.PropertiesUtil;

public abstract class AbstractMetadataFactory {

	protected static final String LIST_SEPARATOR = " ";

	protected void encodeString(IServiceProperties props, String name,
			String value) {
		props.setPropertyString(name, value);
	}

	protected String decodeString(IServiceProperties props, String name) {
		return props.getPropertyString(name);
	}

	protected void encodeLong(IServiceProperties result, String name, Long value) {
		result.setPropertyString(name, value.toString());
	}

	protected Long decodeLong(IServiceProperties props, String name) {
		String longAsString = props.getPropertyString(name);
		if (longAsString == null)
			return new Long(0);
		return new Long(longAsString);
	}

	protected void encodeList(IServiceProperties props, String name,
			List<String> list) {
		if (list == null)
			return;
		if (list.size() == 1) {
			props.setPropertyString(name, list.get(0));
		} else {
			final StringBuffer result = new StringBuffer();
			for (Iterator<String> i = list.iterator(); i.hasNext();) {
				result.append(i.next());
				if (i.hasNext())
					result.append(LIST_SEPARATOR);
			}
			// Now add to props
			props.setPropertyString(name, result.toString());
		}
	}

	protected List<String> decodeList(IServiceProperties props, String name) {
		String value = props.getPropertyString(name);
		if (value == null)
			return Collections.EMPTY_LIST;
		List<String> result = new ArrayList<String>();
		final StringTokenizer t = new StringTokenizer(value, LIST_SEPARATOR);
		while (t.hasMoreTokens())
			result.add(t.nextToken());
		return result;
	}

	protected void encodeIDArray(IServiceProperties result, ID[] idFilter) {
		// First, for every id, setup prop name with index suffix
		for (int i = 0; i < idFilter.length; i++) {
			encodeString(result,
					RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAME_ + i,
					idFilter[i].toExternalForm());
			result.setPropertyString(
					RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAMESPACE_ + i,
					idFilter[i].getNamespace().getName());
		}
		// Now add count
		result.setPropertyString(
				RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_COUNT, new Integer(
						idFilter.length).toString());
	}

	protected ID[] decodeIDArray(IServiceProperties props) {
		// First, get the count
		String countValue = props
				.getPropertyString(RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_COUNT);
		if (countValue == null)
			return null;
		int count = new Integer(countValue).intValue();
		if (count <= 0)
			return null;
		List result = new ArrayList();
		for (int i = 0; i < count; i++) {
			// decode string as name
			String idName = decodeString(props,
					RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAME_ + i);
			if (idName == null)
				continue;
			String nsName = props
					.getPropertyString(RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAMESPACE_
							+ i);
			Namespace ns = (nsName != null) ? IDUtil.getNamespaceByName(nsName)
					: IDUtil.findNamespaceByIdName(idName);
			if (ns == null)
				continue;
			result.add(IDUtil.createID(ns, idName));
		}
		return (ID[]) result.toArray(new ID[] {});
	}

	protected void decodeOSGiProperties(IServiceProperties props,
			Map osgiProperties) {
		// OSGI
		// endpoint.id
		String endpointId = decodeString(props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_ID);
		osgiProperties
				.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_ID,
						endpointId);
		// endpoint.service.id
		Long endpointServiceId = decodeLong(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_SERVICE_ID);
		osgiProperties
				.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_SERVICE_ID,
						endpointServiceId);
		// objectClass
		List<String> interfaces = decodeList(props,
				org.osgi.framework.Constants.OBJECTCLASS);
		osgiProperties.put(org.osgi.framework.Constants.OBJECTCLASS,
				(String[]) interfaces.toArray(new String[] {}));
		// framework uuid
		String fwkuuid = decodeString(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_FRAMEWORK_UUID);
		osgiProperties
				.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_FRAMEWORK_UUID,
						fwkuuid);
		// configuration types
		List<String> configTypes = decodeList(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED_CONFIGS);
		if (configTypes != null && configTypes.size() > 0)
			osgiProperties
					.put(org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED_CONFIGS,
							(String[]) configTypes
									.toArray(new String[configTypes.size()]));
		// service intents
		List<String> intents = decodeList(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS);
		if (intents != null && intents.size() > 0)
			osgiProperties
					.put(org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS,
							(String[]) intents.toArray(new String[intents
									.size()]));

		// remote supported configs
		List<String> remoteConfigsSupported = decodeList(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_CONFIGS_SUPPORTED);
		if (remoteConfigsSupported != null && remoteConfigsSupported.size() > 0)
			osgiProperties
					.put(org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_CONFIGS_SUPPORTED,
							(String[]) remoteConfigsSupported
									.toArray(new String[remoteConfigsSupported
											.size()]));

		// remote supported configs
		List<String> remoteIntentsSupported = decodeList(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_INTENTS_SUPPORTED);
		if (remoteIntentsSupported != null && remoteIntentsSupported.size() > 0)
			osgiProperties
					.put(org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_INTENTS_SUPPORTED,
							(String[]) remoteIntentsSupported
									.toArray(new String[remoteIntentsSupported
											.size()]));

	}

	protected EndpointDescription decodeEndpointDescription(
			IServiceProperties discoveredServiceProperties) {
		Map osgiProperties = new HashMap();
		decodeOSGiProperties(discoveredServiceProperties, osgiProperties);

		// remote service id
		Long remoteServiceId = decodeLong(discoveredServiceProperties,
				org.eclipse.ecf.remoteservice.Constants.SERVICE_ID);
		osgiProperties.put(org.eclipse.ecf.remoteservice.Constants.SERVICE_ID,
				remoteServiceId);
		// container id namespace
		String containerIDNamespace = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE);
		// target ID
		String targetName = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONNECTTARGET_ID);
		String targetNamespace = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE);
		ID targetID = null;
		if (targetName != null) {
			Namespace ns = (targetNamespace != null) ? IDUtil
					.getNamespaceByName(targetNamespace) : IDUtil
					.findNamespaceByIdName(targetName);
			if (ns != null)
				targetID = IDUtil.createID(ns, targetName);
		}
		// ID filter
		ID[] idFilter = decodeIDArray(discoveredServiceProperties);
		// remote service filter
		String remoteServiceFilter = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_REMOTESERVICE_FILTER);

		// Finally, fill out other properties
		decodeNonStandardServiceProperties(discoveredServiceProperties,
				osgiProperties);

		return new EndpointDescription(osgiProperties, containerIDNamespace,
				targetID, idFilter, remoteServiceFilter);
	}

	protected void encodeServiceProperties(
			EndpointDescription endpointDescription, IServiceProperties result) {
		// OSGi objectClass = endpointDescription.getInterfaces();
		List<String> interfaces = endpointDescription.getInterfaces();
		encodeList(result, org.osgi.framework.Constants.OBJECTCLASS, interfaces);
		// OSGi service properties
		// endpoint.id == endpointDescription.getId()
		String endpointId = endpointDescription.getId();
		encodeString(
				result,
				org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_ID,
				endpointId);
		// OSGi endpoint.service.id = endpointDescription.getServiceId()
		long endpointServiceId = endpointDescription.getServiceId();
		encodeLong(
				result,
				org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_SERVICE_ID,
				new Long(endpointServiceId));
		// OSGi frameworkUUID = endpointDescription.getFrameworkUUID()
		String frameworkUUID = endpointDescription.getFrameworkUUID();
		if (frameworkUUID != null)
			encodeString(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_FRAMEWORK_UUID,
					frameworkUUID);
		// OSGi configuration types =
		// endpointDescription.getConfigurationTypes();
		List<String> configurationTypes = endpointDescription
				.getConfigurationTypes();
		if (configurationTypes.size() > 0)
			encodeList(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED_CONFIGS,
					configurationTypes);
		// OSGI service intents = endpointDescription.getIntents()
		List<String> serviceIntents = endpointDescription.getIntents();
		if (serviceIntents.size() > 0)
			encodeList(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS,
					serviceIntents);
		Map endpointDescriptionProperties = endpointDescription.getProperties();
		List<String> remoteConfigsSupported = PropertiesUtil
				.getStringPlusProperty(
						endpointDescriptionProperties,
						org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_CONFIGS_SUPPORTED);
		if (remoteConfigsSupported.size() > 0)
			encodeList(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_CONFIGS_SUPPORTED,
					remoteConfigsSupported);

		List<String> remoteIntentsSupported = PropertiesUtil
				.getStringPlusProperty(
						endpointDescriptionProperties,
						org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_INTENTS_SUPPORTED);
		if (remoteIntentsSupported.size() > 0)
			encodeList(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_INTENTS_SUPPORTED,
					remoteIntentsSupported);

		// namespace
		String containerIDNamespace = endpointDescription
				.getContainerIDNamespace();
		encodeString(result, RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE,
				containerIDNamespace);
		// ECF remote service id = endpointDescription.getRemoteServiceId()
		long remoteServiceId = endpointDescription.getRemoteServiceId();
		encodeLong(result, org.eclipse.ecf.remoteservice.Constants.SERVICE_ID,
				new Long(remoteServiceId));
		// ECF connectTargetID = endpointDescription.getConnectTargetID()
		ID connectTargetID = endpointDescription.getConnectTargetID();
		if (connectTargetID != null) {
			// external form of ID
			encodeString(result, RemoteConstants.ENDPOINT_CONNECTTARGET_ID,
					connectTargetID.toExternalForm());
			// namespace
			encodeString(result,
					RemoteConstants.ENDPOINT_CONNECTTARGET_ID_NAMESPACE,
					connectTargetID.getNamespace().getName());
		}
		// ECF idFilter = endpointDescription.getIDFilter();
		ID[] idFilter = endpointDescription.getIDFilter();
		if (idFilter != null && idFilter.length > 0) {
			encodeIDArray(result, idFilter);
		}

		// ECF remote service filter =
		// endpointDescription.getRemoteServiceFilter()
		String remoteFilter = endpointDescription.getRemoteServiceFilter();
		if (remoteFilter != null) {
			encodeString(result, RemoteConstants.ENDPOINT_REMOTESERVICE_FILTER,
					remoteFilter);
		}
		// encode non standar properties
		encodeNonStandardServiceProperties(endpointDescription.getProperties(),
				result);
	}

	protected void encodeNonStandardServiceProperties(
			Map<String, Object> properties, IServiceProperties result) {
		for (String key : properties.keySet()) {
			if (!PropertiesUtil.isReservedProperty(key)) {
				Object val = properties.get(key);
				if (val instanceof byte[]) {
					result.setPropertyBytes(key, (byte[]) val);
				} else if (val instanceof String) {
					result.setPropertyString(key, (String) val);
				} else {
					result.setProperty(key, val);
				}
			}
		}
	}

	protected void decodeNonStandardServiceProperties(IServiceProperties props,
			Map<String, Object> result) {
		for (Enumeration keys = props.getPropertyNames(); keys
				.hasMoreElements();) {
			String key = (String) keys.nextElement();
			if (!PropertiesUtil.isReservedProperty(key)) {
				byte[] bytes = props.getPropertyBytes(key);
				if (bytes != null) {
					result.put(key, bytes);
					continue;
				}
				String str = props.getPropertyString(key);
				if (str != null) {
					result.put(key, str);
					continue;
				}
				Object obj = props.getProperty(key);
				if (obj != null) {
					result.put(key, obj);
					continue;
				}
			}
		}
	}

	protected void logWarning(String methodName, String message, Throwable t) {
		LogUtility.logWarning(methodName, DebugOptions.DISCOVERY,
				this.getClass(), message, t);
	}

	protected void logError(String methodName, String message, Throwable t) {
		LogUtility.logError(methodName, DebugOptions.DISCOVERY,
				this.getClass(), message, t);
	}

	public void close() {
		// nothing to do
	}
}