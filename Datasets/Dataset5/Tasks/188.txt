protected static final int REGISTER_WAIT = Integer.parseInt(System.getProperty("waittime","15000"));

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

import java.util.Properties;

import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteCallListener;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceProxy;
import org.eclipse.ecf.remoteservice.events.IRemoteCallCompleteEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteCallEvent;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.Activator;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public abstract class AbstractRemoteServiceAccessTest extends
		AbstractDistributionTest {

	private static final String TESTPROP1_VALUE = "baz";
	private static final String TESTPROP_VALUE = "foobar";
	private static final String TESTPROP1_NAME = "org.eclipse.ecf.testprop1";
	private static final String TESTPROP_NAME = "org.eclipse.ecf.testprop";
	protected static final int REGISTER_WAIT = 30000;

	protected ServiceTracker createProxyServiceTracker(String clazz)
			throws InvalidSyntaxException {
		ServiceTracker st = new ServiceTracker(getContext(), getContext()
				.createFilter(
						"(&(" + org.osgi.framework.Constants.OBJECTCLASS + "="
								+ clazz + ")(" + SERVICE_IMPORTED + "=*))"),
				new ServiceTrackerCustomizer() {

					public Object addingService(ServiceReference reference) {
						Trace.trace(Activator.PLUGIN_ID, "addingService="
								+ reference);
						return getContext().getService(reference);
					}

					public void modifiedService(ServiceReference reference,
							Object service) {
						Trace.trace(Activator.PLUGIN_ID, "modifiedService="
								+ reference);
					}

					public void removedService(ServiceReference reference,
							Object service) {
						Trace.trace(Activator.PLUGIN_ID, "removedService="
								+ reference + ",svc=" + service);
					}
				});
		st.open();
		return st;
	}

	protected Properties getServiceProperties() {
		Properties props = new Properties();
		props.put(SERVICE_EXPORTED_CONFIGS, getServerContainerName());
		props.put(SERVICE_EXPORTED_INTERFACES,
				new String[] { SERVICE_EXPORTED_INTERFACES_WILDCARD });
		return props;
	}

	protected void assertReferenceHasCorrectType(ServiceReference sr,
			String classname) {
		String[] classes = (String[]) sr
				.getProperty(org.osgi.framework.Constants.OBJECTCLASS);
		assertTrue(classes != null);
		// Check object class
		assertTrue(classname.equals(classes[0]));
	}

	protected void assertReferencesValidAndFirstHasCorrectType(
			ServiceReference[] references, String classname) {
		assertReferencesValid(references);
		assertReferenceHasCorrectType(references[0], classname);
	}

	protected void assertReferencesValid(ServiceReference[] references) {
		assertTrue(references != null);
		assertTrue(references.length > 0);
	}

	protected void assertStringResultValid(Object result, String compare) {
		assertNotNull(result);
		assertTrue(result instanceof String);
		assertTrue(compare.equals(result));
	}
	
	protected void assertProxyValid(Object proxy) {
		assertNotNull(proxy);
		assertTrue(proxy instanceof TestServiceInterface1);
	}
	
	protected IRemoteService getRemoteServiceFromProxy(Object proxy) {
		assertTrue(proxy instanceof IRemoteServiceProxy);
		return ((IRemoteServiceProxy) proxy).getRemoteService();
	}
	
	protected IRemoteCall createRemoteCall() {
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


	public void testGetRemoteServiceReference() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client container
		ServiceTracker st = createProxyServiceTracker(classname);
		// Get service properties...and allow subclasses to override to add
		// other service properties
		Properties props = getServiceProperties();
		// Service Host: register service
		ServiceRegistration registration = registerService(classname,
				new TestService1(), props);
		// Wait
		Thread.sleep(REGISTER_WAIT);

		// Service Consumer - Get (remote) ervice references
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);
		// Spec requires that the 'service.imported' property be set
		assertTrue(remoteReferences[0].getProperty(SERVICE_IMPORTED) != null);
		
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}
	
	public void testGetRemoteServiceReferenceWithExtraProperties() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client container
		ServiceTracker st = createProxyServiceTracker(classname);
		// Get service properties...and allow subclasses to override to add
		// other service properties
		Properties props = getServiceProperties();
		// Add other properties
		props.put(TESTPROP_NAME, TESTPROP_VALUE);
		props.put(TESTPROP1_NAME,TESTPROP1_VALUE);
		// Service Host: register service
		ServiceRegistration registration = registerService(classname,
				new TestService1(), props);
		// Wait
		Thread.sleep(REGISTER_WAIT);

		// Service Consumer - Get (remote) ervice references
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);
		// Spec requires that the 'service.imported' property be set
		assertTrue(remoteReferences[0].getProperty(SERVICE_IMPORTED) != null);
		
		String testProp = (String) remoteReferences[0].getProperty(TESTPROP_NAME);
		String testProp1 = (String) remoteReferences[0].getProperty(TESTPROP1_NAME);
		assertTrue(TESTPROP_VALUE.equals(testProp));
		assertTrue(TESTPROP1_VALUE.equals(testProp1));
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}


	public void testProxy() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);

		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname,
				new TestService1(), getServiceProperties());
		Thread.sleep(REGISTER_WAIT);

		// Client - Get service references from service tracker
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);

		// Get proxy/service
		TestServiceInterface1 proxy = (TestServiceInterface1) getContext()
				.getService(remoteReferences[0]);
		assertNotNull(proxy);
		// Now use proxy
		String result = proxy.doStuff1();
		Trace.trace(Activator.PLUGIN_ID, "proxy.doStuff1 result=" + result);
		assertTrue(TestServiceInterface1.TEST_SERVICE_STRING1.equals(result));

		// Unregister on server and wait
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testCallSyncFromProxy() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);

		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname,
				new TestService1(), getServiceProperties());
		Thread.sleep(REGISTER_WAIT);

		// Client - Get service references from service tracker
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);

		// Get proxy
		TestServiceInterface1 proxy = (TestServiceInterface1) getContext()
				.getService(remoteReferences[0]);

		assertProxyValid(proxy);
		
		// Get IRemoteService from proxy
		IRemoteService remoteService = getRemoteServiceFromProxy(proxy);

		// Call remote service synchronously
		Object result = remoteService.callSync(createRemoteCall());
		Trace.trace(Activator.PLUGIN_ID, "proxy.doStuff1 result=" + result);
		assertStringResultValid(result, TestServiceInterface1.TEST_SERVICE_STRING1);
		
		// Unregister on server and wait
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testCallSync() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);

		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname,
				new TestService1(), getServiceProperties());
		Thread.sleep(REGISTER_WAIT);

		// Client - Get service references from service tracker
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);

		Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		IRemoteService rs = (IRemoteService) o;

		// Call synchronously
		Object result = rs.callSync(createRemoteCall());
		Trace.trace(Activator.PLUGIN_ID, "callSync.doStuff1 result=" + result);
		assertStringResultValid(result, TestServiceInterface1.TEST_SERVICE_STRING1);

		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testCallAsync() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);

		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname,
				new TestService1(), getServiceProperties());
		Thread.sleep(REGISTER_WAIT);

		// Client - Get service references from service tracker
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValid(remoteReferences);

		Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		IRemoteService rs = (IRemoteService) o;
		// Call asynchronously
		rs.callAsync(createRemoteCall(), new IRemoteCallListener() {
			public void handleEvent(IRemoteCallEvent event) {
				if (event instanceof IRemoteCallCompleteEvent) {
					Object result = ((IRemoteCallCompleteEvent) event)
							.getResponse();
					Trace.trace(Activator.PLUGIN_ID,
							"callSync.doStuff1 result=" + result);
					assertStringResultValid(result,TestServiceInterface1.TEST_SERVICE_STRING1);
					syncNotify();
				}
			}
		});

		syncWaitForNotify(REGISTER_WAIT);
		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testCallFuture() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);

		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname,
				new TestService1(), getServiceProperties());
		Thread.sleep(REGISTER_WAIT);

		// Client - Get service references from service tracker
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValid(remoteReferences);

		Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		IRemoteService rs = (IRemoteService) o;
		// Call asynchronously
		IFuture futureResult = rs.callAsync(createRemoteCall());

		// now get result from futureResult
		Object result = futureResult.get();
		Trace.trace(Activator.PLUGIN_ID, "callSync.doStuff1 result=" + result);
		assertStringResultValid(result, TestServiceInterface1.TEST_SERVICE_STRING1);

		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

	public void testFireAsync() throws Exception {
		String classname = TestServiceInterface1.class.getName();
		// Setup service tracker for client
		ServiceTracker st = createProxyServiceTracker(classname);

		// Actually register and wait a while
		ServiceRegistration registration = registerService(classname,
				new TestService1(), getServiceProperties());
		Thread.sleep(REGISTER_WAIT);

		// Client - Get service references from service tracker
		ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValid(remoteReferences);

		Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		IRemoteService rs = (IRemoteService) o;
		// Call asynchronously
		rs.fireAsync(createRemoteCall());
		Thread.sleep(5000);
		// Unregister on server
		registration.unregister();
		st.close();
		Thread.sleep(REGISTER_WAIT);
	}

}