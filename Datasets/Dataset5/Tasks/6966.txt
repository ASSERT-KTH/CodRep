public static final String COLLABORATION_IMAGE = "collaboration"; //$NON-NLS-1$

/****************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.example.collab;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.resource.FontRegistry;
import org.eclipse.jface.resource.ImageRegistry;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

/**
 * The main plug-in class to be used in the desktop.
 */
public class ClientPlugin extends AbstractUIPlugin implements ClientPluginConstants {
	public static final String PLUGIN_ID = "org.eclipse.ecf.example.collab"; //$NON-NLS-1$

	public static final String COLLABORATION_IMAGE = "collaboration";

	// The shared instance.
	private static ClientPlugin plugin;

	private FontRegistry fontRegistry = null;
	private ServerStartup serverStartup = null;

	private BundleContext context;

	public static void log(String message) {
		getDefault().getLog().log(new Status(IStatus.OK, ClientPlugin.getDefault().getBundle().getSymbolicName(), IStatus.OK, message, null));
	}

	public static void log(String message, Throwable e) {
		getDefault().getLog().log(new Status(IStatus.ERROR, ClientPlugin.getDefault().getBundle().getSymbolicName(), IStatus.OK, message, e));
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
		// this.getPreferenceStore().setDefault(ClientPlugin.PREF_CHAT_FONT,
		// "");
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_CONFIRM_FILE_SEND, true);
		// this.getPreferenceStore().setDefault(ClientPlugin.PREF_CONFIRM_FILE_RECEIVE,
		// true);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_CONFIRM_REMOTE_VIEW, true);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_START_SERVER, false);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_REGISTER_SERVER, false);

		this.getPreferenceStore().setDefault(ClientPlugin.PREF_SHAREDEDITOR_PLAY_EVENTS_IMMEDIATELY, true);
		this.getPreferenceStore().setDefault(ClientPlugin.PREF_SHAREDEDITOR_ASK_RECEIVER, true);
	}

	/**
	 * This method is called upon plug-in activation
	 * @param ctxt 
	 * @throws Exception 
	 */
	public void start(BundleContext ctxt) throws Exception {
		super.start(ctxt);
		setPreferenceDefaults();
		this.context = ctxt;
	}

	protected BundleContext getContext() {
		return context;
	}

	public synchronized void initServer() throws Exception {
		if (serverStartup == null) {
			serverStartup = new ServerStartup();
		}
	}

	public synchronized boolean isServerActive() {
		if (serverStartup == null)
			return false;
		else
			return serverStartup.isActive();
	}

	public synchronized void disposeServer() {
		if (serverStartup != null) {
			serverStartup.dispose();
			serverStartup = null;
		}
	}

	/**
	 * This method is called when the plug-in is stopped
	 * @param context 
	 * @throws Exception 
	 */
	public void stop(BundleContext context) throws Exception {
		super.stop(context);
		plugin = null;
		context = null;
		disposeServer();
	}

	public FontRegistry getFontRegistry() {
		return this.fontRegistry;
	}

	public Shell getActiveShell() {
		return this.getWorkbench().getDisplay().getActiveShell();
	}

	protected void initializeImageRegistry(ImageRegistry registry) {
		registry.put(COLLABORATION_IMAGE, AbstractUIPlugin.imageDescriptorFromPlugin(PLUGIN_ID, "icons/collaboration.gif")); //$NON-NLS-1$
	}

	/**
	 * Returns the shared instance.
	 * @return default client plugin
	 */
	public static ClientPlugin getDefault() {
		return plugin;
	}
}