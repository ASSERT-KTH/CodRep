Thread.sleep(10000);

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
import java.util.Dictionary;
import java.util.Hashtable;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.osgi.services.discovery.ECFServicePublication;
import org.eclipse.ecf.osgi.services.distribution.ECFServiceConstants;
import org.eclipse.ecf.tests.ECFAbstractTestCase;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.Activator;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;
import org.osgi.service.discovery.ServicePublication;
import org.osgi.util.tracker.ServiceTracker;

public abstract class AbstractServicePublicationTest extends ECFAbstractTestCase implements ECFServiceConstants, ECFServicePublication {

	protected static void assertStringsEqual(final String[] s1, final String[] s2) {
		assertEquals(s1.length, s2.length);
		for (int i = 0; i < s1.length; i++) {
			assertEquals(s1[i], s2[i]);
		}
	}

	// Member variables that should be set by subclasses
	protected IContainer container;
	protected String[] ifaces;

	protected abstract IContainer createContainer() throws Exception;
	protected abstract String[] createInterfaces() throws Exception;


	protected void setUp() throws Exception {
		super.setUp();
		setContainer(createContainer());
		setInterfaces(createInterfaces());
	}
	
	protected void tearDown() throws Exception {
		super.tearDown();
		if (container != null) {
			container.dispose();
			container = null;
		}
		if (ifaces != null) {
			ifaces = null;
		}
	}
	
	public IContainer getContainer() {
		return container;
	}
	
	public String[] getInterfaces() {
		return ifaces;
	}
	
	public void setContainer(IContainer container) {
		this.container = container;
	}
	
	public void testServicePublication() throws InterruptedException {
		final BundleContext context = Activator.getDefault().getContext();
	
		// register a service with the marker property set
		final Dictionary props = new Hashtable();
		props.put(ECFServiceConstants.OSGI_REMOTE_INTERFACES, getInterfaces());
		// prepare a service tracker
		final ServiceTracker tracker = new ServiceTracker(context,
				TestServiceInterface1.class.getName(), null);
		tracker.open();
	
		// register the (remote-enabled) service
		context.registerService(TestServiceInterface1.class.getName(),
				new TestService1(), props);
	
		// wait for service to become registered
		tracker.waitForService(1000);
	
		// expected behavior: an endpoint is published
		final ServiceReference ref = context
				.getServiceReference(ServicePublication.class.getName());
		assertTrue(ref != null);
		// check the service publication properties
		final Object o = ref
				.getProperty(ServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME);
		assertTrue(o instanceof Collection);
		final Collection refIfaces = (Collection) o;
		assertStringsEqual(getInterfaces(), (String []) refIfaces.toArray(new String[] {}));
		Thread.sleep(50000);
	}
	public void setInterfaces(String [] interfaces) {
		this.ifaces = interfaces;
	}
}