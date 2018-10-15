final URI uri = createDefaultURI();

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

import java.net.URI;
import java.util.Comparator;
import java.util.Properties;

import org.eclipse.core.runtime.AssertionFailedException;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceTypeEvent;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.identity.IServiceTypeID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.ecf.tests.discovery.listener.TestListener;

public abstract class DiscoveryTest extends AbstractDiscoveryTest {

	protected IServiceInfo serviceInfo;
	protected IServiceID serviceID;
	protected IServiceInfo serviceInfo2;
	protected IServiceID serviceID2;
	protected IServiceInfo serviceInfo3;
	protected IServiceID serviceID3;

	/**
	 * @param name
	 * @param aDiscoveryContainerInterval 
	 * @param aComparator 
	 */
	public DiscoveryTest(String name, long aDiscoveryContainerInterval, Comparator aComparator) {
		containerUnderTest = name;
		comparator = aComparator;
		// interval how often the provider discovers for services + 1/10 * discoveryInterval
		waitTimeForProvider = aDiscoveryContainerInterval + (aDiscoveryContainerInterval * 1 / 2);
	}

	public DiscoveryTest(String name, long aDiscoveryContainerInterval) {
		this(name, aDiscoveryContainerInterval, new ServiceInfoComparator());
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		assertNotNull(containerUnderTest);
		assertTrue(containerUnderTest.startsWith("ecf.discovery."));

		container = ContainerFactory.getDefault().createContainer(containerUnderTest);
		discoveryContainer = getAdapter(IDiscoveryContainerAdapter.class);

		assertNotNull(container);
		assertNotNull(discoveryContainer);

		final Properties props = new Properties();
		final URI uri = new URI(ITestConstants.URI);

		serviceID = (IServiceID) IDFactory.getDefault().createID(discoveryContainer.getServicesNamespace(), new Object[] {ITestConstants.SERVICE_TYPE, ITestConstants.HOST});
		assertNotNull(serviceID);
		final ServiceProperties serviceProperties = new ServiceProperties(props);
		serviceProperties.setPropertyString("serviceProperties", "serviceProperties");
		serviceInfo = new ServiceInfo(uri, serviceID, 0, 0, serviceProperties);
		assertNotNull(serviceInfo);

		serviceID2 = (IServiceID) IDFactory.getDefault().createID(discoveryContainer.getServicesNamespace(), new Object[] {ITestConstants.SERVICE_TYPE2, ITestConstants.HOST});
		assertNotNull(serviceID);
		final ServiceProperties serviceProperties2 = new ServiceProperties(props);
		serviceProperties2.setPropertyString("serviceProperties2", "serviceProperties2");
		serviceInfo2 = new ServiceInfo(uri, serviceID2, 2, 2, serviceProperties2);
		assertNotNull(serviceInfo2);

		serviceID3 = (IServiceID) IDFactory.getDefault().createID(discoveryContainer.getServicesNamespace(), new Object[] {ITestConstants.SERVICE_TYPE3, ITestConstants.HOST});
		assertNotNull(serviceID);
		final ServiceProperties serviceProperties3 = new ServiceProperties(props);
		serviceProperties3.setPropertyString("serviceProperties3", "serviceProperties3");
		serviceInfo3 = new ServiceInfo(uri, serviceID3, 3, 3, serviceProperties3);
		assertNotNull(serviceInfo3);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		discoveryContainer.unregisterService(serviceInfo);
		discoveryContainer = null;
		container.disconnect();
		container.dispose();
		container = null;
	}

	protected void registerService() {
		try {
			discoveryContainer.registerService(serviceInfo);
		} catch (final ECFException e) {
			fail("IServiceInfo may be valid with this IDCA");
		}
	}

	protected void unregisterService() {
		try {
			discoveryContainer.unregisterService(serviceInfo);
		} catch (final ECFException e) {
			fail("unregistering of " + serviceInfo + " should just work");
		}
	}

	public void testConnect() {
		assertNull(container.getConnectedID());
		try {
			container.connect(null, null);
		} catch (final ContainerConnectException e) {
			fail("connect may not fail the first time");
		}
		assertNotNull(container.getConnectedID());
	}

	public void testConnectTwoTimes() {
		testConnect();
		try {
			container.connect(null, null);
		} catch (final ContainerConnectException e) {
			return;
		}
		fail("succeeding connects should fail");
	}

	public void testDisconnect() {
		testConnect();
		container.disconnect();
		assertNull(container.getConnectedID());
	}

