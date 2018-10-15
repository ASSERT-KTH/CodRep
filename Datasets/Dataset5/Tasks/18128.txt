null,

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.distribution;

import java.util.Arrays;
import java.util.Properties;
import org.eclipse.core.runtime.IAdapterManager;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.IIDFactory;
import org.eclipse.ecf.core.util.LogHelper;
import org.eclipse.ecf.core.util.PlatformHelper;
import org.eclipse.ecf.core.util.SystemLogService;
import org.eclipse.ecf.osgi.services.discovery.DiscoveredServiceTracker;
import org.eclipse.ecf.osgi.services.distribution.DefaultHostContainerFinder;
import org.eclipse.ecf.osgi.services.distribution.DefaultProxyContainerFinder;
import org.eclipse.ecf.osgi.services.distribution.IDistributionConstants;
import org.eclipse.ecf.osgi.services.distribution.IHostContainerFinder;
import org.eclipse.ecf.osgi.services.distribution.IHostDistributionListener;
import org.eclipse.ecf.osgi.services.distribution.IProxyContainerFinder;
import org.eclipse.ecf.osgi.services.distribution.IProxyDistributionListener;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.framework.Constants;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.framework.hooks.service.EventHook;
import org.osgi.service.log.LogService;
import org.osgi.util.tracker.ServiceTracker;

public class Activator implements BundleActivator {

	public static final String PLUGIN_ID = "org.eclipse.ecf.osgi.services.distribution"; //$NON-NLS-1$

	public static final boolean autoCreateProxyContainer = new Boolean(
			System.getProperty(
					"org.eclipse.ecf.osgi.services.distribution.autoCreateProxyContainer", //$NON-NLS-1$
					"true")).booleanValue(); //$NON-NLS-1$

	public static final boolean autoCreateHostContainer = new Boolean(
			System.getProperty(
					"org.eclipse.ecf.osgi.services.distribution.autoCreateHostContainer", //$NON-NLS-1$
					"true")).booleanValue(); //$NON-NLS-1$

	public static final String defaultHostConfigType = System.getProperty(
			"org.eclipse.ecf.osgi.services.distribution.defaultConfigType", //$NON-NLS-1$
			"ecf.generic.server"); //$NON-NLS-1$

	private static Activator plugin;
	private BundleContext context;

	private ServiceTracker containerManagerTracker;

	private DistributionProviderImpl distributionProvider;

	private ServiceRegistration eventHookRegistration;

	private ServiceRegistration discoveredServiceTrackerRegistration;
	private DiscoveredServiceTrackerImpl discoveredServiceTrackerImpl;

	private ServiceRegistration proxyrsContainerFinderRegistration;
	private ServiceRegistration hostrsContainerFinderRegistration;

	private ServiceTracker logServiceTracker = null;
	private LogService logService = null;

	private ServiceTracker adapterManagerTracker;

	private ServiceTracker proxyrsContainerFinder;
	private ServiceTracker hostrsContainerFinder;

	private ServiceTracker hostRegistrationListenerServiceTracker;
	private ServiceTracker proxyDistributionListenerServiceTracker;

	private ServiceTracker idFactoryTracker;

	public static Activator getDefault() {
		return plugin;
	}

	public BundleContext getContext() {
		return context;
	}

	protected synchronized LogService getLogService() {
		if (this.context == null)
			return null;
		if (logServiceTracker == null) {
			logServiceTracker = new ServiceTracker(this.context,
					LogService.class.getName(), null);
			logServiceTracker.open();
		}
		logService = (LogService) logServiceTracker.getService();
		if (logService == null)
			logService = new SystemLogService(PLUGIN_ID);
		return logService;
	}

	public void log(IStatus status) {
		if (logService == null)
			logService = getLogService();
		if (logService != null)
			logService.log(null, LogHelper.getLogCode(status),
					LogHelper.getLogMessage(status), status.getException());
	}

	public void log(ServiceReference sr, IStatus status) {
		log(sr, LogHelper.getLogCode(status), LogHelper.getLogMessage(status),
				status.getException());
	}

