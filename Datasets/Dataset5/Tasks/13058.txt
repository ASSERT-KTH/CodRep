super("ecf.discovery.jmdns");

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
package org.eclipse.ecf.tests.provider.jmdns;

import java.net.InetAddress;
import java.net.URI;
import java.util.Date;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceTypeEvent;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.ecf.provider.jmdns.identity.JMDNSNamespace;
import org.eclipse.ecf.tests.discovery.DiscoveryTest;

public class JMDNSDiscoveryServiceTest extends DiscoveryTest {

	static final String TEST_SERVICE_TYPE = "_http._tcp.local.";
	static final int TEST_PORT = 3282;

	public JMDNSDiscoveryServiceTest() {
		super("ecf.discovery.jmdns", 1000);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		assertNotNull(containerUnderTest);
		assertTrue(containerUnderTest.equals("ecf.discovery.jmdns"));

		container = ContainerFactory.getDefault().createContainer(containerUnderTest);
		assertNotNull(container);
		discoveryContainer = getAdapter(IDiscoveryContainerAdapter.class);
		assertNotNull(discoveryContainer);

		final URI uri = new URI(JMDNSNamespace.JMDNS_SCHEME, null, InetAddress.getLocalHost().getHostAddress(), TEST_PORT, null, null, null);

		serviceID = ServiceIDFactory.getDefault().createServiceID(discoveryContainer.getServicesNamespace(), TEST_SERVICE_TYPE, new Date().getTime() + "");
		assertNotNull(serviceID);
		final ServiceProperties serviceProperties = new ServiceProperties();
		serviceProperties.setPropertyString("serviceProperties", "serviceProperties");
		serviceInfo = new ServiceInfo(uri, createServiceID(TEST_SERVICE_TYPE, "slewis" + System.currentTimeMillis()), 0, 0, serviceProperties);
		assertNotNull(serviceInfo);

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		container.disconnect();
		container.dispose();
		container = null;
		discoveryContainer = null;
	}

	class ServiceTypeListener implements IServiceTypeListener {

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceTypeListener#serviceTypeDiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceTypeDiscovered(IServiceTypeEvent event) {
			System.out.println("serviceTypeDiscovered(" + event + ")");
		}

	}

	class ServiceListener implements IServiceListener {
		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceListener#serviceDiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceDiscovered(IServiceEvent anEvent) {
			System.out.println("serviceDiscovered(" + anEvent + ")");
		}

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceListener#serviceUndiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceUndiscovered(IServiceEvent anEvent) {
			System.out.println("serviceUndiscovered(" + anEvent + ")");
		}
	}

}