	public void testReconnect() {
		testDisconnect();
		testConnect();
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServiceInfo(org.eclipse.ecf.discovery.identity.IServiceID)}.
	 */
	public void testGetServiceInfo() {
		testConnect();
		registerService();
		final IServiceInfo info = discoveryContainer.getServiceInfo(serviceInfo.getServiceID());
		assertTrue("IServiceInfo should match, expected:\n" + serviceInfo + " but:\n" + info, comparator.compare(info, serviceInfo) == 0);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServiceInfo(org.eclipse.ecf.discovery.identity.IServiceID)}.
	 */
	public void testGetServiceInfoWithNull() {
		try {
			discoveryContainer.getServiceInfo(null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServiceTypes()}.
	 */
	public void testGetServiceTypes() {
		testConnect();
		registerService();
		final IServiceTypeID[] serviceTypeIDs = discoveryContainer.getServiceTypes();
		assertTrue(serviceTypeIDs.length > 0);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServices()}.
	 */
	public void testGetServices() {
		testConnect();
		registerService();
		final IServiceInfo[] services = discoveryContainer.getServices();
		assertTrue(services.length >= 1);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServices(org.eclipse.ecf.discovery.identity.IServiceTypeID)}.
	 */
	public void testGetServicesIServiceTypeID() {
		testConnect();
		registerService();
		final IServiceInfo serviceInfo[] = discoveryContainer.getServices(serviceID.getServiceTypeID());
		assertTrue(serviceInfo.length > 0);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServices(org.eclipse.ecf.discovery.identity.IServiceTypeID)}.
	 */
	public void testGetServicesIServiceTypeIDWithNull() {
		try {
			discoveryContainer.getServices(null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#registerService(org.eclipse.ecf.discovery.IServiceInfo)}.
	 */
	public void testRegisterService() {
		testConnect();
		registerService();
		final IServiceInfo[] services = discoveryContainer.getServices();
		assertTrue(services.length >= 1);
		for (int i = 0; i < services.length; i++) {
			final IServiceInfo service = services[i];
			if (comparator.compare(service, serviceInfo) == 0) {
				return;
			}
		}
		fail("Self registered service not found");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#registerService(org.eclipse.ecf.discovery.IServiceInfo)}.
	 */
	public void testRegisterServiceWithNull() {
		testConnect();
		try {
			discoveryContainer.registerService(null);
		} catch (final ECFException e) {
			fail("null must cause AssertionFailedException");
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null must cause AssertionFailedException");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#unregisterService(org.eclipse.ecf.discovery.IServiceInfo)}.
	 */
	public void testUnregisterService() {
		testRegisterService();
		unregisterService();
		final IServiceInfo[] services = discoveryContainer.getServices();
		for (int i = 0; i < services.length; i++) {
			final IServiceInfo service = services[i];
			if (comparator.compare(service, serviceInfo) == 0) {
				fail("Expected service to be not registered anymore");
			}
		}
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#unregisterService(org.eclipse.ecf.discovery.IServiceInfo)}.
	 */
	public void testUnregisterServiceWithNull() {
		testConnect();
		try {
			discoveryContainer.unregisterService(null);
		} catch (final ECFException e) {
			fail("null must cause AssertionFailedException");
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null must cause AssertionFailedException");
	}

	public void testDispose() {
		testConnect();
		container.dispose();
		assertNull(container.getConnectedID());
		try {
			container.connect(null, null);
		} catch (final ContainerConnectException e) {
			return;
		}
		fail("A disposed container must not be reusable");
	}

	protected void addServiceListener(TestListener serviceListener) {
		discoveryContainer.addServiceListener(serviceListener);
		addListenerRegisterAndWait(serviceListener, serviceInfo);
		assertTrue("IServiceInfo mismatch", comparator.compare(((IServiceEvent) serviceListener.getEvent()).getServiceInfo(), serviceInfo) == 0);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#addServiceListener(org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testAddServiceListenerIServiceListener() {
		testConnect();
		assertTrue("No Services must be registerd at this point", discoveryContainer.getServices().length == 0);
		final TestListener tsl = new TestListener();
		addServiceListener(tsl);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#addServiceListener(org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testAddServiceListenerIServiceListenerWithNull() {
		try {
			discoveryContainer.addServiceListener(null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#addServiceListener(org.eclipse.ecf.discovery.identity.IServiceTypeID, org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testAddServiceListenerIServiceTypeIDIServiceListener() {
		testConnect();
		assertTrue("No Services must be registerd at this point", discoveryContainer.getServices().length == 0);

		final TestListener tsl = new TestListener();
		discoveryContainer.addServiceListener(serviceID.getServiceTypeID(), tsl);
		addListenerRegisterAndWait(tsl, serviceInfo);
		assertTrue("IServiceInfo mismatch", comparator.compare(((IServiceEvent) tsl.getEvent()).getServiceInfo(), serviceInfo) == 0);
	}

	private void addListenerRegisterAndWait(TestListener testServiceListener, IServiceInfo aServiceInfo) {
		synchronized (testServiceListener) {
			// register a service which we expect the test listener to get notified of
			registerService();
			int i = 0;
			while (!testServiceListener.isDone() && i++ < 10) {
				try {
					testServiceListener.wait(waitTimeForProvider / 10);
				} catch (final InterruptedException e) {
					Thread.currentThread().interrupt();
					fail("Some discovery unrelated threading issues?");
				}
			}
			if (i < 9)
				return;
		}
		assertNotNull("Test listener didn't receive discovery", testServiceListener.getEvent());
		assertTrue("Container mismatch", testServiceListener.getEvent().getLocalContainerID().equals(container.getConnectedID()));
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#addServiceListener(org.eclipse.ecf.discovery.identity.IServiceTypeID, org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testAddServiceListenerIServiceTypeIDIServiceListenerWithNull() {
		try {
			discoveryContainer.addServiceListener(null, null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#addServiceTypeListener(org.eclipse.ecf.discovery.IServiceTypeListener)}.
	 */
	public void testAddServiceTypeListener() {
		testConnect();
		final IServiceTypeListener serviceTypeListener = createServiceTypeListener();
		discoveryContainer.addServiceTypeListener(serviceTypeListener);
	}

	/**
	 * @return
	 */
	protected IServiceTypeListener createServiceTypeListener() {
		return new IServiceTypeListener() {

			public void serviceTypeDiscovered(IServiceTypeEvent event) {
				System.out.println("serviceTypeDiscovered(" + event + ")");
			}
		};
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#addServiceTypeListener(org.eclipse.ecf.discovery.IServiceTypeListener)}.
	 */
	public void testAddServiceTypeListenerWithNull() {
		try {
			discoveryContainer.addServiceTypeListener(null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.core.IContainer#getConnectNamespace()}.
	 */
	public void testGetConnectNamespace() {
		testConnect();
		assertNotNull(container.getConnectNamespace());
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.core.IContainer#getID()}.
	 */
	public void testGetID() {
		testConnect();
		assertNotNull(container.getID());
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#getServicesNamespace()}.
	 */
	public void testGetServicesNamespace() {
		testConnect();
		final Namespace namespace = discoveryContainer.getServicesNamespace();
		assertNotNull(namespace);
		try {
			final IServiceID serviceID = ServiceIDFactory.getDefault().createServiceID(namespace, serviceInfo.getServiceID().getServiceTypeID());
			assertNotNull(serviceID);
		} catch (final IDCreateException e) {
			fail("It must be possible to obtain a IServiceID");
		}
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#removeServiceListener(org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testRemoveServiceListenerIServiceListener() {
		testConnect();
		final TestListener serviceListener = new TestListener();
		addServiceListener(serviceListener);
		discoveryContainer.removeServiceListener(serviceListener);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#removeServiceListener(org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testRemoveServiceListenerIServiceListenerWithNull() {
		try {
			discoveryContainer.removeServiceListener(null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#removeServiceListener(org.eclipse.ecf.discovery.identity.IServiceTypeID, org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testRemoveServiceListenerIServiceTypeIDIServiceListener() {
		testConnect();
		final TestListener serviceListener = new TestListener();
		addServiceListener(serviceListener);
		discoveryContainer.removeServiceListener(serviceID.getServiceTypeID(), serviceListener);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#removeServiceListener(org.eclipse.ecf.discovery.identity.IServiceTypeID, org.eclipse.ecf.discovery.IServiceListener)}.
	 */
	public void testRemoveServiceListenerIServiceTypeIDIServiceListenerWithNull() {
		try {
			discoveryContainer.removeServiceListener(null, null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#removeServiceTypeListener(org.eclipse.ecf.discovery.IServiceTypeListener)}.
	 */
	public void testRemoveServiceTypeListener() {
		testConnect();
		final TestListener serviceTypeListener = new TestListener();
		addServiceListener(serviceTypeListener);
		discoveryContainer.removeServiceTypeListener(serviceTypeListener);
	}

	/**
	 * Test method for
	 * {@link org.eclipse.ecf.discovery.IDiscoveryContainerAdapter#removeServiceTypeListener(org.eclipse.ecf.discovery.IServiceTypeListener)}.
	 */
	public void testRemoveServiceTypeListenerWithNull() {
		try {
			discoveryContainer.removeServiceTypeListener(null);
		} catch (final AssertionFailedException e) {
			return;
		}
		fail("null argument is not allowed in api");
	}

	/**
	 * Test method for methods which can't do business when unconnected
	 */
	public void testMethodsWhichMustFailWhenUnconnected() {
		// TODO-mkuppe which methods require the container to be connected?
		// - listener registration/unregistration doesn't
		// - getService* is depending on the underlying mechanism
		fail("not yet implemented");
	}
}