	public void log(ServiceReference sr, int level, String message, Throwable t) {
		if (logService == null)
			logService = getLogService();
		if (logService != null)
			logService.log(sr, level, message, t);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext
	 * )
	 */
	public void start(final BundleContext ctxt) throws Exception {
		plugin = this;
		this.context = ctxt;

		// Create distribution provider impl
		this.distributionProvider = new DistributionProviderImpl();
		// Create discovered service tracker impl
		discoveredServiceTrackerImpl = new DiscoveredServiceTrackerImpl(
				this.distributionProvider);
		// Register discovered service tracker
		this.discoveredServiceTrackerRegistration = this.context
				.registerService(DiscoveredServiceTracker.class.getName(),
						discoveredServiceTrackerImpl, null);

		// Set service ranking to Integer.MIN_VALUE so that other impls
		// will be prefered over the default one
		final Properties proxyContainerFinderProps = new Properties();
		proxyContainerFinderProps.put(Constants.SERVICE_RANKING, new Integer(
				Integer.MIN_VALUE));
		// Register default proxy container finder
		this.proxyrsContainerFinderRegistration = this.context.registerService(
				IProxyContainerFinder.class.getName(),
				new DefaultProxyContainerFinder(autoCreateProxyContainer),
				proxyContainerFinderProps);

		// register the event hook to get informed when new services appear
		final EventHookImpl hook = new EventHookImpl(distributionProvider);
		this.eventHookRegistration = this.context.registerService(
				EventHook.class.getName(), hook, null);

		// register the default host container finder
		final Properties hostContainerFinderProps = new Properties();
		hostContainerFinderProps.put(Constants.SERVICE_RANKING, new Integer(
				Integer.MIN_VALUE));

		// If defaultHostConfigType is empty string or "null" then set to null
		String[] defaultHostConfigTypes = ("".equals(defaultHostConfigType) || "null".equals(defaultHostConfigType)) ? null : new String[] { defaultHostConfigType }; //$NON-NLS-1$ //$NON-NLS-2$

		this.hostrsContainerFinderRegistration = this.context.registerService(
				IHostContainerFinder.class.getName(),
				new DefaultHostContainerFinder(autoCreateHostContainer,
						defaultHostConfigTypes), hostContainerFinderProps);

		// register all existing services which have the marker property
		// http://bugs.eclipse.org/323208
		new Thread(new Runnable() {
			public void run() {
				registerExistingServices(hook, ctxt);
			}
		}, "Distribution Provider startup worker").start(); //$NON-NLS-1$

	}

	private void registerExistingServices(final EventHookImpl hook,
			final BundleContext bundleContext) {
		try {
			final ServiceReference[] refs = bundleContext.getServiceReferences(
					(String) null,
					"(" + IDistributionConstants.SERVICE_EXPORTED_INTERFACES //$NON-NLS-1$
							+ "=*)"); //$NON-NLS-1$
			if (refs != null) {
				for (int i = 0; i < refs.length; i++) {
					hook.handleRegisteredServiceEvent(refs[i], null);
				}
			}
		} catch (InvalidSyntaxException e) {
			// not possible
		}

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext ctxt) throws Exception {
		if (this.discoveredServiceTrackerRegistration != null) {
			this.discoveredServiceTrackerRegistration.unregister();
			this.discoveredServiceTrackerRegistration = null;
		}
		if (discoveredServiceTrackerImpl != null) {
			this.discoveredServiceTrackerImpl.close();
			this.discoveredServiceTrackerImpl = null;
		}
		if (this.proxyrsContainerFinderRegistration != null) {
			this.proxyrsContainerFinderRegistration.unregister();
			this.proxyrsContainerFinderRegistration = null;
		}
		if (this.eventHookRegistration != null) {
			this.eventHookRegistration.unregister();
			this.eventHookRegistration = null;
		}
		if (this.hostrsContainerFinderRegistration != null) {
			this.hostrsContainerFinderRegistration.unregister();
			this.hostrsContainerFinderRegistration = null;
		}
		if (containerManagerTracker != null) {
			containerManagerTracker.close();
			containerManagerTracker = null;
		}
		if (logServiceTracker != null) {
			logServiceTracker.close();
			logServiceTracker = null;
			logService = null;
		}
		if (adapterManagerTracker != null) {
			adapterManagerTracker.close();
			adapterManagerTracker = null;
		}
		if (distributionProvider != null) {
			distributionProvider.dispose();
			distributionProvider = null;
		}
		if (proxyrsContainerFinder != null) {
			proxyrsContainerFinder.close();
			proxyrsContainerFinder = null;
		}
		if (hostRegistrationListenerServiceTracker != null) {
			hostRegistrationListenerServiceTracker.close();
			hostRegistrationListenerServiceTracker = null;
		}
		if (proxyDistributionListenerServiceTracker != null) {
			proxyDistributionListenerServiceTracker.close();
			proxyDistributionListenerServiceTracker = null;
		}
		if (idFactoryTracker != null) {
			idFactoryTracker.close();
			idFactoryTracker = null;
		}
		synchronized (this) {
			this.context = null;
		}
		plugin = null;
	}

