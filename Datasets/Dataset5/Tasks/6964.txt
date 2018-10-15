public static final String NAME = "ecf.discovery.jmdns"; //$NON-NLS-1$

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
package org.eclipse.ecf.internal.provider.jmdns;

import java.util.Properties;
import org.eclipse.core.runtime.IAdapterManager;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.util.*;
import org.eclipse.ecf.discovery.IDiscoveryAdvertiser;
import org.eclipse.ecf.discovery.IDiscoveryLocator;
import org.eclipse.ecf.discovery.service.IDiscoveryService;
import org.eclipse.ecf.provider.jmdns.container.JMDNSDiscoveryContainer;
import org.osgi.framework.*;
import org.osgi.service.log.LogService;
import org.osgi.util.tracker.ServiceTracker;

/**
 * The main plugin class to be used in the desktop.
 */
public class JMDNSPlugin implements BundleActivator {
	private static final String NAME = "ecf.discovery.jmdns"; //$NON-NLS-1$

	// The shared instance.
	private static JMDNSPlugin plugin;

	private BundleContext context = null;

	public static final String PLUGIN_ID = "org.eclipse.ecf.provider.jmdns"; //$NON-NLS-1$

	/**
	 * The constructor.
	 */
	public JMDNSPlugin() {
		super();
		plugin = this;
	}

	private ServiceTracker adapterManagerTracker = null;

	private ServiceRegistration serviceRegistration;

	private ServiceTracker logServiceTracker = null;

	private LogService logService = null;

	public IAdapterManager getAdapterManager() {
		// First, try to get the adapter manager via
		if (adapterManagerTracker == null) {
			adapterManagerTracker = new ServiceTracker(this.context, IAdapterManager.class.getName(), null);
			adapterManagerTracker.open();
		}
		IAdapterManager adapterManager = (IAdapterManager) adapterManagerTracker.getService();
		// Then, if the service isn't there, try to get from Platform class via
		// PlatformHelper class
		if (adapterManager == null)
			adapterManager = PlatformHelper.getPlatformAdapterManager();
		return adapterManager;
	}

	/**
	 * This method is called upon plug-in activation
	 */
	public void start(final BundleContext ctxt) throws Exception {
		this.context = ctxt;

		final Properties props = new Properties();
		props.put(IDiscoveryService.CONTAINER_NAME, NAME);
		props.put(Constants.SERVICE_RANKING, new Integer(750));
		String[] clazzes = new String[] {IDiscoveryService.class.getName(), IDiscoveryLocator.class.getName(), IDiscoveryAdvertiser.class.getName()};
		serviceRegistration = context.registerService(clazzes, new ServiceFactory() {
			private volatile JMDNSDiscoveryContainer jdc;

			/* (non-Javadoc)
			 * @see org.osgi.framework.ServiceFactory#getService(org.osgi.framework.Bundle, org.osgi.framework.ServiceRegistration)
			 */
			public Object getService(final Bundle bundle, final ServiceRegistration registration) {
				if (jdc == null) {
					try {
						jdc = new JMDNSDiscoveryContainer();
						jdc.connect(null, null);
					} catch (final IDCreateException e) {
						Trace.catching(JMDNSPlugin.PLUGIN_ID, JMDNSDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "getService(Bundle, ServiceRegistration)", e); //$NON-NLS-1$ //$NON-NLS-2$
					} catch (final ContainerConnectException e) {
						Trace.catching(JMDNSPlugin.PLUGIN_ID, JMDNSDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "getService(Bundle, ServiceRegistration)", e); //$NON-NLS-1$ //$NON-NLS-2$
						jdc = null;
					}
				}
				return jdc;
			}

			/* (non-Javadoc)
			 * @see org.osgi.framework.ServiceFactory#ungetService(org.osgi.framework.Bundle, org.osgi.framework.ServiceRegistration, java.lang.Object)
			 */
			public void ungetService(final Bundle bundle, final ServiceRegistration registration, final Object service) {
				//TODO-mkuppe we later might want to dispose jSLP when the last!!! consumer ungets the service 
				//Though don't forget about the (ECF) Container which might still be in use
			}
		}, props);

	}

	protected Bundle getBundle() {
		if (context == null) {
			return null;
		}
		return context.getBundle();
	}

	/**
	 * This method is called when the plug-in is stopped
	 */
	public void stop(final BundleContext ctxt) throws Exception {
		if (serviceRegistration != null) {
			ServiceReference reference = serviceRegistration.getReference();
			IDiscoveryLocator aLocator = (IDiscoveryLocator) ctxt.getService(reference);

			serviceRegistration.unregister();

			IContainer container = (IContainer) aLocator.getAdapter(IContainer.class);
			container.disconnect();
			container.dispose();

			serviceRegistration = null;
		}
		if (adapterManagerTracker != null) {
			adapterManagerTracker.close();
			adapterManagerTracker = null;
		}
		if (logServiceTracker != null) {
			logServiceTracker.close();
			logServiceTracker = null;
			logService = null;
		}
		this.context = ctxt;
		plugin = null;
	}

	/**
	 * Returns the shared instance.
	 */
	public synchronized static JMDNSPlugin getDefault() {
		return plugin;
	}

	/**
	 * @param string
	 * @param t
	 */
	public void logException(final String string, final Throwable t) {
		getLogService();
		if (logService != null) {
			logService.log(LogService.LOG_ERROR, string, t);
		}
	}

	/**
	 * @param string
	 * @param t
	 */
	public void logInfo(final String string, final Throwable t) {
		getLogService();
		if (logService != null) {
			logService.log(LogService.LOG_INFO, string, t);
		}
	}

	protected LogService getLogService() {
		if (logServiceTracker == null) {
			logServiceTracker = new ServiceTracker(this.context, LogService.class.getName(), null);
			logServiceTracker.open();
		}
		logService = (LogService) logServiceTracker.getService();
		if (logService == null) {
			logService = new SystemLogService(PLUGIN_ID);
		}
		return logService;
	}

	/**
	 * @param errorString
	 */
	public void logError(final String errorString) {
		getLogService();
		if (logService != null) {
			logService.log(LogService.LOG_ERROR, errorString);
		}
	}

}