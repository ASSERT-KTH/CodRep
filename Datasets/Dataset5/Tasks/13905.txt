private static final String PLUGIN_ID = "ID: org.eclipse.m2t.common.recipe";

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.m2t.common.recipe.ui;
import java.net.MalformedURLException;
import java.net.URL;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.m2t.common.recipe.ui.shared.iface.ITraceLog;
import org.eclipse.m2t.common.recipe.ui.shared.messages.DialogMessages;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;
/**
 * 
 * This class manages the initialization for a generator plugin. If the plugin
 * is run in debug mode (see plugin.properties) then a default logger is
 * initialized with the settings read from the plugin.properties. It also
 * manages the reading of images.
 *  
 */
public class RecipePlugin extends AbstractUIPlugin implements ITraceLog {
    
    
    private static final String PLUGIN_ID = "ID: org.openarchitectureware.recipe";
	/**
	 * The shared instance
	 */
	private static RecipePlugin cvGeneratorPlugin;
	
	/**
	 * Creates new Generator plugin. Reads logging information from descriptor
	 * and adds a LogListener if needed
	 * 
	 * @see Plugin.properties
	 */
	public RecipePlugin() {
	    super();
		cvGeneratorPlugin = this;
	}
	/**
	 * Returns the shared instance of GeneratorPlugin
	 */
	public static RecipePlugin getDefault() {
	    if (cvGeneratorPlugin==null) {
	        IStatus status = new Status(Status.ERROR,getPluginId(),ITraceLog.CRITICAL , "singleton not initialized",new NullPointerException());
	        Platform.getLog(Platform.getBundle(getPluginId())).log(status);
	    }
		return cvGeneratorPlugin;
	}
	/**
	 * Returns an ImageDescriptor for a given name
	 * 
	 * @param aName
	 *            a name of an image
	 */
	public ImageDescriptor getImageDescriptor(String aName) {
		ImageDescriptor imageDesc = null;
		try {
			URL url = new URL(getBundle().getEntry("/icons/"), aName);
			imageDesc = ImageDescriptor.createFromURL(url);
		} catch (MalformedURLException e) {
			imageDesc = ImageDescriptor.getMissingImageDescriptor();
		}
		return imageDesc;
	}
	/**
	 * Returns the unique id associated with the plugin
	 */
	public static String getPluginId() {
		return PLUGIN_ID;
	}
	/**
	 * Returns a message for a given key
	 * 
	 * @param aKey
	 *            a key associated with a message
	 */
	public static String getMessage(String aKey) {
		return DialogMessages.getMessage(aKey);
	}
	/**
	 * Logs a status
	 * 
	 * @param aStatus
	 *            a status to be logged
	 * @see Plugin.properties
	 */
	public static void log(IStatus aStatus) {
		getDefault().getLog().log(aStatus);
	}
	
	/**
	 * Logs a message
	 * 
	 * @param aMessage
	 *            a message to be logged
	 * @see Plugin.properties
	 */
	public void log(String aMessage) {
		log(new Status(IStatus.INFO, getPluginId(), INFO, aMessage, null));
	}
	/**
	 * Logs a message for a given level
	 * 
	 * @param aLevel
	 *            a log level for a message
	 * @param aMessage
	 *            a message to be logged
	 * @see Plugin.properties
	 */
	public void log(int aLevel, String aMessage) {
		log(new Status(IStatus.INFO, getPluginId(), aLevel, aMessage, null));
	}
	/**
	 * Logs an Exception
	 * 
	 * @param anException
	 *            an exception to be logged
	 * @see Plugin.properties
	 */
	public static void log(Exception anException) {
		log(new Status(IStatus.ERROR, getPluginId(), EXCEPTION, "EXCEPTION",
				anException));
	}
	
	
	public IWorkbenchPage getActivePage() {
		IWorkbenchWindow window= getWorkbench().getActiveWorkbenchWindow();
		if (window == null)
			return null;
		return getWorkbench().getActiveWorkbenchWindow().getActivePage();
	}
	
	public void start(BundleContext context) throws Exception {
		super.start(context);
	}
}