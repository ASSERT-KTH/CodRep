props.put(SERVICE_EXPORTED_INTERFACES, SERVICE_EXPORTED_INTERFACES_WILDCARD);

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
package org.eclipse.ecf.internal.examples.remoteservices.hello.host;

import java.util.Properties;

import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.examples.remoteservices.hello.IHello;
import org.eclipse.ecf.examples.remoteservices.hello.impl.Hello;
import org.eclipse.ecf.osgi.services.distribution.IDistributionConstants;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceRegistration;
import org.osgi.util.tracker.ServiceTracker;

public class HelloHostApplication implements IApplication,
		IDistributionConstants {

	private static final String DEFAULT_CONTAINER_TYPE = "ecf.r_osgi.peer";
	public static final String DEFAULT_CONTAINER_ID = null;

	private BundleContext bundleContext;
	private ServiceTracker containerManagerServiceTracker;

	private String containerType = DEFAULT_CONTAINER_TYPE;
	private String containerId = DEFAULT_CONTAINER_ID;

	private final Object appLock = new Object();
	private boolean done = false;

	private ServiceRegistration helloRegistration;

	public Object start(IApplicationContext appContext) throws Exception {
		bundleContext = Activator.getContext();
		// Process Arguments
		processArgs(appContext);
		// Create Container of desired type
		IContainerManager containerManager = getContainerManagerService();
		if (containerId == null || "".equals(containerId))
			containerManager.getContainerFactory().createContainer(
					containerType);
		else
			containerManager.getContainerFactory().createContainer(
					containerType, new Object[] { containerId });

		Properties props = new Properties();
		// add OSGi service property indicating this
		props.put(REMOTE_INTERFACES, REMOTE_INTERFACES_WILDCARD);
		// register remote service
		helloRegistration = bundleContext.registerService(IHello.class
				.getName(), new Hello(), props);
		System.out.println("Host: Hello Service Registered");

		// wait until stopped
		waitForDone();

		return IApplication.EXIT_OK;
	}

	public void stop() {
		if (helloRegistration != null) {
			helloRegistration.unregister();
			helloRegistration = null;
		}
		if (containerManagerServiceTracker != null) {
			containerManagerServiceTracker.close();
			containerManagerServiceTracker = null;
		}
		bundleContext = null;
	}

	private IContainerManager getContainerManagerService() {
		if (containerManagerServiceTracker == null) {
			containerManagerServiceTracker = new ServiceTracker(bundleContext,
					IContainerManager.class.getName(), null);
			containerManagerServiceTracker.open();
		}
		return (IContainerManager) containerManagerServiceTracker.getService();
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
			} else if (originalArgs[i].equals("-containerId")) {
				containerId = originalArgs[i + 1];
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

}