uri = DiscoveryTestHelper.createDefaultURI(DiscoveryTestHelper.HOSTNAME);

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.tests.discovery;

import java.net.URI;
import java.util.Comparator;

import junit.framework.TestCase;

import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;

/**
 * 
 */
public abstract class ServiceInfoTest extends TestCase {

	protected URI uri;
	protected IServiceTypeID serviceTypeID;
	protected int priority;
	protected int weight;
	protected IServiceProperties serviceProperties;
	protected IServiceInfo serviceInfo;
	protected Comparator serviceInfoComparator = new ServiceInfoComparator();

	public ServiceInfoTest(Namespace namespace) {
		uri = DiscoveryTestHelper.createDefaultURI();
		priority = DiscoveryTestHelper.PRIORITY;
		weight = DiscoveryTestHelper.WEIGHT;
		serviceProperties = new ServiceProperties();
		serviceProperties.setProperty("foobar", new String("foobar"));
		serviceProperties.setPropertyBytes("foobar1", new byte[] { 1, 2, 3 });
		try {
			serviceTypeID = ServiceIDFactory.getDefault().createServiceTypeID(namespace, DiscoveryTestHelper.SERVICES, DiscoveryTestHelper.PROTOCOLS);
		} catch (IDCreateException e) {
			fail(e.getMessage());
		}

		serviceInfo = new ServiceInfo(uri, DiscoveryTestHelper.SERVICENAME, serviceTypeID, priority, weight,
				serviceProperties);
	}

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		assertNotNull(uri);
		assertNotNull(serviceTypeID);
		assertNotNull(serviceProperties);
		assertNotNull(serviceInfo);
		assertNotNull(serviceInfoComparator);
	}

	/**
	 * Test method for {@link org.eclipse.ecf.discovery.ServiceInfo#getLocation()}.
	 */
	public void testGetLocation() {
		assertEquals(serviceInfo.getServiceID().getLocation(), uri);
	}

	/**
	 * Test method for {@link org.eclipse.ecf.discovery.ServiceInfo#getServiceID()}.
	 */
	public void testGetServiceID() {
		assertNotNull(serviceInfo.getServiceID());
		assertEquals(serviceInfo.getServiceID().getServiceTypeID(), serviceTypeID);
	}

	/**
	 * Test method for {@link org.eclipse.ecf.discovery.ServiceInfo#getPriority()}.
	 */
	public void testGetPriority() {
		assertTrue(serviceInfo.getPriority() == priority);
	}

	/**
	 * Test method for {@link org.eclipse.ecf.discovery.ServiceInfo#getWeight()}.
	 */
	public void testGetWeight() {
		assertTrue(serviceInfo.getWeight() == weight);
	}

	/**
	 * Test method for {@link org.eclipse.ecf.discovery.ServiceInfo#getServiceProperties()}.
	 */
	public void testGetServiceProperties() {
		final IServiceProperties sprops = serviceInfo.getServiceProperties();
		assertEquals(sprops, serviceProperties);
	}

	/**
	 * Test method for {@link java.lang.Object#hashCode()}.
	 */
//	public void testHashCode() {
//		fail("Not yet implemented. How should equality be defined anyway?");
//	}

	/**
	 * Test method for {@link java.lang.Object#equals(java.lang.Object)}.
	 */
//	public void testEquals() {
//		fail("Not yet implemented. How should equality be defined anyway?");
//	}

	/**
	 * Test method for {@link org.eclipse.ecf.discovery.ServiceInfo}.
	 */
	public void testServiceInfo() {
		IServiceInfo si = null;
		try {
			si = getServiceInfo(serviceInfo);
		} catch (final SecurityException e) {
			fail();
		}
		assertTrue(serviceInfoComparator.compare(si, serviceInfo) == 0);
	}

	protected IServiceInfo getServiceInfo(IServiceInfo aServiceInfo) {
		return serviceInfo;
	}
}