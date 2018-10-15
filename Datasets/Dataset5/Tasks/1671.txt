return Generic.CONSUMER_CONTAINER_TYPE;

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.tests.remoteservice.generic;

import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.util.tracker.RemoteServiceTracker;
import org.eclipse.ecf.tests.remoteservice.AbstractServiceTrackerTest;

/**
 *
 */
public class RemoteServiceTrackerTest extends AbstractServiceTrackerTest {

	RemoteServiceTracker remoteServiceTracker;
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.remoteservice.AbstractRemoteServiceTest#getClientContainerName()
	 */
	protected String getClientContainerName() {
		return Generic.CLIENT_CONTAINER_NAME;
	}

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
		if (remoteServiceTracker != null) {
			remoteServiceTracker.close();
		}
		super.tearDown();
	}

	protected IRemoteService getRemoteService(IRemoteServiceContainerAdapter adapter, String clazz, String filter) {
		remoteServiceTracker = new RemoteServiceTracker(adapter, null, clazz, null);
		assertNotNull(remoteServiceTracker);
		remoteServiceTracker.open();
		return remoteServiceTracker.getRemoteService();
	}

/*
	public void testRemoteServiceTracker() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		// Register
		adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(3000);

		final RemoteServiceTracker st = new RemoteServiceTracker(adapters[1], null, IConcatService.class.getName(), null);
		assertNotNull(st);
		st.open();
		IRemoteService rs = st.getRemoteService();
		final IConcatService concatService = (IConcatService) rs.getProxy();
		assertNotNull(concatService);
		System.out.println("proxy call start");
		final String result = concatService.concat("OSGi ", "is cool");
		System.out.println("proxy call end. result=" + result);
		sleep(3000);
		st.close();
		sleep(3000);
	}
*/
}