public class DiscoveryTest extends TestCase {

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

package org.eclipse.ecf.tests.discovery;

import java.net.InetAddress;
import java.util.Properties;

import junit.framework.TestCase;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.ServiceID;

public class JMDNSDiscoveryTest extends TestCase {
	
	static IContainer container = null;
	static IDiscoveryContainerAdapter discoveryContainer = null;
	static final String TEST_SERVICE_TYPE = "_ecftcp._tcp.local.";
	static final String TEST_PROTOCOL = "ecftcp";
	static final String TEST_HOST = "localhost";
	static final int TEST_PORT = 3282;
	static final String TEST_SERVICE_NAME = System.getProperty("user.name") + "." + TEST_PROTOCOL;
	
	public void testContainerCreate() throws Exception {
		container = ContainerFactory.getDefault().createContainer(
		"ecf.discovery.jmdns");
		assertNotNull(container);
	}
	
	public void testContainerConnect() throws Exception {
		container.connect(null, null);		
	}
	public void testDiscoveryContainerAdapter() throws Exception {
		discoveryContainer = (IDiscoveryContainerAdapter) container
		.getAdapter(IDiscoveryContainerAdapter.class);		
		assertNotNull(discoveryContainer);
	}
	
	public void testAddServiceTypeListener() throws Exception {
		discoveryContainer
		.addServiceTypeListener(new CollabServiceTypeListener());
	}
	
	public void testRegisterServiceType() throws Exception {
		discoveryContainer.registerServiceType(TEST_SERVICE_TYPE);
		System.out.println("registered service type "+TEST_SERVICE_TYPE+" waiting 5s");
		Thread.sleep(5000);
	}
	
	public void testRegisterService() throws Exception {
		Properties props = new Properties();
		String protocol = TEST_PROTOCOL;
		InetAddress host = InetAddress.getByName(TEST_HOST);
		int port = TEST_PORT;
		String svcName = System.getProperty("user.name") + "."
				+ protocol;
		ServiceInfo svcInfo = new ServiceInfo(host, new ServiceID(
				TEST_SERVICE_TYPE, svcName), port,
				0, 0, new ServiceProperties(props));
		discoveryContainer.registerService(svcInfo);
	}
	public final void testDiscovery() throws Exception {
		
		System.out.println("Discovery started.  Waiting 10s for discovered services");
		Thread.sleep(10000);
	}

	class CollabServiceTypeListener implements IServiceTypeListener {
		public void serviceTypeAdded(IServiceEvent event) {
			System.out.println("serviceTypeAdded(" + event + ")");
			ServiceID svcID = event.getServiceInfo().getServiceID();
			discoveryContainer.addServiceListener(svcID.getServiceType(),
					new CollabServiceListener());
			discoveryContainer.registerServiceType(svcID.getServiceType());
		}
	}
	class CollabServiceListener implements IServiceListener {
		public void serviceAdded(IServiceEvent event) {
			System.out.println("serviceAdded(" + event + ")");
			discoveryContainer.requestServiceInfo(event.getServiceInfo()
					.getServiceID(), 3000);
		}
		public void serviceRemoved(IServiceEvent event) {
			System.out.println("serviceRemoved(" + event + ")");
		}
		public void serviceResolved(IServiceEvent event) {
			System.out.println("serviceResolved(" + event + ")");
		}
	}

}