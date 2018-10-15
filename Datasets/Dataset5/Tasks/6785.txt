eventAdminImpl = new DistributedEventAdmin(bundleContext);

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.examples.internal.eventadmin.app;

import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerFactory;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.remoteservice.eventadmin.DistributedEventAdmin;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.event.EventConstants;
import org.osgi.util.tracker.ServiceTracker;

public abstract class AbstractEventAdminApplication implements IApplication {

	public static final String DEFAULT_TOPIC = "defaultTopic";

	protected BundleContext bundleContext;

	// The following must be set in processArgs
	protected String containerType;
	protected String containerId;
	protected String targetId;
	protected String topic = DEFAULT_TOPIC;

	protected ServiceTracker containerManagerTracker;
	private final Object appLock = new Object();
	private boolean done = false;
	protected DistributedEventAdmin eventAdminImpl;
	protected ServiceRegistration eventAdminRegistration;
	protected IContainer container;

	protected Object startup(IApplicationContext context) throws Exception {
		// Get BundleContext
		bundleContext = Activator.getContext();
		
		// Process Arguments
		final String[] args = mungeArguments((String[]) context.getArguments()
				.get("application.args")); //$NON-NLS-1$
		processArgs(args);
		
		// Create event admin impl
		eventAdminImpl = new DistributedEventAdmin(bundleContext,topic);
		
		// Create, configure, and connect container
		createConfigureAndConnectContainer();
		
		// start event admin
		eventAdminImpl.start();
		// register as EventAdmin service instance
		Properties props = new Properties();
		props.put(EventConstants.EVENT_TOPIC, topic);
	    eventAdminRegistration = bundleContext.registerService("org.osgi.service.event.EventAdmin", eventAdminImpl,props);
		
		return IApplication.EXIT_OK;
	}
	
	protected void shutdown() {
		if (eventAdminRegistration != null) {
			eventAdminRegistration.unregister();
			eventAdminRegistration = null;
		}
		if (container != null) {
			container.dispose();
			getContainerManager().removeAllContainers();
			container = null;
		}
		if (containerManagerTracker != null) {
			containerManagerTracker.close();
			containerManagerTracker = null;
		}
		synchronized (appLock) {
			done = true;
			appLock.notifyAll();
		}
		bundleContext = null;
	}
	
	protected Object run() {
		waitForDone();
		return IApplication.EXIT_OK;
	}
	
	public Object start(IApplicationContext context) throws Exception {
		Object startupResult = startup(context);
		if (!startupResult.equals(IApplication.EXIT_OK)) return startupResult;
		return run();
	}

	private String[] mungeArguments(String originalArgs[]) {
		if (originalArgs == null)
			return new String[0];
		final List l = new ArrayList();
		for (int i = 0; i < originalArgs.length; i++)
			if (!originalArgs[i].equals("-pdelaunch")) //$NON-NLS-1$
				l.add(originalArgs[i]);
		return (String[]) l.toArray(new String[] {});
	}

	protected void usage() {
		System.out.println("Usage: eclipse.exe -application "+usageApplicationId()+" "+usageParameters());
	}
	
	protected abstract String usageApplicationId();
	protected abstract String usageParameters();
	
	protected abstract void processArgs(String[] args);

	protected void waitForDone() {
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

	public void stop() {
		shutdown();
	}

	protected void createConfigureAndConnectContainer()
			throws ContainerCreateException, SharedObjectAddException,
			ContainerConnectException {
		// get container factory and create container
		IContainerFactory containerFactory = getContainerManager()
				.getContainerFactory();
		container = (containerId == null) ? containerFactory
		.createContainer(containerType) : containerFactory
		.createContainer(containerType, new Object[] { containerId });
		
		// Get socontainer
		ISharedObjectContainer soContainer = (ISharedObjectContainer) container.getAdapter(ISharedObjectContainer.class);
		// Add to soContainer, with topic as name
		soContainer.getSharedObjectManager().addSharedObject(IDFactory.getDefault().createStringID(topic), eventAdminImpl, null);
		
		// then connect to target Id
		if (targetId != null) container.connect(IDFactory.getDefault().createID(
					container.getConnectNamespace(), targetId), null);
	}

	protected IContainerManager getContainerManager() {
		if (containerManagerTracker == null) {
			containerManagerTracker = new ServiceTracker(bundleContext,
					IContainerManager.class.getName(), null);
			containerManagerTracker.open();
		}
		return (IContainerManager) containerManagerTracker.getService();
	}

}