public static final String PLUGIN_ID = "org.eclipse.ecf.ui"; //$NON-NLS-1$

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

package org.eclipse.ecf.internal.ui;

import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.jface.resource.ImageRegistry;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;
import org.osgi.util.tracker.ServiceTracker;

/**
 * The main plugin class to be used in the desktop.
 */
public class Activator extends AbstractUIPlugin {

	public static final String PLUGIN_ID = "org.eclipse.ecf.ui";

	public static final String PREF_DISPLAY_TIMESTAMP = "TextChatComposite.displaytimestamp";

	// The shared instance.
	private static Activator plugin;

	private ServiceTracker extensionRegistryTracker = null;

	public IExtensionRegistry getExtensionRegistry() {
		return (IExtensionRegistry) extensionRegistryTracker.getService();
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
	public Activator() {
		super();
		plugin = this;
	}

	/**
	 * This method is called upon plug-in activation
	 */
	public void start(BundleContext context) throws Exception {
		super.start(context);
		this.extensionRegistryTracker = new ServiceTracker(context,
				IExtensionRegistry.class.getName(), null);
		this.extensionRegistryTracker.open();
	}

	/**
	 * This method is called when the plug-in is stopped
	 */
	public void stop(BundleContext context) throws Exception {
		if (extensionRegistryTracker != null) {
			extensionRegistryTracker.close();
			extensionRegistryTracker = null;
		}
		plugin = null;
		super.stop(context);
	}

	/**
	 * Returns the shared instance.
	 */
	public static Activator getDefault() {
		return plugin;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ui.plugin.AbstractUIPlugin#createImageRegistry()
	 */
	protected ImageRegistry createImageRegistry() {
		ImageRegistry registry = super.createImageRegistry();

		registry.put(SharedImages.IMG_USER_AVAILABLE, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID,
						IImageFiles.USER_AVAILABLE).createImage());
		registry.put(SharedImages.IMG_USER_AWAY, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.USER_AWAY)
				.createImage());
		registry.put(SharedImages.IMG_USER_DND, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.USER_DND)
				.createImage());
		registry.put(SharedImages.IMG_GROUP, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.GROUP)
				.createImage());
		registry.put(SharedImages.IMG_USER_UNAVAILABLE, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID,
						IImageFiles.USER_UNAVAILABLE).createImage());

		registry.put(SharedImages.IMG_SEND, PlatformUI.getWorkbench()
				.getSharedImages().getImage(ISharedImages.IMG_TOOL_UNDO));

		registry.put(SharedImages.IMG_DISCONNECT_DISABLED, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID,
						IImageFiles.DISCONNECT_DISABLED).createImage());
		registry.put(SharedImages.IMG_DISCONNECT, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID,
						IImageFiles.DISCONNECT_ENABLED).createImage());

		registry.put(SharedImages.IMG_ADD_GROUP, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.ADD_GROUP)
				.createImage());
		registry.put(SharedImages.IMG_ADD_BUDDY, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.ADD_BUDDY)
				.createImage());

		registry.put(SharedImages.IMG_ADD_CHAT, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.ADD_CHAT)
				.createImage());

		registry.put(SharedImages.IMG_MESSAGE, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.SEND_MESSAGE)
				.createImage());

		registry.put(SharedImages.IMG_ADD, AbstractUIPlugin
				.imageDescriptorFromPlugin(PLUGIN_ID, IImageFiles.ADD)
				.createImage());

		return registry;
	}

}