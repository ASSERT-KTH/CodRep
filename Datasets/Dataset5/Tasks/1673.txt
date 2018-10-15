return Generic.CONSUMER_CONTAINER_TYPE;

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

package org.eclipse.ecf.tests.remoteservice.generic;

import java.util.Dictionary;
import java.util.Hashtable;

import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.tests.remoteservice.AbstractRemoteServiceTest;
import org.eclipse.ecf.tests.remoteservice.Activator;
import org.eclipse.ecf.tests.remoteservice.IConcatService;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

public class TransparentProxyTest extends AbstractRemoteServiceTest {

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
		super.tearDown();
	}

	public void testTransparentProxy() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClients()[1].getConnectedID());
		props.put(Constants.AUTOREGISTER_REMOTE_PROXY, "true");
		// Register
		adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(2000);

		final BundleContext bc = Activator.getDefault().getContext();
		assertNotNull(bc);
		final ServiceReference ref = bc.getServiceReference(IConcatService.class.getName());
		assertNotNull(ref);
		final IConcatService concatService = (IConcatService) bc.getService(ref);
		assertNotNull(concatService);
		System.out.println("proxy call start");
		final String result = concatService.concat("OSGi ", "is cool");
		System.out.println("proxy call end. result=" + result);
		bc.ungetService(ref);
	}

	/*
	public void testIRemoteService() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClients()[1].getConnectedID());
		props.put(Constants.AUTOREGISTER_REMOTE_PROXY, "true");
		// Register
		adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(3000);

		final BundleContext bc = Activator.getDefault().getContext();
		assertNotNull(bc);
		final ServiceReference ref = bc.getServiceReference(IConcatService.class.getName());
		assertNotNull(ref);
		final IRemoteService remoteService = (IRemoteService) ref.getProperty(Constants.REMOTE_SERVICE);
		assertNotNull(remoteService);
		// Call it asynch with listener
		remoteService.callAsynch(createRemoteConcat("OSGi ", "Sucks (sic)"), createRemoteCallListener());
		sleep(3000);
	}
	*/
}