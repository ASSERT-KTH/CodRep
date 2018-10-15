package org.eclipse.ecf.internal.ui;

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

package org.eclipse.ecf.ui;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.resource.ImageRegistry;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.plugin.*;
import org.osgi.framework.BundleContext;
import java.util.*;

/**
 * The main plugin class to be used in the desktop.
 */
public class UiPlugin extends AbstractUIPlugin {
	
	public static final String PLUGIN_ID = "org.eclipse.ecf.ui";
	
    private ImageRegistry registry = null;
    
    public static final String PREF_DISPLAY_TIMESTAMP = "TextChatComposite.displaytimestamp";
    
	//The shared instance.
	private static UiPlugin plugin;
	//Resource bundle.
	private ResourceBundle resourceBundle;
	
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
	public UiPlugin() {
		super();
		plugin = this;
	}

	/**
	 * This method is called upon plug-in activation
	 */
	public void start(BundleContext context) throws Exception {
		super.start(context);
	}

	/**
	 * This method is called when the plug-in is stopped
	 */
	public void stop(BundleContext context) throws Exception {
		super.stop(context);
		plugin = null;
		resourceBundle = null;
	}

	/**
	 * Returns the shared instance.
	 */
	public static UiPlugin getDefault() {
		return plugin;
	}

	/**
	 * Returns the string from the plugin's resource bundle,
	 * or 'key' if not found.
	 */
	public static String getResourceString(String key) {
		ResourceBundle bundle = UiPlugin.getDefault().getResourceBundle();
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
				resourceBundle = ResourceBundle.getBundle("org.eclipse.ecf.ui.UiPluginResources");
		} catch (MissingResourceException x) {
			resourceBundle = null;
		}
		return resourceBundle;
	}
    /* (non-Javadoc)
     * @see org.eclipse.ui.plugin.AbstractUIPlugin#createImageRegistry()
     */
    protected ImageRegistry createImageRegistry() {
        registry = super.createImageRegistry();
       
        registry.put(UiPluginConstants.DECORATION_PROJECT, PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJ_FOLDER));
        registry.put(UiPluginConstants.DECORATION_USER, AbstractUIPlugin.imageDescriptorFromPlugin(PLUGIN_ID, "icons/enabled/presence_member.gif").createImage());
        registry.put(UiPluginConstants.DECORATION_USER_INACTIVE, AbstractUIPlugin.imageDescriptorFromPlugin(PLUGIN_ID, "icons/disabled/presence_member.gif").createImage());
        registry.put(UiPluginConstants.DECORATION_TIME, PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
        registry.put(UiPluginConstants.DECORATION_TASK, PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJ_ELEMENT));
        
        registry.put(UiPluginConstants.DECORATION_SEND , PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_UNDO));
        registry.put(UiPluginConstants.DECORATION_RECEIVE , PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_REDO));
        registry.put(UiPluginConstants.DECORATION_PRIVATE , PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJS_WARN_TSK));
        registry.put(UiPluginConstants.DECORATION_SYSTEM_MESSAGE , PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJS_INFO_TSK));
        return registry;
    }

}