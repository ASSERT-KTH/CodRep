public interface RemoteServicePublication extends ServicePublication {

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.discovery;

import org.osgi.service.discovery.ServicePublication;

public interface IServicePublication extends ServicePublication {

	/**
	 * Discovery OSGi Service Type for publishing/discovering osgiservices
	 */
	public static final String SERVICE_TYPE = "osgiservices"; //$NON-NLS-1$
	/**
	 * Prefix for the default service name. The default service name will be the
	 * DEFAULT_SERVICE_NAME_PREFIX+serviceID (long)
	 */
	public static final String DEFAULT_SERVICE_NAME_PREFIX = "service "; //$NON-NLS-1$

	// Discovery service properties

	/**
	 * Discovery service name property. If the specified service property is
	 * non-null, the service name will override the default value, which is the
	 * DEFAULT_SERVICE_NAME_PREFIX+serviceID as described above. The value
	 * provided for this property must be of type String.
	 */
	public static final String SERVICE_NAME = "ecf.sp.svcname"; //$NON-NLS-1$
	/**
	 * Discovery naming authority property. If the specified serviceproperty is
	 * non-null, the discovery naming authority will override the default value,
	 * which is IServiceID#DEFAULT_NA ("iana"). The value provided for this
	 * property must be of type String.
	 */
	public static final String NAMING_AUTHORITY = "ecf.sp.namingauth"; //$NON-NLS-1$
	/**
	 * Discovery scope property. If the specified service property is non-null,
	 * the discovery scope will override the default value, which is
	 * IServiceID#DEFAULT_SCOPE ("default"). The value provided for this
	 * property must be of type String, which can be split into a String[] using
	 * ';' as the delimiter (e.g. 'scope1;scope2;scope3').
	 */
	public static final String SCOPE = "ecf.sp.scope"; //$NON-NLS-1$
	/**
	 * Discovery protocol property. If the specified service property is
	 * non-null, the discovery protocol will override the default value, which
	 * is IServiceID#DEFAULT_PROTO ("tcp"). The value provided for this property
	 * must be of type String, which can be split into a String[] using ';' as
	 * the delimiter (e.g. 'proto1;proto1;proto1').
	 */
	public static final String SERVICE_PROTOCOL = "ecf.sp.protocol"; //$NON-NLS-1$
	/**
	 * Endpoint container ID property. The value for this property must be of
	 * type byte[] which is a UTF-8 encoding of a String.
	 */
	public static final String ENDPOINT_CONTAINERID = "ecf.sp.cid"; //$NON-NLS-1$
	/**
	 * Endpoint container ID namespace property. The value provided for this
	 * property must be of type String.
	 */
	public static final String ENDPOINT_CONTAINERID_NAMESPACE = "ecf.sp.cns"; //$NON-NLS-1$
	/**
	 * Target container ID property. The value for this property must be of type
	 * byte[] which is a UTF-8 encoding of a String.
	 */
	public static final String TARGET_CONTAINERID = "ecf.sp.tid"; //$NON-NLS-1$
	/**
	 * Target container ID namespace property. The value provided for this
	 * property must be of type String.
	 */
	public static final String TARGET_CONTAINERID_NAMESPACE = "ecf.sp.tns"; //$NON-NLS-1$
	/**
	 * Client remote service filter property. The value provided for this
	 * property must be of type String.
	 */
	public static final String REMOTE_SERVICE_FILTER = "ecf.client.filter"; //$NON-NLS-1$
}