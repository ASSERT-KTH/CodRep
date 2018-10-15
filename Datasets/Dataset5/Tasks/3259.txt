protected static final int REGISTER_WAIT = Integer.parseInt(System.getProperty("waittime","30000"));

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
import org.eclipse.ecf.remoteservice.events.IRemoteCallCompleteEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteCallEvent;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.Activator;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.util.tracker.ServiceTracker;

public abstract class AbstractRemoteServiceAccessTest extends
		AbstractDistributionTest {

	protected static final int REGISTER_WAIT = Integer.parseInt(System.getProperty("waittime","15000"));

	private final String classname = TestServiceInterface1.class.getName();
	private ServiceTracker st;
	private ServiceRegistration registration;

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.osgi.services.distribution.AbstractDistributionTest#tearDown()
	 */
	protected void tearDown() throws Exception {
		// Unregister on server
		if (registration != null) {
			registration.unregister();
			registration = null;
		}
		if (st != null) {
			st.close();
			st = null;
		}
		Thread.sleep(REGISTER_WAIT);

		super.tearDown();
	}

	protected void createServiceTrackerAndRegister(final Properties props) throws Exception {
		// Setup service tracker for client
		st = createProxyServiceTracker(classname);

		// Actually register
		registration = registerService(classname,
				new TestService1(), props);

		// Wait
		Thread.sleep(REGISTER_WAIT);
	}

	protected void createServiceTrackerAndRegister() throws Exception {
		createServiceTrackerAndRegister(getServiceProperties());
	}

	protected Properties getServiceProperties() {
		final Properties props = new Properties();
		props.put(SERVICE_EXPORTED_CONFIGS, getServerContainerName());
		props.put(SERVICE_EXPORTED_INTERFACES, SERVICE_EXPORTED_INTERFACES_WILDCARD);
		return props;
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
		startTest("testGetRemoteServiceReference");
		createServiceTrackerAndRegister();
		
		// Service Consumer - Get (remote) ervice references
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);
		// Spec requires that the 'service.imported' property be set
		assertTrue(remoteReferences[0].getProperty(SERVICE_IMPORTED) != null);
		endTest("testGetRemoteServiceReference");
	}
	
	public void testGetRemoteServiceReferenceWithExtraProperties() throws Exception {
		startTest("testGetRemoteServiceReferenceWithExtraProperties");
		final String TESTPROP1_VALUE = "baz";
		final String TESTPROP_VALUE = "foobar";
		final String TESTPROP1_NAME = "org.eclipse.ecf.testprop1";
		final String TESTPROP_NAME = "org.eclipse.ecf.testprop";

		final Properties props = getServiceProperties();
		// Add other properties
		props.put(TESTPROP_NAME, TESTPROP_VALUE);
		props.put(TESTPROP1_NAME,TESTPROP1_VALUE);
		createServiceTrackerAndRegister(props);

		// Service Consumer - Get (remote) ervice references
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);
		// Spec requires that the 'service.imported' property be set
		assertTrue(remoteReferences[0].getProperty(SERVICE_IMPORTED) != null);
		
		final String testProp = (String) remoteReferences[0].getProperty(TESTPROP_NAME);
		final String testProp1 = (String) remoteReferences[0].getProperty(TESTPROP1_NAME);
		assertTrue(TESTPROP_VALUE.equals(testProp));
		assertTrue(TESTPROP1_VALUE.equals(testProp1));
		endTest("testGetRemoteServiceReferenceWithExtraProperties");
	}


	public void testProxy() throws Exception {
		startTest("testProxy");
		createServiceTrackerAndRegister();
		
		// Client - Get service references from service tracker
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);

		// Get proxy/service
		final TestServiceInterface1 proxy = (TestServiceInterface1) getContext()
				.getService(remoteReferences[0]);
		assertNotNull(proxy);
		// Now use proxy
		final String result = proxy.doStuff1();
		Trace.trace(Activator.PLUGIN_ID, "proxy.doStuff1 result=" + result);
		assertTrue(TestServiceInterface1.TEST_SERVICE_STRING1.equals(result));
		endTest("testProxy");
	}

	public void testCallSyncFromProxy() throws Exception {
		startTest("testCallSyncFromProxy");
		createServiceTrackerAndRegister();
		
		// Client - Get service references from service tracker
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);

		// Get proxy
		final TestServiceInterface1 proxy = (TestServiceInterface1) getContext()
				.getService(remoteReferences[0]);

		assertProxyValid(proxy);
		
		// Get IRemoteService from proxy
		final IRemoteService remoteService = getRemoteServiceFromProxy(proxy);

		// Call remote service synchronously
		final Object result = remoteService.callSync(createRemoteCall());
		Trace.trace(Activator.PLUGIN_ID, "proxy.doStuff1 result=" + result);
		assertStringResultValid(result, TestServiceInterface1.TEST_SERVICE_STRING1);
		endTest("testCallSyncFromProxy");
	}

	public void testCallSync() throws Exception {
		startTest("testCallSync");
		createServiceTrackerAndRegister();
		
		// Client - Get service references from service tracker
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValidAndFirstHasCorrectType(remoteReferences, classname);

		final Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		final IRemoteService rs = (IRemoteService) o;

		// Call synchronously
		final Object result = rs.callSync(createRemoteCall());
		Trace.trace(Activator.PLUGIN_ID, "callSync.doStuff1 result=" + result);
		assertStringResultValid(result, TestServiceInterface1.TEST_SERVICE_STRING1);
		endTest("testCallSync");
	}

	public void testCallAsync() throws Exception {
		startTest("testCallAsync");
		createServiceTrackerAndRegister();
		
		// Client - Get service references from service tracker
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValid(remoteReferences);

		final Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		final IRemoteService rs = (IRemoteService) o;
		// Call asynchronously
		rs.callAsync(createRemoteCall(), new IRemoteCallListener() {
			public void handleEvent(final IRemoteCallEvent event) {
				if (event instanceof IRemoteCallCompleteEvent) {
					final Object result = ((IRemoteCallCompleteEvent) event)
							.getResponse();
					Trace.trace(Activator.PLUGIN_ID,
							"callSync.doStuff1 result=" + result);
					assertStringResultValid(result,TestServiceInterface1.TEST_SERVICE_STRING1);
					syncNotify();
				}
			}
		});

		syncWaitForNotify(REGISTER_WAIT);
		endTest("testCallAsync");
	}

	public void testCallFuture() throws Exception {
		startTest("testCallFuture");
		createServiceTrackerAndRegister();
		
		// Client - Get service references from service tracker
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValid(remoteReferences);

		final Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		final IRemoteService rs = (IRemoteService) o;
		// Call asynchronously
		final IFuture futureResult = rs.callAsync(createRemoteCall());

		// now get result from futureResult
		final Object result = futureResult.get();
		Trace.trace(Activator.PLUGIN_ID, "callSync.doStuff1 result=" + result);
		assertStringResultValid(result, TestServiceInterface1.TEST_SERVICE_STRING1);
		endTest("testCallFuture");
	}

	public void testFireAsync() throws Exception {
		startTest("testFireAsync");
		createServiceTrackerAndRegister();
		
		// Client - Get service references from service tracker
		final ServiceReference[] remoteReferences = st.getServiceReferences();
		assertReferencesValid(remoteReferences);

		final Object o = remoteReferences[0].getProperty(SERVICE_IMPORTED);
		assertNotNull(o);
		assertTrue(o instanceof IRemoteService);
		final IRemoteService rs = (IRemoteService) o;
		// Call asynchronously
		rs.fireAsync(createRemoteCall());
		Thread.sleep(REGISTER_WAIT);
		endTest("testFireAsync");
	}
}