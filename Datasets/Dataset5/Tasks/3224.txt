return bundleContext.createFilter("(&("

/****************************************************************************
 * Copyright (c) 2009 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.examples.remoteservices.hello.consumer;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.ecf.core.IContainerFactory;
import org.eclipse.ecf.examples.remoteservices.hello.IHello;
import org.eclipse.ecf.examples.remoteservices.hello.IHelloAsync;
import org.eclipse.ecf.osgi.services.discovery.IProxyDiscoveryListener;
import org.eclipse.ecf.osgi.services.discovery.LoggingProxyDiscoveryListener;
import org.eclipse.ecf.osgi.services.distribution.IDistributionConstants;
import org.eclipse.ecf.osgi.services.distribution.IProxyDistributionListener;
import org.eclipse.ecf.osgi.services.distribution.LoggingProxyDistributionListener;
import org.eclipse.ecf.remoteservice.IAsyncCallback;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceProxy;
import org.eclipse.ecf.remoteservice.RemoteServiceHelper;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.osgi.framework.Bundle;
import org.osgi.framework.BundleContext;
import org.osgi.framework.Filter;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public class HelloConsumerApplication implements IApplication,
		IDistributionConstants, ServiceTrackerCustomizer {

	public static final String CONSUMER_NAME = "org.eclipse.ecf.examples.remoteservices.hello.consumer";

	private BundleContext bundleContext;
	private ServiceTracker containerFactoryServiceTracker;

	private String containerType = "ecf.r_osgi.peer";

	private final Object appLock = new Object();
	private boolean done = false;

	private ServiceTracker helloServiceTracker;

	public Object start(IApplicationContext appContext) throws Exception {
		// Set bundle context (for use with service trackers)
		bundleContext = Activator.getContext();
		processArgs(appContext);

		// Create ECF container of appropriate type. The container instance
		// can be created in a variety of ways...e.g. via code like the line below, 
		// via the new org.eclipse.ecf.container extension point, or automatically 
		// upon discovery via the IProxyContainerFinder/DefaultProxyContainerFinder.  
		getContainerFactory().createContainer(containerType);

		// Register proxy discovery listener to log the publish/unpublish of remote services.  
		// This LoggingProxyDiscoveryListener logs the publication of OSGi remote services...so 
		// that the discovery can be more easily debugged.
		// Note that other IProxyDiscoveryListeners may be created and registered, and
		// all will be notified of publish/unpublish events
		bundleContext.registerService(IProxyDiscoveryListener.class.getName(), new LoggingProxyDiscoveryListener(), null);
		
		// Register proxy distribution listener to log the register/unregister of remote services.  
		// This LoggingProxyDistributionListener logs the register/unregister of OSGi remote services...so 
		// that the distribution can be more easily debugged.
		// Note that other IProxyDistributionListener may be created and registered, and
		// all will be notified of register/unregister events
		bundleContext.registerService(IProxyDistributionListener.class.getName(), new LoggingProxyDistributionListener(), null);

		// Create service tracker to track IHello instances that have the 'service.imported'
		// property set (as defined by OSGi 4.2 remote services spec).
		helloServiceTracker = new ServiceTracker(bundleContext,
				createRemoteFilter(), this);
		helloServiceTracker.open();

		startLocalDiscoveryIfPresent();
		
		waitForDone();

		return IApplication.EXIT_OK;
	}

	private void startLocalDiscoveryIfPresent() {
		Bundle[] bundles = bundleContext.getBundles();
		for(int i=0; i < bundles.length; i++) {
			if (bundles[i].getSymbolicName().equals("org.eclipse.ecf.osgi.services.discovery.local")) {
				try {
					bundles[i].start();
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}
	}

	private Filter createRemoteFilter() throws InvalidSyntaxException {
		// This filter looks for IHello instances that have the 
		// 'service.imported' property set, as specified by OSGi 4.2
		// remote services spec (Chapter 13)
		return bundleContext.createFilter("(|("
				+ org.osgi.framework.Constants.OBJECTCLASS + "="
				+ IHello.class.getName() + ")(" + SERVICE_IMPORTED + "=*))");
	}

	public void stop() {
		if (helloServiceTracker != null) {
			helloServiceTracker.close();
			helloServiceTracker = null;
		}
		if (containerFactoryServiceTracker != null) {
			containerFactoryServiceTracker.close();
			containerFactoryServiceTracker = null;
		}
		this.bundleContext = null;
		synchronized (appLock) {
			done = true;
			appLock.notifyAll();
		}
	}

	private IContainerFactory getContainerFactory() {
		if (containerFactoryServiceTracker == null) {
			containerFactoryServiceTracker = new ServiceTracker(bundleContext,
					IContainerFactory.class.getName(), null);
			containerFactoryServiceTracker.open();
		}
		return (IContainerFactory) containerFactoryServiceTracker.getService();
	}

	private void processArgs(IApplicationContext appContext) {
		String[] originalArgs = (String[]) appContext.getArguments().get(
				"application.args");
		if (originalArgs == null)
			return;
		for (int i = 0; i < originalArgs.length; i++) {
			if (originalArgs[i].equals("-containerType")) {
				containerType = originalArgs[i + 1];
				i++;
			}
		}
	}

	private void waitForDone() {
		// then just wait here
		synchronized (appLock) {
			while (!done) {
				try {
					appLock.wait();
				} catch (InterruptedException e) {
					// do nothing
				}
			}
		}
	}

	/**
	 * Method called when a REMOTE IHello instance is registered.
	 */
	public Object addingService(ServiceReference reference) {
		System.out.println("IHello service proxy being added");
		// Since this reference is for a remote service,
		// The service object returned is a proxy implementing the
		// IHello interface
		IHello proxy = (IHello) bundleContext.getService(reference);
		// Call proxy synchronously.  Note that this call may block or fail due to 
		// synchronous communication with remote service
		System.out.println("STARTING remote call via proxy...");
		proxy.hello(CONSUMER_NAME+" via proxy");
		System.out.println("COMPLETED remote call via proxy");
		System.out.println();
		
		// If the proxy is also an instance of IHelloAsync then use
		// this asynchronous interface to invoke methods asynchronously
		if (proxy instanceof IHelloAsync) {
			IHelloAsync helloA = (IHelloAsync) proxy;
			// Create callback for use in IHelloAsync
			IAsyncCallback callback = new IAsyncCallback<String>() {
				public void onSuccess(String result) {
					System.out.println("COMPLETED remote call with callback SUCCESS with result="+result);
					System.out.println();
				}
				public void onFailure(Throwable t) {
					System.out.println("COMPLETED remote call with callback FAILED with exception="+t);
					System.out.println();
				}
			};
			
			// Call asynchronously with callback
			System.out.println("STARTING async remote call via callback...");
			helloA.helloAsync(CONSUMER_NAME + " via async proxy with listener", callback);
			System.out.println("LOCAL async invocation complete");
			System.out.println();
			
			// Call asynchronously with future
			System.out.println("STARTING async remote call via future...");
			IFuture future = helloA.helloAsync(CONSUMER_NAME + " via async proxy with future");
			System.out.println("LOCAL async future invocation complete");
			System.out.println();
			try {
				while (!future.isDone()) {
					// do some other stuff
					System.out.println("LOCAL future not yet done...so we're doing other stuff while waiting for future to be done");
					Thread.sleep(200);
				}
				// Now it's done, so this will not block
				Object result = future.get();
				System.out.println("COMPLETED remote call with future SUCCEEDED with result="+result);
				System.out.println();
			} catch (OperationCanceledException e) {
				System.out.println("COMPLETED remote call with callback CANCELLED with exception="+e);
				System.out.println();
				e.printStackTrace();
			} catch (InterruptedException e) {
				System.out.println("COMPLETED remote call with callback INTERRUPTED with exception="+e);
				System.out.println();
				e.printStackTrace();
			}
		}
		
		
		// OSGi 4.2 remote service spec requires a property named 'service.imported' to be
		// set to a non-null value.  In the case of any ECF provider, this 'service.imported' property
		// is set to the IRemoteService object associated with the remote service.
		IRemoteService remoteService = (IRemoteService) reference
				.getProperty(IDistributionConstants.SERVICE_IMPORTED);
		Assert.isNotNull(remoteService);
		
		// This IRemoteService instance allows allows non-blocking/asynchronous invocation of
		// remote methods.  This allows the client to decide (at runtime if necessary) whether
		// to do synchronous/blocking calls or asynchronous/non-blocking calls.
		
		// It's also possible to get the remote service directly from the proxy
		remoteService = ((IRemoteServiceProxy) proxy).getRemoteService();
		Assert.isNotNull(remoteService);
		
		// In this case, we will make an non-blocking call and immediately get a 'future'...which is
		// a placeholder for a result of the remote computation.  This will not block.
		System.out.println("STARTING async remote call via future...");
		IFuture future = RemoteServiceHelper.futureExec(remoteService, "hello",
				new Object[] { CONSUMER_NAME + " future" });
		System.out.println("LOCAL async future invocation complete");
		// Client can execute arbitrary code here...
		try {
			// This blocks until communication and computation have completed successfully
			while (!future.isDone()) {
				// do some other stuff
				System.out.println("LOCAL future not yet done...so we're doing other stuff while waiting for future to be done");
				Thread.sleep(200);
			}
			// Now it's done, so this will not block
			Object result = future.get();
			System.out.println("COMPLETED remote call with future SUCCEEDED with result="+result);
			System.out.println();
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		return proxy;
	}

	public void modifiedService(ServiceReference reference, Object service) {
	}

	public void removedService(ServiceReference reference, Object service) {
		System.out.println("IHello Service proxy removed");
	}

}