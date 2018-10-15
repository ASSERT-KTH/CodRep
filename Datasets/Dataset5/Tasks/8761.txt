adapter.setResourceProcessor(createRestResource());

/******************************************************************************* 
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.tests.remoteservice.rest.twitter;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.remoteservice.IRemoteCall;
import org.eclipse.ecf.remoteservice.IRemoteCallListener;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.remoteservice.events.IRemoteCallCompleteEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteCallEvent;
import org.eclipse.ecf.remoteservice.rest.IRestCallable;
import org.eclipse.ecf.remoteservice.rest.RestCallFactory;
import org.eclipse.ecf.remoteservice.rest.RestCallable;
import org.eclipse.ecf.remoteservice.rest.client.IRestClientContainerAdapter;
import org.eclipse.ecf.remoteservice.rest.resource.IRestResourceProcessor;
import org.eclipse.ecf.tests.remoteservice.rest.AbstractRestTestCase;
import org.eclipse.ecf.tests.remoteservice.rest.RestConstants;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class TwitterRemoteServiceTest extends AbstractRestTestCase {

	private String username = System.getProperty("username","eclipsedummy");
	private String password = System.getProperty("password","eclipse");
	
	IContainer container;
	IRemoteServiceRegistration registration;
	
	protected void setUp() throws Exception {
		// Create container
		container = createRestContainer(RestConstants.TEST_TWITTER_TARGET);	
		// Get adapter
		IRestClientContainerAdapter adapter = (IRestClientContainerAdapter) getRestClientContainerAdapter(container);
		// Setup authentication info
		adapter.setConnectContextForAuthentication(ConnectContextFactory.createUsernamePasswordConnectContext(username, password));
		
		// Setup resource handler
		adapter.setRestResource(createRestResource());

		// Create and register callable to register service
		List callables = new ArrayList();
		callables.add(new RestCallable("getUserStatuses","/statuses/user_timeline.json",null,IRestCallable.RequestType.GET));
		// Setup callable
		registration = adapter.registerCallable(new String[] { IUserTimeline.class.getName() }, callables, null);
}

	protected void tearDown() throws Exception {
		registration.unregister();
		container.disconnect();
	}

	private IRestResourceProcessor createRestResource() {
		return new IRestResourceProcessor() {

			public Object createResponseRepresentation(IRemoteCall call, IRestCallable callable, Map responseHeaders, String responseBody)
					throws ECFException {
				try {
					JSONArray timeline = new JSONArray(responseBody);
					List statuses = new ArrayList();
					for (int i = 0; i < timeline.length(); i++) {
						try {
							JSONObject jsonObject = timeline.getJSONObject(i);
							String source = jsonObject.getString("source");
							String text = jsonObject.getString("text");
							String createdString = jsonObject.getString("created_at");
							IUserStatus status = new UserStatus(createdString, source, text);
							statuses.add(status);
						} catch (JSONException e) {
							throw new ECFException("Cannot process response representation",e);
						}
					}
					return (IUserStatus[]) statuses.toArray(new IUserStatus[statuses.size()]);
				} catch (JSONException e) {
					throw new ECFException("JSON array parse exception",e);
				}
			}};
	}

	public void testSyncCall() {
		IRemoteService restClientService = getRestClientContainerAdapter(container).getRemoteService(registration.getReference());
		try {
			Object result = restClientService.callSync(RestCallFactory.createRestCall(IUserTimeline.class.getName() + ".getUserStatuses"));
			assertNotNull(result);
		} catch (ECFException e) {
			fail("Could not contact the service");
		}
	}

	public void testGetProxy() {
		IRemoteService restClientService = getRestClientContainerAdapter(container).getRemoteService(registration.getReference());
		try {
			IUserTimeline userTimeline = (IUserTimeline) restClientService.getProxy();
			assertNotNull(userTimeline);
		} catch (ECFException e) {
			fail("Could not contact the service");
		}
	}

	public void testAsyncCall() {
		IRemoteService restClientService = getRestClientContainerAdapter(container).getRemoteService(registration.getReference());
		IFuture future = restClientService.callAsync(RestCallFactory.createRestCall(IUserTimeline.class.getName() + ".getUserStatuses"));
		try {
			Object response = future.get();
			assertTrue(response instanceof IUserStatus[]);
		} catch (OperationCanceledException e) {
			fail(e.getMessage());
		} catch (InterruptedException e) {
			fail(e.getMessage());
		}
	}

	public void testAsyncCallWithListener() throws Exception {
		IRemoteService restClientService = getRestClientContainerAdapter(container).getRemoteService(registration.getReference());
		restClientService.callAsync(RestCallFactory.createRestCall(IUserTimeline.class.getName() + ".getUserStatuses"), new IRemoteCallListener() {
			public void handleEvent(IRemoteCallEvent event) {
				if (event instanceof IRemoteCallCompleteEvent) {
					IRemoteCallCompleteEvent cce = (IRemoteCallCompleteEvent) event;
					Object response = cce.getResponse();
					assertTrue(response instanceof IUserStatus[]);
					syncNotify();
				}
			}
		});
		syncWaitForNotify(10000);
	}

	public void testProxyCall() {
		IRemoteService restClientService = getRestClientContainerAdapter(container).getRemoteService(registration.getReference());
		try {
			IUserTimeline userTimeline = (IUserTimeline) restClientService.getProxy();
			IUserStatus[] statuses = userTimeline.getUserStatuses();
			assertNotNull(statuses);
		} catch (ECFException e) {
			fail("Could not contact the service");
		}
	}

}