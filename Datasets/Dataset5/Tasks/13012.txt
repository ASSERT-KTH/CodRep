}, (Dictionary) rsaProps);

/*******************************************************************************
 * Copyright (c) 2010-2011 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.remoteserviceadmin;

import java.util.Dictionary;
import java.util.Properties;
import java.util.UUID;

import javax.xml.parsers.SAXParserFactory;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.util.LogHelper;
import org.eclipse.ecf.core.util.SystemLogService;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.EndpointDescriptionAdvertiser;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.EndpointDescriptionLocator;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.IEndpointDescriptionAdvertiser;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.RemoteServiceAdmin;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.BasicTopologyManager;
import org.osgi.framework.Bundle;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.framework.Constants;
import org.osgi.framework.ServiceFactory;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.log.LogService;
import org.osgi.util.tracker.ServiceTracker;

public class Activator implements BundleActivator {

	public static final String PLUGIN_ID = "org.eclipse.ecf.osgi.services.remoteserviceadmin";

	private static BundleContext context;
	private static Activator instance;

	static BundleContext getContext() {
		return context;
	}

	public static Activator getDefault() {
		return instance;
	}

	private ServiceRegistration remoteServiceAdminRegistration;

	private EndpointDescriptionLocator endpointDescriptionLocator;
	private EndpointDescriptionAdvertiser endpointDescriptionAdvertiser;
	private ServiceRegistration endpointDescriptionAdvertiserRegistration;

	private BasicTopologyManager basicTopologyManager;

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext
	 * )
	 */
	public void start(BundleContext bundleContext) throws Exception {
		Activator.context = bundleContext;
		Activator.instance = this;
		startRemoteServiceAdmin();

		endpointDescriptionLocator = new EndpointDescriptionLocator(context);

		startEndpointDescriptionAdvertiser();

		basicTopologyManager = new BasicTopologyManager(context);
		// start topology manager first
		basicTopologyManager.start();
		// start endpointDescriptionLocator
		endpointDescriptionLocator.start();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext bundleContext) throws Exception {
		if (endpointDescriptionLocator != null) {
			endpointDescriptionLocator.close();
			endpointDescriptionLocator = null;
		}
		if (basicTopologyManager != null) {
			basicTopologyManager.close();
			basicTopologyManager = null;
		}
		stopRemoteServiceAdmin();
		stopEndpointDescriptionAdvertiser();
		stopSAXParserTracker();
		stopLogServiceTracker();
		stopContainerManagerTracker();
		Activator.context = null;
		Activator.instance = null;
	}

	private void startRemoteServiceAdmin() {
		Properties rsaProps = new Properties();
		rsaProps.put(RemoteServiceAdmin.SERVICE_PROP, new Boolean(true));
		remoteServiceAdminRegistration = context.registerService(
				org.osgi.service.remoteserviceadmin.RemoteServiceAdmin.class
						.getName(), new ServiceFactory() {
					public Object getService(Bundle bundle,
							ServiceRegistration registration) {
						return new RemoteServiceAdmin(bundle);
					}

					public void ungetService(Bundle bundle,
							ServiceRegistration registration, Object service) {
						if (service != null) ((RemoteServiceAdmin) service).close();
					}
				}, rsaProps);
	}

	private void stopRemoteServiceAdmin() {
		if (remoteServiceAdminRegistration != null) {
			remoteServiceAdminRegistration.unregister();
			remoteServiceAdminRegistration = null;
		}
	}

	private void startEndpointDescriptionAdvertiser() {
		final Properties properties = new Properties();
		properties.put(Constants.SERVICE_RANKING,
				new Integer(Integer.MIN_VALUE));
		endpointDescriptionAdvertiser = new EndpointDescriptionAdvertiser(
				endpointDescriptionLocator);
		endpointDescriptionAdvertiserRegistration = getContext()
				.registerService(
						IEndpointDescriptionAdvertiser.class.getName(),
						endpointDescriptionAdvertiser, (Dictionary) properties);
	}

	private void stopEndpointDescriptionAdvertiser() {
		if (endpointDescriptionAdvertiserRegistration != null) {
			endpointDescriptionAdvertiserRegistration.unregister();
			endpointDescriptionAdvertiserRegistration = null;
		}
		if (endpointDescriptionAdvertiser != null) {
			endpointDescriptionAdvertiser.close();
			endpointDescriptionAdvertiser = null;
		}
	}

	public String getFrameworkUUID() {
		if (context == null)
			return null;
		// code get and set the framework uuid property as specified in
		// r2.enterprise.pdf pg 297
		synchronized ("org.osgi.framework.uuid") {
			String result = context.getProperty("org.osgi.framework.uuid");
			if (result == null) {
				UUID newUUID = UUID.randomUUID();
				result = newUUID.toString();
				System.setProperty("org.osgi.framework.uuid",
						newUUID.toString());
			}
			return result;
		}
	}

	// Sax parser

	private Object saxParserFactoryTrackerLock = new Object();
	private ServiceTracker saxParserFactoryTracker;

	public SAXParserFactory getSAXParserFactory() {
		if (instance == null)
			return null;
		synchronized (saxParserFactoryTrackerLock) {
			if (saxParserFactoryTracker == null) {
				saxParserFactoryTracker = new ServiceTracker(context,
						SAXParserFactory.class.getName(), null);
				saxParserFactoryTracker.open();
			}
			return (SAXParserFactory) saxParserFactoryTracker.getService();
		}
	}

	private void stopSAXParserTracker() {
		synchronized (saxParserFactoryTrackerLock) {
			if (saxParserFactoryTracker != null) {
				saxParserFactoryTracker.close();
				saxParserFactoryTracker = null;
			}
		}
	}

	// Logging

	private ServiceTracker logServiceTracker = null;
	private LogService logService = null;
	private Object logServiceTrackerLock = new Object();

	public LogService getLogService() {
		if (context == null)
			return null;
		synchronized (logServiceTrackerLock) {
			if (logServiceTracker == null) {
				logServiceTracker = new ServiceTracker(context,
						LogService.class.getName(), null);
				logServiceTracker.open();
			}
			logService = (LogService) logServiceTracker.getService();
			if (logService == null)
				logService = new SystemLogService(PLUGIN_ID);
			return logService;
		}
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

	private void stopLogServiceTracker() {
		synchronized (logServiceTrackerLock) {
			if (logServiceTracker != null) {
				logServiceTracker.close();
				logServiceTracker = null;
				logService = null;
			}
		}
	}

	private ServiceTracker containerManagerTracker;

	public IContainerManager getContainerManager() {
		if (containerManagerTracker == null) {
			containerManagerTracker = new ServiceTracker(context,
					IContainerManager.class.getName(), null);
			containerManagerTracker.open();
		}
		return (IContainerManager) containerManagerTracker.getService();
	}

	private void stopContainerManagerTracker() {
		if (containerManagerTracker != null) {
			containerManagerTracker.close();
			containerManagerTracker = null;
		}
	}
}