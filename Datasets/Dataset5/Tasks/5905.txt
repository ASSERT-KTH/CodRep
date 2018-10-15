ID connectTargetID = endpointDescription.getConnectTargetID();

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
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IIDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.StringID;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.Activator;

public abstract class AbstractMetadataFactory {

	protected static final String COLLECTION_SEPARATOR = ",";
	protected static final List osgiProperties = Arrays
			.asList(new String[] {
					// OSGi properties
					org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_ID,
					org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_SERVICE_ID,
					org.osgi.framework.Constants.OBJECTCLASS,
					org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_FRAMEWORK_UUID,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED_CONFIGS,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED, });

	protected static final List ecfProperties = Arrays.asList(new String[] {
			// ECF properties
			RemoteConstants.ENDPOINT_CONTAINER_ID,
			RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE,
			RemoteConstants.ENDPOINT_REMOTESERVICE_ID,
			RemoteConstants.ENDPOINT_CONNECTTARGET_ID,
			RemoteConstants.ENDPOINT_CONNECTTARGET_ID_NAMESPACE,
			RemoteConstants.ENDPOINT_IDFILTER_IDS,
			RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_COUNT,
			RemoteConstants.ENDPOINT_REMOTESERVICE_FILTER });

	protected String[] getStringArrayWithDefault(
			Map<String, Object> properties, String key, String[] def) {
		if (properties == null)
			return def;
		Object o = properties.get(key);
		if (o instanceof String) {
			return new String[] { (String) o };
		} else if (o instanceof String[]) {
			return (String[]) o;
		} else if (o instanceof List) {
			List l = (List) o;
			return (String[]) l.toArray(new String[l.size()]);
		}
		return def;
	}

	protected String getStringWithDefault(Map props, String key, String def) {
		if (props == null)
			return def;
		Object o = props.get(key);
		if (o == null || (!(o instanceof String)))
			return def;
		return (String) o;
	}

	protected Long getLongWithDefault(Map props, String key, Long def) {
		if (props == null)
			return def;
		Object o = props.get(key);
		if (o instanceof Long)
			return (Long) o;
		if (o instanceof String)
			return Long.valueOf((String) o);
		return def;
	}

	protected void encodeString(IServiceProperties props, String name,
			String value) {
		byte[] bytes = value.getBytes();
		props.setPropertyBytes(name, bytes);
	}

	protected String decodeString(IServiceProperties props, String name) {
		byte[] bytes = props.getPropertyBytes(name);
		if (bytes == null)
			return null;
		return new String(bytes);
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
			List<String> value) {
		final StringBuffer result = new StringBuffer();
		for (final Iterator<String> i = value.iterator(); i.hasNext();) {
			final String item = (String) i.next();
			result.append(item);
			if (i.hasNext()) {
				result.append(COLLECTION_SEPARATOR);
			}
		}
		// Now add to props
		props.setPropertyString(name, result.toString());
	}

