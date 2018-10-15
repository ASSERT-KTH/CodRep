appLock.notifyAll();

/****************************************************************************
 * Copyright (c) 2009 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 ****************************************************************************/
package org.eclipse.ecf.internal.examples.loadbalancing.server;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.examples.loadbalancing.IDataProcessor;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.osgi.framework.BundleContext;
import org.osgi.util.tracker.ServiceTracker;

public class DataProcessorServerApplication implements IApplication {

	private static final String LB_SERVER_CONTAINER_TYPE = "ecf.jms.activemq.tcp.lb.server";
	private static final String DEFAULT_QUEUE_ID = "tcp://localhost:61616/exampleQueue";

	private BundleContext bundleContext;
	private ServiceTracker containerManagerServiceTracker;
	private String containerType = LB_SERVER_CONTAINER_TYPE;
	
	// Queue that we will attach to as queue message consumer (receiver of
	// actual remote method/invocation
	// requests). Note that this queueId can be changed by using the -queueId
	// launch parameter...e.g.
	// -queueId tcp://localhost:61616/myQueueName
	private String queueId = DEFAULT_QUEUE_ID;

	// Container instance that connects us with the ActiveMQ queue as a message
	// consumer
	private IContainer container;
	// The IDataProcessor service implementation. This object receives the
	// actual
	// remote method calls, executes arbitrary code, and returns a result.
	private DataProcessorImpl dataProcessorImpl;
	// The remote service registration associated with the dataProcessorImpl
	private IRemoteServiceRegistration dataProcessorRemoteServiceRegistration;

	public Object start(IApplicationContext appContext) throws Exception {
		bundleContext = Activator.getContext();
		// Process Arguments...i.e. set queueId if specified
		processArgs(appContext);

		// Create container and connect to given queueId as message consumer
		container = getContainerManagerService().getContainerFactory()
				.createContainer(containerType,
						new Object[] { queueId });

		// Get remote service container adapter
		IRemoteServiceContainerAdapter remoteServiceContainerAdapter = (IRemoteServiceContainerAdapter) container
				.getAdapter(IRemoteServiceContainerAdapter.class);

		// Create the data processor implementation
		dataProcessorImpl = new DataProcessorImpl(container.getID());

		// Register data processor as remote services (with queue consumer
		// container)
		dataProcessorRemoteServiceRegistration = remoteServiceContainerAdapter
				.registerRemoteService(new String[] { IDataProcessor.class
						.getName() }, dataProcessorImpl, null);

		// Report success of registration
		System.out
				.println("LB Server:  Data Processor Registered queue="+queueId);

		// then just wait for service requests
		waitForDone();
		return IApplication.EXIT_OK;
	}

	public void stop() {
		if (dataProcessorRemoteServiceRegistration != null) {
			dataProcessorRemoteServiceRegistration.unregister();
			dataProcessorRemoteServiceRegistration = null;
		}
		if (dataProcessorImpl != null) {
			dataProcessorImpl.stop();
			dataProcessorImpl = null;
		}
		if (container != null) {
			container.dispose();
			container = null;
			getContainerManagerService().removeAllContainers();
		}
		if (containerManagerServiceTracker != null) {
			containerManagerServiceTracker.close();
			containerManagerServiceTracker = null;
		}
		bundleContext = null;
		synchronized (appLock) {
			done = true;
			notifyAll();
		}
	}

	private void processArgs(IApplicationContext appContext) {
		String[] originalArgs = (String[]) appContext.getArguments().get(
				"application.args");
		if (originalArgs == null)
			return;
		for (int i = 0; i < originalArgs.length; i++) {
			if (originalArgs[i].equals("-queueId")) {
				queueId = originalArgs[i + 1];
				i++;
			} else if (originalArgs[i].equals("-containerType")) {
				containerType = originalArgs[i + 1];
				i++;
			}
		}
	}

	private IContainerManager getContainerManagerService() {
		if (containerManagerServiceTracker == null) {
			containerManagerServiceTracker = new ServiceTracker(bundleContext,
					IContainerManager.class.getName(), null);
			containerManagerServiceTracker.open();
		}
		return (IContainerManager) containerManagerServiceTracker.getService();
	}

	private final Object appLock = new Object();
	private boolean done = false;

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