package org.eclipse.ecf.internal.provider.xmpp;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp;

import java.util.MissingResourceException;
import java.util.ResourceBundle;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Plugin;
import org.eclipse.core.runtime.Status;
import org.osgi.framework.BundleContext;

/**
 * The main plugin class to be used in the desktop.
 */
public class XmppPlugin extends Plugin {
	public static final String ID = "org.eclipse.ecf.provider.xmpp";
    protected static final String NAMESPACE_IDENTIFIER = "ecf.xmpp";
    protected static final String SECURE_NAMESPACE_IDENTIFIER = "ecf.xmpps";
    protected static final String ROOM_NAMESPACE_IDENTIFIER = "xmpp.room.jive";
	//The shared instance.
	private static XmppPlugin plugin;
	//Resource bundle.
	private ResourceBundle resourceBundle;
	
	public static void log(String message) {
		getDefault().getLog().log(
				new Status(IStatus.OK, XmppPlugin.getDefault().getBundle().getSymbolicName(), IStatus.OK, message, null));
	}

	public static void log(String message, Throwable e) {
		getDefault().getLog().log(
				new Status(IStatus.ERROR, XmppPlugin.getDefault().getBundle().getSymbolicName(), IStatus.OK,
						"Caught exception", e));
	}

	/**
	 * The constructor.
	 */
	public XmppPlugin() {
		super();
		plugin = this;
		try {
			resourceBundle = ResourceBundle.getBundle("org.eclipse.ecf.provider.xmpp.XmppPluginResources");
		} catch (MissingResourceException x) {
			resourceBundle = null;
		}
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
	}

	/**
	 * Returns the shared instance.
	 */
	public static XmppPlugin getDefault() {
		return plugin;
	}

	/**
	 * Returns the string from the plugin's resource bundle,
	 * or 'key' if not found.
	 */
	public static String getResourceString(String key) {
		ResourceBundle bundle = XmppPlugin.getDefault().getResourceBundle();
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
		return resourceBundle;
	}
    public String getNamespaceIdentifier() {
    	return NAMESPACE_IDENTIFIER;
    }
    public String getSecureNamespaceIdentifier() {
    	return SECURE_NAMESPACE_IDENTIFIER;
    }
    public String getRoomNamespaceIdentifier() {
    	return ROOM_NAMESPACE_IDENTIFIER;
    }
}