	protected List decodeList(IServiceProperties props, String name) {
		String value = props.getPropertyString(name);
		if (value == null)
			return Collections.EMPTY_LIST;
		List result = new ArrayList();
		final StringTokenizer t = new StringTokenizer(value,
				COLLECTION_SEPARATOR);
		while (t.hasMoreTokens()) {
			result.add(t.nextToken());
		}
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
			String name = decodeString(props,
					RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAME_ + i);
			String ns = props
					.getPropertyString(RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAMESPACE_
							+ i);
			if (name != null && ns != null) {
				ID id = createID(ns, name);
				if (id != null)
					result.add(id);
			}
		}
		return (ID[]) result.toArray(new ID[] {});
	}

	protected ID createID(String namespace, String name)
			throws IDCreateException {
		return IDFactory.getDefault().createID(namespace, name);
	}

	protected ID createID(Namespace namespace, String name)
			throws IDCreateException {
		return IDFactory.getDefault().createID(namespace, name);
	}

	protected IIDFactory getIDFactory() {
		return IDFactory.getDefault();
	}

	protected Namespace getNamespace(String namespaceName) {
		Namespace result = findNamespace(namespaceName);
		return (result == null) ? getIDFactory().getNamespaceByName(
				StringID.class.getName()) : result;
	}

	protected Namespace findNamespace(String namespaceName) {
		return getIDFactory().getNamespaceByName(namespaceName);
	}

	protected Namespace findNamespaceForOSGiId(String osgiId) {
		int colonIndex = osgiId.indexOf(':');
		if (colonIndex <= 0)
			return null;
		String scheme = osgiId.substring(0, colonIndex);
		// First try to find the Namespace using the protocol directly
		Namespace ns = findNamespace(scheme);
		if (ns == null) {
			// Then try to find by comparing to all Namespace.getScheme()
			ns = findNamespaceByScheme(scheme);
		}
		return ns;
	}

	protected Namespace findNamespaceByScheme(String scheme) {
		if (scheme == null)
			return null;
		if (scheme.equals("ecftcp"))
			return getIDFactory().getNamespaceByName(StringID.class.getName());
		List namespaces = getIDFactory().getNamespaces();
		for (Iterator i = namespaces.iterator(); i.hasNext();) {
			Namespace ns = (Namespace) i.next();
			if (scheme.equals(ns.getScheme())) {
				// found it...so return
				return ns;
			}
		}
		// If the scheme is "ecftcp" then we use StringID
		return null;
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
							(String[]) configTypes.toArray(new String[] {}));
		// service intents
		List<String> intents = decodeList(
				props,
				org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS);
		if (intents != null && intents.size() > 0)
			osgiProperties
					.put(org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS,
							(String[]) intents.toArray(new String[] {}));
	}

	protected EndpointDescription decodeEndpointDescription(
			IServiceProperties discoveredServiceProperties) {
		Map osgiProperties = new HashMap();
		decodeOSGiProperties(discoveredServiceProperties, osgiProperties);

		// endpoint ID
		String endpointName = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONTAINER_ID);
		String endpointNamespace = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE);
		ID containerID = createID(endpointNamespace, endpointName);
		if (containerID == null)
			throw new NullPointerException("endpoint containerID for name="
					+ endpointName + " an namespace=" + endpointNamespace
					+ " cannot be null");

		// remote service id
		Long remoteServiceId = decodeLong(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_REMOTESERVICE_ID);
		// target ID
		String targetName = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONNECTTARGET_ID);
		String targetNamespace = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE);
		ID targetID = null;
		if (targetName != null && targetNamespace != null) {
			targetID = createID(targetNamespace, targetName);
		}
		// ID filter
		ID[] idFilter = decodeIDArray(discoveredServiceProperties);
		// remote service filter
		String remoteServiceFilter = decodeString(discoveredServiceProperties,
				RemoteConstants.ENDPOINT_REMOTESERVICE_FILTER);

		// Finally, fill out other properties
		decodeNonStandardServiceProperties(discoveredServiceProperties,
				osgiProperties);

		return new EndpointDescription(osgiProperties, containerID,
				remoteServiceId.longValue(), targetID, idFilter,
				remoteServiceFilter);
	}

	protected void encodeServiceProperties(
			EndpointDescription endpointDescription, IServiceProperties result) {
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

		// OSGi objectClass = endpointDescription.getInterfaces();
		List<String> interfaces = endpointDescription.getInterfaces();
		encodeList(result, org.osgi.framework.Constants.OBJECTCLASS, interfaces);

		// OSGi frameworkUUID = endpointDescription.getFrameworkUUID()
		String frameworkUUID = endpointDescription.getFrameworkUUID();
		if (frameworkUUID == null) {
			frameworkUUID = Activator.getDefault().getFrameworkUUID();
		}
		if (frameworkUUID != null)
			encodeString(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_FRAMEWORK_UUID,
					frameworkUUID);
		// OSGi configuration types =
		// endpointDescription.getConfigurationTypes();
		List<String> configurationTypes = endpointDescription
				.getConfigurationTypes();
		if (configurationTypes.size() > 0) {
			encodeList(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED_CONFIGS,
					configurationTypes);
		}
		// OSGI service intents = endpointDescription.getIntents()
		List<String> serviceIntents = endpointDescription.getIntents();
		if (serviceIntents.size() > 0) {
			encodeList(
					result,
					org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS,
					serviceIntents);
		}

		// ECF endpoint ID = endpointDescription.getID()
		ID endpointID = endpointDescription.getContainerID();
		// external form of ID
		encodeString(result, RemoteConstants.ENDPOINT_CONTAINER_ID,
				endpointID.toExternalForm());
		// namespace
		encodeString(result, RemoteConstants.ENDPOINT_CONTAINER_ID_NAMESPACE,
				endpointID.getNamespace().getName());
		// ECF remote service id = endpointDescription.getRemoteServiceId()
		long remoteServiceId = endpointDescription.getRemoteServiceId();
		encodeLong(result, RemoteConstants.ENDPOINT_REMOTESERVICE_ID, new Long(
				remoteServiceId));
		// ECF connectTargetID = endpointDescription.getConnectTargetID()
		ID connectTargetID = endpointDescription.getTargetID();
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

	protected boolean isOSGiProperty(String key) {
		if (key == null)
			return false;
		return osgiProperties.contains(key);
	}

	protected boolean isECFProperty(String key) {
		if (key == null)
			return false;
		return ecfProperties.contains(key)
				&& !key.startsWith(RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAME_)
				&& !key.startsWith(RemoteConstants.ENDPOINT_IDFILTER_IDARRAY_NAMESPACE_);
	}

	protected boolean isStandardProperty(String key) {
		if (key == null)
			return false;
		return isOSGiProperty(key) || isECFProperty(key);
	}

	protected void encodeNonStandardServiceProperties(
			Map<String, Object> properties, IServiceProperties result) {
		for (String key : properties.keySet()) {
			if (!isStandardProperty(key)) {
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
			if (!isStandardProperty(key)) {
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

	protected void logInfo(String methodName, String message, Throwable t) {
		// XXX todo
	}

	protected void logError(String methodName, String message, Throwable t) {
		// XXX todo
	}

	public void close() {
		// nothing to do
	}
}