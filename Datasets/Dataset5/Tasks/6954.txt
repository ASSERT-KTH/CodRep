protected org.osgi.service.remoteserviceadmin.EndpointDescription createEndpointDescriptionFromDiscovery(

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.tests.osgi.services.remoteserviceadmin;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.discovery.IDiscoveryAdvertiser;
import org.eclipse.ecf.discovery.IDiscoveryLocator;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.DiscoveredEndpointDescription;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.EndpointDescription;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.IDiscoveredEndpointDescriptionFactory;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.IServiceInfoFactory;
import org.eclipse.ecf.tests.ECFAbstractTestCase;
import org.osgi.framework.Constants;
import org.osgi.util.tracker.ServiceTracker;

public abstract class AbstractMetadataFactoryTest extends ECFAbstractTestCase {

	protected static final String DEFAULT_SERVICE_INTF_PACKAGE = "com.foo";
	protected static final String DEFAULT_SERVICE_INTF_VERSION = "3.0.0";
	protected static final String DEFAULT_SERVICE_INTF = DEFAULT_SERVICE_INTF_PACKAGE + "." + "Foo";
	
	protected static final String DEFAULT_ENDPOINT_ID = "ecftcp://localhost:3282/server";
	protected static final String DEFAULT_SERVICE_IMPORTED_CONFIG = "ecf.generic.server";
	protected static final String DEFAULT_SERVICE_INTENT1 = "test.intent.1";
	protected static final String DEFAULT_SERVICE_INTENT2 = "test.intent.2";
	protected static final String DEFAULT_ECF_TARGET_ID = "ecftcp://localhost:3333/server";
	protected static final String DEFAULT_RSFILTER = "(&(key1=foo)(key2=foo2))";
	protected static final String EXTRA_PROPERTY1 = "test.extra.prop.value.1";
	protected static final String EXTRA_PROPERTY2 = "test.extra.prop.value.2";
	
	protected IServiceInfoFactory serviceInfoFactory;
	protected IDiscoveredEndpointDescriptionFactory endpointDescriptionFactory;
	
	protected IDiscoveryAdvertiser discoveryAdvertiser;
	protected IDiscoveryLocator discoveryLocator;

	protected IDiscoveryLocator getDiscoveryLocator() {
		ServiceTracker serviceTracker = new ServiceTracker(Activator.getContext(),IDiscoveryLocator.class.getName(), null);
		serviceTracker.open();
		IDiscoveryLocator result = (IDiscoveryLocator) serviceTracker.getService();
		serviceTracker.close();
		return result;
	}
	
	protected IDiscoveryAdvertiser getDiscoveryAdvertiser() {
		ServiceTracker serviceTracker = new ServiceTracker(Activator.getContext(),IDiscoveryAdvertiser.class.getName(), null);
		serviceTracker.open();
		IDiscoveryAdvertiser result = (IDiscoveryAdvertiser) serviceTracker.getService();
		serviceTracker.close();
		return result;
	}

	protected void setUp() throws Exception {
		super.setUp();
	}
	
	protected void tearDown() throws Exception {
		serviceInfoFactory = null;
		endpointDescriptionFactory = null;
		discoveryAdvertiser = null;
		discoveryLocator = null;
		super.tearDown();
	}
	
	protected Object createOSGiObjectClass() {
		return new String[] { DEFAULT_SERVICE_INTF };
	}
	
	protected String createOSGiEndpointFrameworkUUID() {
		return UUID.randomUUID().toString();
	}
	
	protected String createOSGiEndpointId() {
		return DEFAULT_ENDPOINT_ID;
	}
	
	protected Long createOSGiEndpointServiceId() {
		return new Long(1);
	}
	
	protected EndpointDescription createRequiredEndpointDescription() {
		Map<String,Object> props = new HashMap<String,Object>();
		// Add required OSGi properties
		addRequiredOSGiProperties(props);
		ID containerID = createECFContainerID(props);
		Long remoteServiceId = createECFRemoteServiceId(props);
		// Add extra properties
		addExtraProperties(props);
		return new EndpointDescription(props,containerID,remoteServiceId,null,null,null);
	}
	
	protected EndpointDescription createFullEndpointDescription() {
		Map<String,Object> props = new HashMap<String,Object>();
		// Add required OSGi properties
		addRequiredOSGiProperties(props);
		// Add full OSGi properties
		addOptionalOSGiProperties(props);
		// required ECF properties
		ID containerID = createECFContainerID(props);
		Long remoteServiceId = createECFRemoteServiceId(props);
		ID targetID = createECFTargetID(props);
		ID[] idFilter = createECFIDFilterIDs(props);
		String rsFilter = createECFRSFilter(props);
		// Add extra properties
		addExtraProperties(props);
		return new EndpointDescription(props,containerID, remoteServiceId,targetID,idFilter,rsFilter);
	}

	protected void addExtraProperties(Map<String, Object> props) {
		props.put(EXTRA_PROPERTY1, "com.foo.bar.propertyvalue1");
		props.put(EXTRA_PROPERTY2, "com.foo.bar.propertyvalue2");
	}

	protected EndpointDescription createBadOSGiEndpointDescrption() throws Exception {
		Map<String,Object> props = new HashMap<String,Object>();
		// Add only ECF properties
		// no OSGi properties
		ID containerID = createECFContainerID(props);
		Long remoteServiceId = createECFRemoteServiceId(props);
		// This should throw a runtime exception 
		return new EndpointDescription(props,containerID,remoteServiceId.longValue(),null,null,null);
	}
	
	protected EndpointDescription createBadECFEndpointDescrption() throws Exception {
		Map<String,Object> props = new HashMap<String,Object>();
		// Add required OSGi properties
		addRequiredOSGiProperties(props);
		// Add full OSGi properties
		addOptionalOSGiProperties(props);
		
		// No ECF required properties
		// This should throw a runtime exception 
		return new EndpointDescription(props,null,0,null,null,null);
	}

	protected String createOSGiServiceImportedConfig() {
		return DEFAULT_SERVICE_IMPORTED_CONFIG;
	}
	
	protected ID createECFContainerID(Map<String,Object> props) {
		return getIDFactory().createStringID(DEFAULT_ENDPOINT_ID);
	}
	
	protected ID createECFTargetID(Map<String,Object> props) {
		return getIDFactory().createStringID(DEFAULT_ECF_TARGET_ID);
	}

	protected Long createECFRemoteServiceId(Map<String,Object> props) {
		return new Long(101);
	}
	
	protected void addRequiredOSGiProperties(Map<String,Object> props) {
		// OBJECTCLASS
		props.put(Constants.OBJECTCLASS,createOSGiObjectClass());
		// endpoint.service.id
		props.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_SERVICE_ID, createOSGiEndpointServiceId());
		// endpoint.framework.id
		props.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_FRAMEWORK_UUID, createOSGiEndpointFrameworkUUID());
		// endpoint.id
		props.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_ID, createOSGiEndpointId());
		// service imported configs
		props.put(org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_IMPORTED_CONFIGS,createOSGiServiceImportedConfig());
	}
	
	protected void addOptionalOSGiProperties(Map<String,Object> props) {
		props.put(org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS, createOSGiServiceIntents());
		props.put(org.osgi.service.remoteserviceadmin.RemoteConstants.ENDPOINT_PACKAGE_VERSION_+DEFAULT_SERVICE_INTF_PACKAGE,DEFAULT_SERVICE_INTF_VERSION);
	}
	

	protected Object createOSGiServiceIntents() {
		return new String[] { DEFAULT_SERVICE_INTENT1, DEFAULT_SERVICE_INTENT2 };
	}

	protected String createECFRSFilter(Map<String, Object> props) {
		return DEFAULT_RSFILTER;
	}

	protected ID[] createECFIDFilterIDs(Map<String, Object> props) {
		return new ID[] { getIDFactory().createGUID(), getIDFactory().createGUID() };
	}

	protected IServiceInfo createServiceInfoForDiscovery(EndpointDescription endpointDescription) {
		return serviceInfoFactory.createServiceInfoForDiscovery(discoveryAdvertiser, endpointDescription);
	}
	
	protected EndpointDescription createEndpointDescriptionFromDiscovery(
			IServiceInfo discoveredServiceInfo) {
		DiscoveredEndpointDescription ded = endpointDescriptionFactory.createDiscoveredEndpointDescription(discoveryLocator, discoveredServiceInfo);
		assertNotNull(ded);
		return ded.getEndpointDescription();
	}

}