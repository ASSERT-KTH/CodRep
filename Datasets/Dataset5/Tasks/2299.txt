public static final String DISCOVERY_NAMING_AUTHORITY = "ecf.endpoint.discovery.namingauthority";

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

public class RemoteConstants {

	public static final String SERVICE_TYPE = "osgirsvc";

	public static final String DISCOVERY_SCOPE = "ecf.endpoint.discovery.scope";
	public static final String DISCOVERY_PROTOCOLS = "ecf.endpoint.discovery.protocols";
	public static final String DISCOVERY_NAMING_AUTHORITY = "ecf.endpoint.discovery.nameingauthority";
	public static final String DISCOVERY_SERVICE_NAME = "ecf.endpoint.discovery.servicename";
	public static final String DISCOVERY_DEFAULT_SERVICE_NAME_PREFIX = "osgirsvc_";

	// container id. Value of type ID for EndpointDescription
	public static final String ENDPOINT_CONTAINER_ID = "ecf.endpoint.id";
	// container id namespace. Value of type String
	public static final String ENDPOINT_CONTAINER_ID_NAMESPACE = "ecf.endpoint.id.ns";
	// remote service id. Value of type Long
	public static final String ENDPOINT_REMOTESERVICE_ID = "ecf.endpoint.remoteservice.id";
	// target id. Value of type ID
	public static final String ENDPOINT_CONNECTTARGET_ID = "ecf.endpoint.connecttarget.id";
	// target namespace. Value of type String
	public static final String ENDPOINT_CONNECTTARGET_ID_NAMESPACE = "ecf.endpoint.connecttarget.id.ns";
	// id filter. Value of type ID[]
	public static final String ENDPOINT_IDFILTER_IDS = "ecf.endpoint.idfilter.ids";

	public static final String ENDPOINT_IDFILTER_IDARRAY_COUNT = "ecf.endpoint.idfilter.id.n";
	// id filter external form
	public static final String ENDPOINT_IDFILTER_IDARRAY_NAME_ = "ecf.endpoint.idfilter.id.name.";
	// id filter namespaces
	public static final String ENDPOINT_IDFILTER_IDARRAY_NAMESPACE_ = "ecf.endpoint.idfilter.id.ns.";
	// remote service filter
	public static final String ENDPOINT_REMOTESERVICE_FILTER = "ecf.endpoint.rsfilter";

}