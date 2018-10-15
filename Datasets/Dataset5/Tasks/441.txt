new Status(IStatus.OK, PLUGIN_ID, IStatus.OK, message, null));

/**
 * Copyright (c) 2006 Parity Communications, Inc. 
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Sergey Yakovlev - initial API and implementation
 */
package org.eclipse.ecf.internal.provider.rss;

import java.util.MissingResourceException;
import java.util.ResourceBundle;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.util.LogHelper;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.service.log.LogService;
import org.osgi.util.tracker.ServiceTracker;

/**
 * The main plugin class to be used in the desktop.
 * 
 */
public class RssPlugin implements BundleActivator {

	// public static final String NAMESPACE_IDENTIFIER = "ecf.rss";
	public static final String PLUGIN_ID = "org.eclipse.ecf.internal.provider.rss";

	// The shared instance.
	private static RssPlugin plugin;

	private BundleContext context = null;
	
	// Resource bundle.
	private ResourceBundle resourceBundle;

	private ServiceTracker logServiceTracker = null;

	/**
	 * Logs the given message.
	 * 
	 * @param message
	 *            a human-readable message, localized to the current locale.
	 */
	public static void log(String message) {
		getDefault().log(
				new Status(IStatus.OK, getDefault().PLUGIN_ID, IStatus.OK, message, null));
	}

	/**
	 * Logs the given message and exception.
	 * 
	 * @param message
	 *            a human-readable message, localized to the current locale.
	 * @param e
	 *            a low-level exception, or <code>null</code> if not
	 *            applicable.
	 */
	public static void log(String message, Throwable e) {
		getDefault().log(
				new Status(IStatus.ERROR, PLUGIN_ID, IStatus.OK, "Caught exception", e));
	}

	/**
	 * The constructor.
	 */
	public RssPlugin() {
		super();
		plugin = this;
		try {
			resourceBundle = ResourceBundle
					.getBundle("org.eclipse.ecf.internal.provider.rss.RssPluginResources");
		} catch (MissingResourceException x) {
			resourceBundle = null;
		}
	}

	protected LogService getLogService() {
		if (logServiceTracker == null) {
			logServiceTracker = new ServiceTracker(this.context,
					LogService.class.getName(), null);
			logServiceTracker.open();
		}
		return (LogService) logServiceTracker.getService();
	}

	public void log(IStatus status) {
		LogService logService = getLogService();
		if (logService != null) {
			logService.log(LogHelper.getLogCode(status), LogHelper
					.getLogMessage(status), status.getException());
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext context) throws Exception {
		this.context = context;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		if (logServiceTracker != null) {
			logServiceTracker.close();
			logServiceTracker = null;
		}
		this.context = null;
		plugin = null;
	}

	/**
	 * Returns the shared instance.
	 * 
	 * @return the shared instance.
	 */
	public static RssPlugin getDefault() {
		return plugin;
	}

	/**
	 * Returns the string from the plugin's resource bundle, or 'key' if not
	 * found.
	 * 
	 * @param key
	 *            the key for the desired string.
	 * @return the string for the given key.
	 */
	public static String getResourceString(String key) {
		ResourceBundle bundle = RssPlugin.getDefault().getResourceBundle();
		try {
			return (bundle != null) ? bundle.getString(key) : key;
		} catch (MissingResourceException e) {
			return key;
		}
	}

	/**
	 * Returns the plugin's resource bundle.
	 * 
	 * @return a resource bundle.
	 */
	public ResourceBundle getResourceBundle() {
		return resourceBundle;
	}
}