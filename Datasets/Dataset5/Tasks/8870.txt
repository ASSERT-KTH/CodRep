props.put(IServicePublication.SERVICE_INTERFACE_NAME, interfaces);

/*******************************************************************************
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.osgi.services.discovery;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Properties;

import junit.framework.TestCase;

import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.osgi.services.discovery.IServicePublication;
import org.eclipse.ecf.tests.internal.osgi.discovery.Activator;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.discovery.DiscoveredServiceNotification;
import org.osgi.service.discovery.ServicePublication;
import org.osgi.service.discovery.DiscoveredServiceTracker;

public class PublishTest extends TestCase {

	BundleContext context;
	List serviceRegistrations = new ArrayList();
	
	protected void setUp() throws Exception {
		super.setUp();
		context = Activator.getDefault().getContext();
	}
	
	protected void tearDown() throws Exception {
		super.tearDown();
		for(Iterator i=serviceRegistrations.iterator(); i.hasNext(); ) {
			ServiceRegistration reg = (ServiceRegistration) i.next();
			reg.unregister();
		}
		context = null;
	}
	
	class TestServicePublication implements IServicePublication {

		public ServiceReference getReference() {
			// TODO Auto-generated method stub
			return null;
		}
		
	}
	
	class DiscoveredServiceTrackerImpl implements DiscoveredServiceTracker {

		public void serviceChanged(DiscoveredServiceNotification notification) {
			Trace.trace(Activator.BUNDLE_NAME, "DiscoveredServiceTrackerImpl.serviceChanged("+notification+")");
		}
		
	}
	
	protected Properties createServicePublicationProperties(List interfaces) {
		Properties props = new Properties();
		props.put(IServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME, interfaces);
		return props;
	}
	
	protected ServicePublication createServicePublication() {
		return new TestServicePublication();
	}
	
	protected DiscoveredServiceTracker createDiscoveredServiceTracker() {
		return new DiscoveredServiceTrackerImpl();
	}
	
	public void testDiscoveryTrackerPublish() throws Exception {
		serviceRegistrations.add(context.registerService(DiscoveredServiceTracker.class.getName(), createDiscoveredServiceTracker(), null));
	}
	
	public void testServicePublish() throws Exception {
	    List interfaces = new ArrayList();
	    interfaces.add("foo.bar");
		serviceRegistrations.add(context.registerService(ServicePublication.class.getName(), createServicePublication(), createServicePublicationProperties(interfaces)));
		Thread.sleep(5000);
	}
	
	public void testDiscoveryTrackerAndServicePublish() throws Exception {
		testDiscoveryTrackerPublish();
		testServicePublish();
	}
}