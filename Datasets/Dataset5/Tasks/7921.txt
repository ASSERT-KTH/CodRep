Thread.sleep(SLEEPTIME);

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

import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceListener;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceRegisteredEvent;
import org.eclipse.ecf.tests.remoteservice.AbstractRemoteServiceTest;
import org.eclipse.ecf.tests.remoteservice.IConcatService;
import org.eclipse.equinox.concurrent.future.IFuture;

public class RemoteServiceTest extends AbstractRemoteServiceTest {

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		setClientCount(2);
		createServerAndClients();
		setupRemoteServiceAdapters();
		connectClients();
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

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.remoteservice.AbstractRemoteServiceTest#getClientContainerName()
	 */
	protected String getClientContainerName() {
		return Generic.CONSUMER_CONTAINER_TYPE;
	}

	IRemoteService remoteService;
	boolean done;

	public void testServiceListener() throws Exception {
		final IRemoteServiceContainerAdapter[] adapters = getRemoteServiceAdapters();
		done = false;
		final Object lock = new Object();
		adapters[1].addRemoteServiceListener(new IRemoteServiceListener() {
			public void handleServiceEvent(IRemoteServiceEvent event) {
				if (event instanceof IRemoteServiceRegisteredEvent) {
					IRemoteServiceRegisteredEvent e = (IRemoteServiceRegisteredEvent) event;
					IRemoteServiceReference ref = e.getReference();
					remoteService = adapters[1].getRemoteService(ref);
					assertNotNull(remoteService);
					synchronized (lock) {
						done = true;
						lock.notify();
					}
				}
			}
		});

		// Now register service on server (adapters[0]).  This should result in notification on client (adapters[1])
		// in above handleServiceEvent
		adapters[0].registerRemoteService(new String[] { IConcatService.class.getName() }, createService(),
				customizeProperties(null));

		// wait until block above called asynchronously
		int count = 0;
		synchronized (lock) {
			while (!done && count++ < 10) {
				try {
					lock.wait(1000);
				} catch (InterruptedException e) {
					fail();
				}
			}
		}

		assertTrue(done);

		if (remoteService == null) return;
		// We've got the remote service, so we're good to go
		assertTrue(remoteService != null);
		traceCallStart("callAsynchResult");
		final IFuture result = remoteService
				.callAsync(createRemoteConcat("ECF AsynchResults ", "are cool"));
		traceCallEnd("callAsynch");
		assertNotNull(result);
		Thread.sleep(ASYNC_WAITTIME);
	}


}