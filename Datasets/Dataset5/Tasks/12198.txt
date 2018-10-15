exception.toString(), exception));

/*******************************************************************************
 * Copyright (c) 2008 IONA Technologies PLC
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 * IONA Technologies PLC - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.cxf.consumption.core;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

/**
 * The activator class controls the plug-in life cycle.
 * 
 * @author sclarke
 */
public class CXFConsumptionCorePlugin extends AbstractUIPlugin {
    // The plug-in ID
    public static final String PLUGIN_ID = "org.eclipse.jst.ws.cxf.consumption.core"; //$NON-NLS-1$

    // The shared instance
    private static CXFConsumptionCorePlugin plugin;

    /**
     * The constructor.
     */
    public CXFConsumptionCorePlugin() {
    }
    
    /**
     * Returns the shared instance.
     * 
     * @return the shared instance
     */
    public static CXFConsumptionCorePlugin getDefault() {
        return plugin;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ui.plugin.AbstractUIPlugin#start(org.osgi.framework.BundleContext)
     */
    @Override
    public void start(BundleContext context) throws Exception {
        super.start(context);
        plugin = this;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ui.plugin.AbstractUIPlugin#stop(org.osgi.framework.BundleContext)
     */
    @Override
    public void stop(BundleContext context) throws Exception {
        plugin = null;
        super.stop(context);
    }
    
    public static void logMessage(int severity, String message) {
        CXFConsumptionCorePlugin.log(new Status(severity, CXFConsumptionCorePlugin.PLUGIN_ID, 
            message));
    }

    public static void log(IStatus status) {
        CXFConsumptionCorePlugin.getDefault().getLog().log(status);
    }

    public static void log(Throwable exception) {
        CXFConsumptionCorePlugin.log(new Status(IStatus.ERROR, CXFConsumptionCorePlugin.PLUGIN_ID, 
            exception.getLocalizedMessage(), exception));
    }
}