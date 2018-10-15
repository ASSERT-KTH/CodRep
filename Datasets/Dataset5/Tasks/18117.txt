System.out.println("proxy call end. result=" + result);

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

import java.util.Dictionary;
import java.util.Hashtable;

import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;

public class ServiceReferenceTest extends AbstractRemoteServiceTestCase {

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

	protected Object createService() {
		return new IConcatService() {
			public String concat(String string1, String string2) {
				final String result = string1.concat(string2);
				System.out.println("SERVICE.concat(" + string1 + "," + string2 + ") returning " + result);
				return string1.concat(string2);
			}
		};
	}

	public void testGetServiceReference() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		// client [0]/adapter[0] is the service 'server'
		// client [1]/adapter[1] is the service target (client)
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClients()[1].getConnectedID());
		props.put(Constants.LOCAL_SERVICE_REGISTRATION, "true");
		// Register
		adapters[0].registerRemoteService(new String[] {IConcatService.class.getName()}, createService(), props);
		// Give some time for propagation
		sleep(1500);

		final BundleContext bc = Activator.getDefault().getContext();
		assertNotNull(bc);
		final ServiceReference ref = bc.getServiceReference(IConcatService.class.getName());
		assertNotNull(ref);
		final IConcatService concatService = (IConcatService) bc.getService(ref);
		assertNotNull(concatService);
		System.out.println("proxy call start");
		final String result = concatService.concat("OSGi ", "is cool");
		System.out.println("CLIENT.proxy end. result=" + result);
		sleep(1500);
	}

}