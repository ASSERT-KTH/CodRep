public static final String REMOTESERVICE_NAMESPACE_NAME = "remote.service.namespace"; //$NON-NLS-1$

/****************************************************************************
 * Copyright (c) 2004, 2009 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.remoteservice;

import org.eclipse.ecf.core.IContainer;

/**
 * Remote service API constants.
 */
public interface Constants {

	/**
	 * Service property (named &quot;remote.objectClass&quot;) identifying all
	 * of the class names under which a service was registered in the remote
	 * services API (of type <code>java.lang.String[]</code>).
	 * 
	 * <p>
	 * This property is set by the remote services API when a service is
	 * registered.
	 */
	public static final String OBJECTCLASS = "remote.objectClass"; //$NON-NLS-1$

	/**
	 * Service property (named &quot;remote.service.id&quot;) identifying a
	 * service's registration number (of type <code>java.lang.Long</code>).
	 * 
	 * <p>
	 * The value of this property is assigned by the remote services API when a
	 * service is registered. The remote services API assigns a unique value
	 * that is larger than all previously assigned values since the remote
	 * services API was started. These values are NOT persistent across restarts
	 * of the remote services API.
	 */
	public static final String SERVICE_ID = "remote.service.id"; //$NON-NLS-1$

	/**
	 * Service property (named &quot;remote.service.ranking&quot;) identifying a
	 * service's ranking number (of type <code>java.lang.Integer</code>).
	 * 
	 * <p>
	 * This property may be supplied in the <code>properties
	 * Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 * 
	 * <p>
	 * The service ranking is used by the remote services API to determine the
	 * <i>default </i> service to be returned from a call to the
	 * {@link IRemoteServiceContainerAdapter#getRemoteServiceReferences(org.eclipse.ecf.core.identity.ID[], String, String)}
	 * method: If more than one service implements the specified class, the
	 * <code>RemoteServiceReference</code> object with the highest ranking is
	 * returned.
	 * 
	 * <p>
	 * The default ranking is zero (0). A service with a ranking of
	 * <code>Integer.MAX_VALUE</code> is very likely to be returned as the
	 * default service, whereas a service with a ranking of
	 * <code>Integer.MIN_VALUE</code> is very unlikely to be returned.
	 * 
	 * <p>
	 * If the supplied property value is not of type
	 * <code>java.lang.Integer</code>, it is deemed to have a ranking value
	 * of zero.
	 */
	public static final String SERVICE_RANKING = "remote.service.ranking"; //$NON-NLS-1$

	/**
	 * Service property (named &quot;remote.service.vendor&quot;) identifying a
	 * service's vendor.
	 * 
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 */
	public static final String SERVICE_VENDOR = "remote.service.vendor"; //$NON-NLS-1$

	/**
	 * Service property (named &quot;remoteservice.description&quot;)
	 * identifying a service's description.
	 * 
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 */
	public static final String SERVICE_DESCRIPTION = "remote.service.description"; //$NON-NLS-1$

	/**
	 * Service property (named &quot;remoteservice.description&quot;)
	 * identifying a a registration's target for receiving the service. The
	 * value of the property MUST be either a non-<code>null</code> instance
	 * of org.eclipse.ecf.core.identity.ID OR an ID[].
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 */
	public static final String SERVICE_REGISTRATION_TARGETS = "remote.service.registration.targets"; //$NON-NLS-1$

	/**
	 * Service property that defines the container factory name.
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 */
	public static final String CONTAINER_FACTORY_NAME = "org.eclipse.ecf.containerFactoryName"; //$NON-NLS-1$

	/**
	 * Service property that defines the container target for connection.
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 */
	public static final String CONTAINER_TARGET = "org.eclipse.ecf.containerTarget"; //$NON-NLS-1$

	/**
	 * Service property that defines the container target password.
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the
	 * <code>IRemoteServiceContainerAdapter.registerRemoteService</code>
	 * method.
	 */
	public static final String CONTAINER_PASSWORD = "org.eclipse.ecf.containerPassword"; //$NON-NLS-1$

	/**
	 * Service property that defines the remote service container ID.
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the <code>BundleContext.registerService</code> method.
	 */
	public static final String REMOTE_SERVICE_CONTAINER_ID = "org.eclipse.ecf.containerID"; //$NON-NLS-1$

	/**
	 * Service property that defines the remote service container ID factory name.
	 * <p>
	 * This property may be supplied in the properties <code>Dictionary</code>
	 * object passed to the <code>BundleContext.registerService</code> method.
	 */
	public static final String REMOTE_SERVICE_CONTAINER_ID_FACTORY_NAME = "org.eclipse.ecf.containerID.factory"; //$NON-NLS-1$

