public interface IServiceConstants {

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.distribution;

public interface ECFServiceConstants {

	/*
	 * service.intents  an optional list of intents provided by the service.
	 * The property advertises capabilities of the service and can be used by
	 * the service consumer in the lookup filter to only select a service that
	 * provides certain qualities of service. The value of this property is of
	 * type String[] and has to be provided by the service as part of the
	 * registration, regardless whether its a local service or a proxy. The
	 * value on the proxy is a union of the value specified by the service
	 * provider, plus any remote-specific intents (see
	 * orgi.remote.require.intents, below), plus any intents which the
	 * Distribution Software adds that describe characteristics of the
	 * Distribution being mechanism. Therefore the value of this property can
	 * vary between the client side proxy and the server side.
	 */
	public static final String SERVICE_INTENTS = "service.intents";

	/*
	 * osgi.remote.interfaces  [ * | interface_name [, interface_name]* ]: A
	 * distribution software implementation may expose a service for remote
	 * access, if and only if the service has indicated its intention as well as
	 * support for remote invocations by setting this service property in its
	 * service registration. The value of this property is of type String[]. If
	 * the list contains only one value, which is set to *, all of the
	 * interfaces specified in the BundleContext.registerService() call are
	 * being exposed remotely. The value can also be set to a comma-separated
	 * list of interface names, which should be a subset of the interfaces
	 * specified in the registerService call. In this case only the specified
	 * interfaces are exposed remotely.
	 */
	public static final String OSGI_REMOTE_INTERFACES = "osgi.remote.interfaces";

	/*
	 * osgi.remote.requires.intents  an optional list of intents that should be
	 * provided when remotely exposing the service. If a DSW implementation
	 * cannot satisfy these intents when exposing the service remotely, it
	 * should not expose the service. The value of this property is of type
	 * String[].
	 */
	public static final String OSGI_REMOTE_REQUIRES_INTENTS = "osgi.remote.requires.intents";

	/*
	 * osgi.remote.configuration.type  service providing side property that
	 * identifies the metadata type of additional metadata, if any, that was
	 * provided with the service, e.g. sca. Multiple types and thus sets of
	 * additional metadata may be provided. The value of this property is of
	 * type String[].
	 */
	public static final String OSGI_REMOTE_CONFIGURATION_TYPE = "osgi.remote.configuration.type";

	/*
	 * osgi.remote  this property is set on client side service proxies
	 * registered in the OSGi Service Registry.
	 */
	public static final String OSGI_REMOTE = "osgi.remote";

	public static final String OSGI_REMOTE_INTERFACES_WILDCARD = "*";

	public static final String ECF_REMOTE_CONFIGURATION_TYPE = "ecf";

}