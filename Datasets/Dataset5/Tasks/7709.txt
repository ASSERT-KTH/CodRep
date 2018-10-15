public class RemoteServiceContainerAdapterTest extends AbstractRemoteServiceTestCase {

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.tests.remoteservice;

import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteCallListener;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.remoteservice.events.IRemoteCallEvent;

public class RemoteContainerTest extends AbstractRemoteServiceTestCase {

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		setClientCount(2);
		createServerAndClients();
		connectClients();
		setupRemoteServiceAdapters();
		addRemoteServiceListeners();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		cleanUpServerAndClients();
		super.tearDown();
	}

	public void testRemoteServiceAdapters() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		assertNotNull(adapters);
		for (int i = 0; i < adapters.length; i++)
			assertNotNull(adapters[i]);
	}

	protected Object createService() {
		return new IConcatService() {
			public String concat(String string1, String string2) {
				final String result = string1.concat(string2);
				System.out.println("SERVICE.concat(" + string1 + "," + string2 + ") returning " + result);
				return string1.concat(string2);
			}
		};
	}

	public void testRegisterService() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// adapter [0] is the service 'server'
		final IRemoteServiceRegistration reg = registerService(adapters[0], IConcatService.class.getName(), createService(), 1500);
		assertNotNull(reg);
		assertNotNull(reg.getContainerID());
	}

	public void testUnregisterService() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// adapter [0] is the service 'server'
		final IRemoteServiceRegistration reg = registerService(adapters[0], IConcatService.class.getName(), createService(), 1500);
		assertNotNull(reg);
		assertNotNull(reg.getContainerID());

		reg.unregister();

	}

	public void testGetServiceReference() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		registerService(adapters[0], IConcatService.class.getName(), createService(), 3000);

		final IRemoteServiceReference[] refs = getRemoteServiceReferences(adapters[1], IConcatService.class.getName());

		assertNotNull(refs);
		assertTrue(refs.length > 0);
	}

	public void testGetService() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		assertNotNull(service);
	}

	protected IRemoteCall createRemoteConcat(String first, String second) {
		return createRemoteCall("concat", new Object[] {first, second});
	}

	protected IRemoteService registerAndGetRemoteService() {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		return registerAndGetRemoteService(adapters[0], adapters[1], IConcatService.class.getName(), 1500);

	}

	protected IRemoteCallListener createRemoteCallListener() {
		return new IRemoteCallListener() {
			public void handleEvent(IRemoteCallEvent event) {
				System.out.println("CLIENT.handleEvent(" + event + ")");
			}
		};
	}

	public void testCallSynch() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		System.out.println("CLIENT.callSynch start");
		final Object result = service.callSynch(createRemoteConcat("Eclipse ", "is cool"));
		System.out.println("CLIENT.callSynch end. result=" + result);
		assertNotNull(result);
		assertTrue(result.equals("Eclipse ".concat("is cool")));
	}

	public void testBadCallSynch() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		// Following should throw exception because "concat1" method does not exist
		try {
			service.callSynch(createRemoteCall("concat1", new Object[] {"first", "second"}));
			fail();
		} catch (final ECFException e) {
			// Exception should occur
		}

		// Following should throw exception because wrong number of params for concat	
		try {
			service.callSynch(createRemoteCall("concat", new Object[] {"first"}));
			fail();
		} catch (final ECFException e) {
			// Exception should occur
		}

	}

	public void testCallAsynch() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		System.out.println("CLIENT.callAsynch start");
		service.callAsynch(createRemoteConcat("ECF ", "is cool"), createRemoteCallListener());
		System.out.println("CLIENT.callAsynch end");
		sleep(1500);
	}

	public void testFireAsynch() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		System.out.println("CLIENT.fireAsynch start");
		service.fireAsynch(createRemoteConcat("Eclipse ", "sucks"));
		System.out.println("CLIENT.fireAsynch end");

		sleep(1500);
	}

	public void testProxy() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		final IConcatService proxy = (IConcatService) service.getProxy();
		assertNotNull(proxy);
		System.out.println("CLIENT.proxy start");
		final String result = proxy.concat("ECF ", "sucks");
		System.out.println("CLIENT.proxy end. result=" + result);
		sleep(1500);
	}

}