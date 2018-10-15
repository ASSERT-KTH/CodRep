public final class Messages extends NLS {

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.provider.jmdns;

import org.eclipse.osgi.util.NLS;

/**
 *
 */
public class Messages extends NLS {
	private static final String BUNDLE_NAME = "org.eclipse.ecf.internal.provider.jmdns.messages"; //$NON-NLS-1$
	public static String ContainerInstantiator_EXCEPTION_CONTAINER_CREATE;
	public static String ContainerInstantiator_EXCEPTION_GETTING_INETADDRESS;
	public static String ECFStart_WARNING_COULD_NOT_REGISTER_DISCOVERY;
	public static String JMDNSDiscoveryContainer_EXCEPTION_ALREADY_CONNECTED;
	public static String JMDNSDiscoveryContainer_EXCEPTION_CONTAINER_DISPOSED;
	public static String JMDNSDiscoveryContainer_EXCEPTION_CREATE_JMDNS_INSTANCE;
	public static String JMDNSDiscoveryContainer_DISCOVERY_NOT_INITIALIZED;
	public static String JMDNSDiscoveryContainer_EXCEPTION_REGISTER_SERVICE;
	public static String JMDNSDiscoveryContainer_EXCEPTION_SERVICEINFO_INVALID;
	public static String JMDNSDiscoveryContainer_JMDNS_LOCAL_SUFFIX;
	public static String JMDNSDiscoveryContainer_NO_JMDNS_SERVICE_TYPE;
	public static String JMDNSDiscoveryContainer_NO_SERVICE_TYPE;
	public static String JMDNSDiscoveryContainer_SERVICE_NAME_NOT_NULL;
	public static String JMDNSNamespace_EXCEPTION_ID_CREATE_SERVICE_TYPE_CANNOT_BE_EMPTY;
	public static String JMDNSNamespace_EXCEPTION_ID_PARAM_2_WRONG_TYPE;
	public static String JMDNSNamespace_EXCEPTION_ID_WRONG_PARAM_COUNT;
	public static String JMDNSServiceTypeID_EXCEPTION_INVALID_TYPE_ID;
	public static String JMDNSNamespace_EXCEPTION_TYPE_PARAM_NOT_STRING;
	static {
		// initialize resource bundle
		NLS.initializeMessages(BUNDLE_NAME, Messages.class);
	}

	private Messages() {
		//
	}
}