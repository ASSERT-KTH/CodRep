.getBundle("org.eclipse.ecf.example.collab.ClientPlugin");

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

package org.eclipse.ecf.example.collab;

import java.net.URL;
import java.util.MissingResourceException;
import java.util.ResourceBundle;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jface.resource.FontRegistry;
import org.eclipse.jface.resource.ImageRegistry;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

/**
 * The main plugin class to be used in the desktop.
 */
public class ClientPlugin extends AbstractUIPlugin implements
		ClientPluginConstants {

	public static final String PLUGIN_ID = "org.eclipse.ecf.example.collab";
	
	// The shared instance.
	private static ClientPlugin plugin;

	// Resource bundle.
	private ResourceBundle resourceBundle;
	private static URL pluginLocation;
	private ImageRegistry registry = null;
	private FontRegistry fontRegistry = null;

	private ServerStartup serverStartup = null;
	private DiscoveryStartup discoveryStartup = null;
	
	public static URL getPluginTopLocation() {
		return pluginLocation;
	}

	public static void log(String message) {
		getDefault().getLog().log(
				new Status(IStatus.OK, PLUGIN_ID, IStatus.OK, message, null));
	}

	public static void log(String message, Throwable e) {
		getDefault().getLog().log(
				new Status(IStatus.ERROR, PLUGIN_ID, IStatus.OK,
						"Caught exception", e));
	}

	/**
	 * The constructor.
	 */
	public ClientPlugin() {
		super();
		plugin = this;
		this.fontRegistry = new FontRegistry();
	}

	protected void setPreferenceDefaults() {
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_USE_CHAT_WINDOW, false);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_DISPLAY_TIMESTAMP, true);
		
		//this.getPreferenceStore().setDefault(ClientPlugin.PREF_CHAT_FONT, "");

		this.getPreferenceStore().setDefault(ClientPlugin.PREF_CONFIRM_FILE_SEND, true);
		//this.getPreferenceStore().setDefault(ClientPlugin.PREF_CONFIRM_FILE_RECEIVE, true);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_CONFIRM_REMOTE_VIEW, true);
		
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_START_SERVER,true);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_REGISTER_SERVER,true);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_START_DISCOVERY,true);
	}
	
	class ClientStartupJob extends Job {

		public ClientStartupJob(String name) {
			super(name);
		}

		protected IStatus run(IProgressMonitor monitor) {
			try {
				initDiscovery();
				initServer();
			} catch (Exception e) {
				log("Exception on initialization",e);
			}
			return new Status(IStatus.OK, PLUGIN_ID, IStatus.OK, "Discovery complete", null);
		}
		
		
	}
	/**
	 * This method is called upon plug-in activation
	 */
	public void start(BundleContext context) throws Exception {
		super.start(context);
		setPreferenceDefaults();
		ClientStartupJob job = new ClientStartupJob("Setting up Dynamic Service Discovery");
		job.schedule();
	}

	protected synchronized void initDiscovery() throws Exception {
		if (discoveryStartup == null && getPreferenceStore().getBoolean(PREF_START_DISCOVERY)) {
			discoveryStartup = new DiscoveryStartup();
		}
	}
	
	protected synchronized void initServer() throws Exception {
		if (serverStartup == null && getPreferenceStore().getBoolean(PREF_START_SERVER)) {
			serverStartup = new ServerStartup();
		}
	}
	
	protected synchronized boolean isDiscoveryActive() {
		if (discoveryStartup == null) return false;
		else return discoveryStartup.isActive();
	}
	protected synchronized boolean isServerActive() {
		if (serverStartup == null) return false;
		else return serverStartup.isActive();
	}
	protected synchronized void disposeDiscovery() {
		if (discoveryStartup != null) {
			discoveryStartup.dispose();
			discoveryStartup = null;
		}
	}
	protected synchronized void disposeServer() {
		if (serverStartup != null) {
			serverStartup.dispose();
			serverStartup = null;
		}
	}
	/**
	 * This method is called when the plug-in is stopped
	 */
	public void stop(BundleContext context) throws Exception {
		super.stop(context);
		plugin = null;
		resourceBundle = null;
		disposeServer();
		disposeDiscovery();
	}

	public FontRegistry getFontRegistry() {
		return this.fontRegistry;
	}

	public Shell getActiveShell() {
		return this.getWorkbench().getDisplay().getActiveShell();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ui.plugin.AbstractUIPlugin#createImageRegistry()
	 */
	protected ImageRegistry createImageRegistry() {
		registry = super.createImageRegistry();

		registry.put(ClientPluginConstants.DECORATION_PROJECT, PlatformUI
				.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_OBJ_FOLDER));
		registry.put(ClientPluginConstants.DECORATION_USER, AbstractUIPlugin
				.imageDescriptorFromPlugin("org.eclipse.ecf.example.collab",
						"icons/presence_member.gif").createImage());
		registry.put(ClientPluginConstants.DECORATION_TIME, PlatformUI
				.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_TOOL_FORWARD));
		registry.put(ClientPluginConstants.DECORATION_TASK, PlatformUI
				.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_OBJ_ELEMENT));

		registry.put(ClientPluginConstants.DECORATION_SEND, PlatformUI
				.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_TOOL_UNDO));
		registry.put(ClientPluginConstants.DECORATION_RECEIVE, PlatformUI
				.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_TOOL_REDO));
		registry.put(ClientPluginConstants.DECORATION_PRIVATE, PlatformUI
				.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_OBJS_WARN_TSK));
		registry.put(ClientPluginConstants.DECORATION_SYSTEM_MESSAGE,
				PlatformUI.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_OBJS_INFO_TSK));
		return registry;
	}

	/**
	 * Returns the shared instance.
	 */
	public static ClientPlugin getDefault() {
		return plugin;
	}

	/**
	 * Returns the string from the plugin's resource bundle, or 'key' if not
	 * found.
	 */
	public static String getResourceString(String key) {
		ResourceBundle bundle = ClientPlugin.getDefault().getResourceBundle();
		try {
			return (bundle != null) ? bundle.getString(key) : key;
		} catch (MissingResourceException e) {
			return key;
		}
	}

	/**
	 * Returns the plugin's resource bundle,
	 */
	public ResourceBundle getResourceBundle() {
		try {
			if (resourceBundle == null)
				resourceBundle = ResourceBundle
						.getBundle("org.eclipse.ecf.example.collab.ClientPluginResources");
		} catch (MissingResourceException x) {
			resourceBundle = null;
		}
		return resourceBundle;
	}

}