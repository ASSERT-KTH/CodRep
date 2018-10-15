protected IRemoteServiceRegistration registerService(IRemoteServiceContainerAdapter adapter, String serviceInterface, Object service, Dictionary serviceProperties, int sleepTime) {

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

package org.eclipse.ecf.tests.provider.xmpp.remoteservice;

import java.util.Dictionary;
import java.util.Hashtable;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.tests.remoteservice.AbstractRemoteServiceTest;
import org.ecllpse.ecf.tests.provider.xmpp.XMPPS;

public class RemoteServiceTest extends AbstractRemoteServiceTest {

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.presence.AbstractPresenceTestCase#getClientContainerName()
	 */
	protected String getClientContainerName() {
		return XMPPS.CONTAINER_NAME;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.ContainerAbstractTestCase#getServerConnectID(int)
	 */
	protected ID getServerConnectID(int client) {
		try {
			return IDFactory.getDefault().createID(getClient(client).getConnectNamespace(), getUsername(client));
		} catch (final IDCreateException e) {
			throw new RuntimeException("cannot create connect id for client " + 1, e);
		}
	}

	protected IRemoteServiceRegistration registerService(IRemoteServiceContainerAdapter adapter, String serviceInterface, Object service, int sleepTime) {
		final Dictionary props = new Hashtable();
		props.put(Constants.SERVICE_REGISTRATION_TARGETS, getClient(1).getConnectedID());
		final IRemoteServiceRegistration result = adapter.registerRemoteService(new String[] {serviceInterface}, service, props);
		sleep(sleepTime);
		return result;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		setClientCount(2);
		clients = createClients();
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
		cleanUpClients();
		super.tearDown();
	}

}