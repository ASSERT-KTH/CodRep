protected static final int REGISTER_WAIT = 60000;

/*******************************************************************************
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.osgi.services.distribution;

import java.util.Collection;
import java.util.Iterator;
import java.util.Properties;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.Activator;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.distribution.DistributionProvider;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public abstract class AbstractServiceRegisterTest extends
		AbstractDistributionTest {

	private static final int REGISTER_WAIT = 60000;

	public void testRegisterServer() throws Exception {
		Properties props = new Properties();
		// *For testing purposes only* -- Set the server container id property, so that the service is not
		// distributed by both the client and server (which are both running in the same process
		// for junit plugin tests)
		IContainer serverContainer = getServer();
		props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());
		
		// Set OSGI property that identifies this service as a service to be remoted
		props.put(REMOTE_INTERFACES, new String[] {REMOTE_INTERFACES_WILDCARD});
		// Actually register with default service (IConcatService)
		ServiceRegistration registration = registerDefaultService(props);
		// Wait a while
		Thread.sleep(REGISTER_WAIT);
		// Then unregister
		registration.unregister();
		Thread.sleep(REGISTER_WAIT);
	}

	protected ServiceTracker createProxyServiceTracker(String clazz) throws InvalidSyntaxException {
		ServiceTracker st = new ServiceTracker(getContext(),getContext().createFilter("(&("+org.osgi.framework.Constants.OBJECTCLASS+"=" + clazz +")(" + REMOTE + "=*))"),new ServiceTrackerCustomizer() {

			public Object addingService(ServiceReference reference) {
				Trace.trace(Activator.PLUGIN_ID, "addingService="+reference);
				return getContext().getService(reference);
			}

			public void modifiedService(ServiceReference reference,
					Object service) {
				Trace.trace(Activator.PLUGIN_ID, "modifiedService="+reference);
			}

			public void removedService(ServiceReference reference,
					Object service) {
				Trace.trace(Activator.PLUGIN_ID, "removedService="+reference+",svc="+service);
			}});
		st.open();
		return st;
	}
	
	public void testGetProxy() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);
		
		// Server - register service with required OSGI property and some test properties
		Properties props = new Properties();
		// *For testing purposes only* -- Set the server container id property, so that the service is not
		// distributed by both the client and server (which are both running in the same process
		// for junit plugin tests)
		IContainer serverContainer = getServer();
		props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());
		// Set required OSGI property that identifies this service as a service to be remoted
		props.put(REMOTE_INTERFACES, new String[] {REMOTE_INTERFACES_WILDCARD});
		// Put property foo with value bar into published properties
		String testPropKey = "foo";
		String testPropVal = "bar";
		props.put(testPropKey, testPropVal);
		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname, new TestService1(),props);
		Thread.sleep(REGISTER_WAIT);
		
		// Client - Get service references that are proxies
		ServiceReference [] remoteReferences = st.getServiceReferences();
		assertTrue(remoteReferences != null);
		assertTrue(remoteReferences.length > 0);
		for(int i=0; i < remoteReferences.length; i++) {
			// Get OBJECTCLASS property from first remote reference
			String[] classes = (String []) remoteReferences[i].getProperty(org.osgi.framework.Constants.OBJECTCLASS);
			assertTrue(classes != null);
			// Check object class
			assertTrue(classname.equals(classes[0]));
			// Check the prop
			String prop = (String) remoteReferences[i].getProperty(testPropKey);
			assertTrue(prop != null);
			assertTrue(prop.equals(testPropVal));
		}
		// Now unregister original registration and wait
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}
	
	public void testGetAndUseProxy() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);
		
		// Server - register service with required OSGI property and some test properties
		Properties props = new Properties();
		// *For testing purposes only* -- Set the server container id property, so that the service is not
		// distributed by both the client and server (which are both running in the same process
		// for junit plugin tests)
		IContainer serverContainer = getServer();
		props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());
		// Set required OSGI property that identifies this service as a service to be remoted
		props.put(REMOTE_INTERFACES, new String[] {REMOTE_INTERFACES_WILDCARD});
		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname, new TestService1(),props);
		Thread.sleep(REGISTER_WAIT);
		
		// Client - Get service references from service tracker
		ServiceReference [] remoteReferences = st.getServiceReferences();
		assertTrue(remoteReferences != null);
		assertTrue(remoteReferences.length > 0);
		
		for(int i=0; i < remoteReferences.length; i++) {
			// Get proxy/service
			TestServiceInterface1 proxy = (TestServiceInterface1) getContext().getService(remoteReferences[0]);
			assertNotNull(proxy);
			// Now use proxy
			String result = proxy.doStuff1();
			Trace.trace(Activator.PLUGIN_ID, "proxy.doStuff1 result="+result);
			assertTrue(TestServiceInterface1.TEST_SERVICE_STRING1.equals(result));
		}
		
		// Unregister on server and wait
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testGetAndUseIRemoteService() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);
		
		// Server - register service with required OSGI property and some test properties
		Properties props = new Properties();
		// *For testing purposes only* -- Set the server container id property, so that the service is not
		// distributed by both the client and server (which are both running in the same process
		// for junit plugin tests)
		IContainer serverContainer = getServer();
		props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());
		// Set required OSGI property that identifies this service as a service to be remoted
		props.put(REMOTE_INTERFACES, new String[] {REMOTE_INTERFACES_WILDCARD});
		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname, new TestService1(),props);
		Thread.sleep(REGISTER_WAIT);
		
		// Client - Get service references from service tracker
		ServiceReference [] remoteReferences = st.getServiceReferences();
		assertTrue(remoteReferences != null);
		assertTrue(remoteReferences.length > 0);
		
		for(int i=0; i < remoteReferences.length; i++) {
			Object o = remoteReferences[i].getProperty(REMOTE);
			assertNotNull(o);
			assertTrue(o instanceof IRemoteService);
			IRemoteService rs = (IRemoteService) o;
			// Now call rs methods
			IRemoteCall call = createRemoteCall(TestServiceInterface1.class);
			if (call != null) {
				// Call synchronously
				Object result = rs.callSync(call);
				Trace.trace(Activator.PLUGIN_ID, "callSync.doStuff1 result="+result);
				assertNotNull(result);
				assertTrue(result instanceof String);
				assertTrue(TestServiceInterface1.TEST_SERVICE_STRING1.equals(result));
			}
		}
		
		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testGetExposedServicesFromDistributionProvider() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for distribution provider
		ServiceTracker st = new ServiceTracker(getContext(),DistributionProvider.class.getName(),null);
		st.open();
		DistributionProvider distributionProvider = (DistributionProvider) st.getService();
		assertNotNull(distributionProvider);
		
		// The returned collection should not be null
		Collection exposedServices = distributionProvider.getExposedServices();
		assertNotNull(exposedServices);

		// Server - register service with required OSGI property and some test properties
		Properties props = new Properties();
		// *For testing purposes only* -- Set the server container id property, so that the service is not
		// distributed by both the client and server (which are both running in the same process
		// for junit plugin tests)
		IContainer serverContainer = getServer();
		props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());
		// Set required OSGI property that identifies this service as a service to be remoted
		props.put(REMOTE_INTERFACES, new String[] {REMOTE_INTERFACES_WILDCARD});
		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname, new TestService1(),props);
		Thread.sleep(REGISTER_WAIT);

		// Client
		exposedServices = distributionProvider.getExposedServices();
		assertNotNull(exposedServices);
		int exposedLength = exposedServices.size();
		assertTrue(exposedLength > 0);
		for(Iterator i=exposedServices.iterator(); i.hasNext(); ) {
			Object o = ((ServiceReference) i.next()).getProperty(REMOTE_INTERFACES);
			assertTrue(o != null);
		}

		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
		
		// Check to see that the exposed service went away
		exposedServices= distributionProvider.getExposedServices();
		assertNotNull(exposedServices);
		assertTrue(exposedServices.size() == (exposedLength - 1));

	}

	public void testGetRemoteServicesFromDistributionProvider() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for distribution provider
		ServiceTracker st = new ServiceTracker(getContext(),DistributionProvider.class.getName(),null);
		st.open();
		DistributionProvider distributionProvider = (DistributionProvider) st.getService();
		assertNotNull(distributionProvider);
		
		// The returned collection should not be null
		Collection remoteServices = distributionProvider.getRemoteServices();
		assertNotNull(remoteServices);

		// Server - register service with required OSGI property and some test properties
		Properties props = new Properties();
		// *For testing purposes only* -- Set the server container id property, so that the service is not
		// distributed by both the client and server (which are both running in the same process
		// for junit plugin tests)
		IContainer serverContainer = getServer();
		props.put(Constants.SERVICE_CONTAINER_ID, serverContainer.getID());
		// Set required OSGI property that identifies this service as a service to be remoted
		props.put(REMOTE_INTERFACES, new String[] {REMOTE_INTERFACES_WILDCARD});
		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname, new TestService1(),props);
		Thread.sleep(REGISTER_WAIT);
		
		// Check that distribution provider (client) has remote services now
		remoteServices = distributionProvider.getRemoteServices();
		assertNotNull(remoteServices);
		int remotesLength = remoteServices.size();
		assertTrue(remotesLength > 0);
		for(Iterator i=remoteServices.iterator(); i.hasNext(); ) {
			Object o = ((ServiceReference) i.next()).getProperty(REMOTE);
			assertTrue(o != null);
		}
		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
		
		// Remote services should have gone down by one (because of unregister
		remoteServices= distributionProvider.getRemoteServices();
		assertNotNull(remoteServices);
		assertTrue(remoteServices.size() < remotesLength);

	}

	protected IRemoteCall createRemoteCall(Class clazz) {
		if (clazz.equals(TestServiceInterface1.class)) {
			return new IRemoteCall() {

				public String getMethod() {
					return "doStuff1";
				}

				public Object[] getParameters() {
					return new Object[] {};
				}

				public long getTimeout() {
					return 30000;
				}
				
			};
		}
		return null;
	}
}