	public synchronized IContainerManager getContainerManager() {
		if (this.context == null)
			return null;
		if (containerManagerTracker == null) {
			containerManagerTracker = new ServiceTracker(this.context,
					IContainerManager.class.getName(), null);
			containerManagerTracker.open();
		}
		return (IContainerManager) containerManagerTracker.getService();
	}

	public synchronized IProxyContainerFinder getProxyRemoteServiceContainerFinder() {
		if (this.context == null)
			return null;
		if (proxyrsContainerFinder == null) {
			proxyrsContainerFinder = new ServiceTracker(this.context,
					IProxyContainerFinder.class.getName(), null);
			proxyrsContainerFinder.open();
		}
		return (IProxyContainerFinder) proxyrsContainerFinder.getService();
	}

	public synchronized IHostContainerFinder getHostRemoteServiceContainerFinder() {
		if (this.context == null)
			return null;
		if (hostrsContainerFinder == null) {
			hostrsContainerFinder = new ServiceTracker(this.context,
					IHostContainerFinder.class.getName(), null);
			hostrsContainerFinder.open();
		}
		return (IHostContainerFinder) hostrsContainerFinder.getService();
	}

	public synchronized IHostDistributionListener[] getHostRegistrationListeners() {
		if (this.context == null)
			return null;
		if (hostRegistrationListenerServiceTracker == null) {
			hostRegistrationListenerServiceTracker = new ServiceTracker(
					this.context, IHostDistributionListener.class.getName(),
					null);
			hostRegistrationListenerServiceTracker.open();
		}
		Object[] objs = hostRegistrationListenerServiceTracker.getServices();
		if (objs == null)
			return null;
		return (IHostDistributionListener[]) Arrays.asList(objs).toArray(
				new IHostDistributionListener[] {});
	}

	public synchronized IProxyDistributionListener[] getProxyDistributionListeners() {
		if (this.context == null)
			return null;
		if (proxyDistributionListenerServiceTracker == null) {
			proxyDistributionListenerServiceTracker = new ServiceTracker(
					this.context, IProxyDistributionListener.class.getName(),
					null);
			proxyDistributionListenerServiceTracker.open();
		}
		Object[] objs = proxyDistributionListenerServiceTracker.getServices();
		if (objs == null)
			return null;
		return (IProxyDistributionListener[]) Arrays.asList(objs).toArray(
				new IProxyDistributionListener[] {});
	}

	public synchronized IAdapterManager getAdapterManager() {
		if (this.context == null)
			return null;
		// First, try to get the adapter manager via
		if (adapterManagerTracker == null) {
			adapterManagerTracker = new ServiceTracker(this.context,
					IAdapterManager.class.getName(), null);
			adapterManagerTracker.open();
		}
		IAdapterManager adapterManager = (IAdapterManager) adapterManagerTracker
				.getService();
		// Then, if the service isn't there, try to get from Platform class via
		// PlatformHelper class
		if (adapterManager == null)
			adapterManager = PlatformHelper.getPlatformAdapterManager();
		return adapterManager;
	}

	public IIDFactory getIDFactory() {
		if (this.context == null)
			return null;
		if (idFactoryTracker == null) {
			idFactoryTracker = new ServiceTracker(this.context,
					IIDFactory.class.getName(), null);
			idFactoryTracker.open();
		}
		return (IIDFactory) idFactoryTracker.getService();
	}
}