	/**
	 * Service property that determines whether a remote service proxy is automatically added to the local
	 * service registry.  This property can be used to expose remote services transparently
	 * to client (i.e. automatically putting a proxy into the client's local service registry).
	 * If this property is set in during service registration, then the the associated remote 
	 * service proxy should be added to the client's service registry by the implementing provider.  The value 
	 * of the property can be any non-<code>null</code> value.  
	 * <p></p>
	 * For example:
	 * <pre>
	 * final Dictionary props = new Hashtable();
	 * props.put(Constants.AUTOREGISTER_REMOTE_PROXY, "true");
	 * // Register
	 * adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, serviceImpl, props);
	 * </pre>
	 * 
	 */
	public static final String AUTOREGISTER_REMOTE_PROXY = "org.eclipse.ecf.serviceRegistrationRemote"; //$NON-NLS-1$

	// Constants for use with the ECF remote services API

	/**
	 * Constant defining the ECF remote services discovery service type.  This service type should
	 * be provided in the service type id when registering a remote service.  Then clients may
	 * identify an ECF remote service type ID and therefore be made aware of how the client can
	 * interact with the service.  
	 */
	public static final String DISCOVERY_SERVICE_TYPE = "remotesvcs"; //$NON-NLS-1$

	/**
	 * Discovery service property to specify a namespace name for creating a connect id.  Note that
	 * this property should be equal to the name of the namespace retrieved from {@link IContainer#getConnectNamespace()}.
	 * Note that this property is <b>optional</b> if DISCOVERY_SERVICE_TYPE is specified.
	 */
	public static final String DISCOVERY_CONNECT_ID_NAMESPACE_PROPERTY = "cns"; //$NON-NLS-1$

	/**
	 * Discovery service property to specify value for creating a connect id.  Note that
	 * this property should be equal to connectID retrieved from {@link IContainer#getConnectedID()}.
	 * Note that this property is <b>optional</b> if DISCOVERY_SERVICE_TYPE is specified.
	 */
	public static final String DISCOVERY_CONNECT_ID_PROPERTY = "cid"; //$NON-NLS-1$

	/**
	 * Discovery service property to specify a namespace name for creating a target service ID.
	 * Note that this property is <b>optional</b> if the DISCOVERY_SERVICE_TYPE is as given above. It is 
	 * expected that clients will use the value of this property, along with the DISCOVERY_SERVICE_ID_PROPERTY
	 * to create an ID instance for the 'idFilter' parameter via
	 * remoteServicesContainerAdapter.getRemoteServiceReferences(ID [] idFilter, String clazz, String filter). 

	 */
	public static final String DISCOVERY_SERVICE_ID_NAMESPACE_PROPERTY = "sns"; //$NON-NLS-1$

	/**
	 * Discovery service property for a 'remotesvcs' discovery type.  Note that this
	 * property is <b>optional</b> if the DISCOVERY_SERVICE_TYPE is as given above.  It is expected
	 * that clients will use the value of this property, along with the DISCOVERY_CONNECT_ID_NAMESPACE_PROPERTY
	 * to create an ID instance for the 'idFilter' parameter via
	 * remoteServicesContainerAdapter.getRemoteServiceReferences(ID [] idFilter, String clazz, String filter). 
	 */
	public static final String DISCOVERY_SERVICE_ID_PROPERTY = "sid"; //$NON-NLS-1$

	/**
	 * Discovery service property for specifying the remote interface type.  Note that this
	 * property is <b>required</b> if the DISCOVERY_SERVICE_TYPE is as given.  It is expected
	 * that clients will use the value of this property to perform service lookups with the 
	 * 'clazz' parameter via
	 * remoteServicesContainerAdapter.getRemoteServiceReferences(ID [] idFilter, String clazz, String filter).  
	 */
	public static final String DISCOVERY_OBJECTCLASS_PROPERTY = "cls"; //$NON-NLS-1$
	/**
	 * Discovery service property for specifying the service lookup filter for
	 * client service lookup via 
	 * remoteServicesContainerAdapter.getRemoteServiceReferences(ID [] idFilter, String clazz, String filter).  
	 * Note that this
	 * property is <b>optional</b> if the DISCOVERY_SERVICE_TYPE is as given above.
	 */
	public static final String DISCOVERY_FILTER_PROPERTY = "fltr"; //$NON-NLS-1$

	/**
	 * Discovery service property for specifying the container factory type.  Note that this
	 * property is <b>optional</b> if the DISCOVERY_SERVICE_TYPE is used as given above.
	 */
	public static final String DISCOVERY_CONTAINER_FACTORY_PROPERTY = "cft"; //$NON-NLS-1$

	public static final String REMOTESERVICE_NAMESPACE_NAME = "remote.service.namespace";

}