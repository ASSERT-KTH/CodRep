import org.eclipse.ecf.remoteservice.rest.RestCallableFactory;

/******************************************************************************* 
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.tests.remoteservice.rest;

import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.remoteservice.IRemoteCallListener;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.remoteservice.client.IRemoteCallable;
import org.eclipse.ecf.remoteservice.events.IRemoteCallCompleteEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteCallEvent;
import org.eclipse.ecf.remoteservice.rest.IRestCall;
import org.eclipse.ecf.remoteservice.rest.RestCallFactory;
import org.eclipse.ecf.remoteservice.rest.client.RestCallableFactory;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.w3c.dom.Document;

public class RestRemoteServiceTest extends AbstractRestTestCase {

	IContainer container;
	IRemoteServiceRegistration registration;
	
	protected void setUp() throws Exception {
		container = createRestContainer(RestConstants.TEST_TWITTER_TARGET);
		IRemoteCallable callable = RestCallableFactory.createCallable(RestConstants.TEST_TWITTER_RESOURCEPATH);
		registration = registerCallable(container, callable, null);
	}

	protected void tearDown() throws Exception {
		registration.unregister();
		container.disconnect();
	}

	public void testSyncCall() {
		IRemoteService restClientService = getRemoteServiceClientContainerAdapter(container).getRemoteService(registration.getReference());
		try {
			Object result = restClientService.callSync(getRestXMLCall());
			assertNotNull(result);
		} catch (ECFException e) {
			fail("Could not contact the service");
		}
	}

	public void testAsynCall() {
		IRemoteService restClientService = getRemoteServiceClientContainerAdapter(container).getRemoteService(registration.getReference());
		IFuture future = restClientService.callAsync(getRestXMLCall());
		try {
			Object response = future.get();
			assertTrue(response instanceof Document);
		} catch (OperationCanceledException e) {
			fail(e.getMessage());
		} catch (InterruptedException e) {
			fail(e.getMessage());
		}
	}

	public void testAsyncCallWithListener() throws Exception {
		IRemoteService restClientService = getRemoteServiceClientContainerAdapter(container).getRemoteService(registration.getReference());
		restClientService.callAsync(getRestXMLCall(), new IRemoteCallListener() {
			public void handleEvent(IRemoteCallEvent event) {
				if (event instanceof IRemoteCallCompleteEvent) {
					IRemoteCallCompleteEvent cce = (IRemoteCallCompleteEvent) event;
					Object response = cce.getResponse();
					assertTrue(response instanceof Document);
					syncNotify();
				}
			}
		});
		syncWaitForNotify(10000);
	}

	private IRestCall getRestXMLCall() {
		return RestCallFactory.createRestCall(RestConstants.TEST_TWITTER_RESOURCEPATH);
	}

}