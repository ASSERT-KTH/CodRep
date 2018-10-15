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

package org.eclipse.ecf.tests.remoteservice.presence;

import java.util.Dictionary;
import java.util.Hashtable;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.IAsyncResult;
import org.eclipse.ecf.remoteservice.Constants;
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
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClients()[1].getConnectedID());
		// Register
		final IRemoteServiceRegistration result = adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(1500);

		final IRemoteServiceRegistration reg = result;
		assertNotNull(reg);
		assertNotNull(reg.getContainerID());
	}

	public void testUnregisterService() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClients()[1].getConnectedID());
		// Register
		final IRemoteServiceRegistration reg = adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(1500);

		assertNotNull(reg);
		assertNotNull(reg.getContainerID());

		reg.unregister();

	}

	public void testGetServiceReference() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClients()[1].getConnectedID());
		// Register
		adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(1500);

		final IRemoteServiceReference[] refs = adapters[1].getRemoteServiceReferences(null, IConcatService.class.getName(), null);

		assertNotNull(refs);
		assertTrue(refs.length == 1);
	}

	public void testGetService() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();

		assertNotNull(service);
	}

	protected IRemoteCall createRemoteConcat(String first, String second) {
		return createRemoteCall("concat", new Object[] {first, second});
	}

	protected IRemoteCall createBogus(String first, String second) {
		return createRemoteCall("bogus", new Object[] {first, second});
	}

	protected IRemoteService registerAndGetRemoteService() {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final ID targetID = getClients()[1].getConnectedID();
		final String serviceName = IConcatService.class.getName();
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, targetID);
		adapters[0].registerRemoteService(new String[] {serviceName}, createService(), props);
		sleep(1500);
		final IRemoteServiceContainerAdapter adapter = adapters[1];
		final IRemoteServiceReference[] refs = adapter.getRemoteServiceReferences(null, serviceName, null);
		if (refs.length == 0)
			return null;
		return adapter.getRemoteService(refs[0]);

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

	public void testAsyncResult() throws Exception {
		final IRemoteService service = registerAndGetRemoteService();
		System.out.println("CLIENT.asyncResult start");
		final IAsyncResult result = service.callAsynch(createRemoteConcat("ECF AsynchResults ", "are cool"));
		assertNotNull(result);
		sleep(2500);
		System.out.println("CLIENT.asyncResult end. result=" + result.get());
	}

}