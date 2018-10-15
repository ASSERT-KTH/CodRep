Platform.getDebugOption(PLUGIN_ID + "/debug/semanticCheck")).booleanValue();

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.launching;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Plugin;
import org.eclipse.dltk.core.DLTKCore;
import org.eclipse.dltk.core.ElementChangedEvent;
import org.eclipse.wst.xquery.internal.launching.XQDTBuildPathChangedListener;
import org.osgi.framework.BundleContext;

/**
 * The activator class controls the plug-in life cycle
 */
public class XQDTLaunchingPlugin extends Plugin {

    // The plug-in ID
    public static final String PLUGIN_ID = "org.eclipse.wst.xquery.launching";

    // The shared instance
    private static XQDTLaunchingPlugin plugin;

    // Automatic XQuery processor detection trace flag
    public static final boolean DEBUG_AUTOMATIC_PROCESSOR_DETECTION = Boolean.valueOf(
            Platform.getDebugOption(PLUGIN_ID + "/debug/processors/automaticDetection")).booleanValue();
    // XQuery semantic checker trace flag
    public static final boolean DEBUG_SEMANTIC_CHECK = Boolean.valueOf(
            Platform.getDebugOption(PLUGIN_ID + "/debug/debug/semanticCheck")).booleanValue();

    private static XQDTBuildPathChangedListener fBuildPathListener = new XQDTBuildPathChangedListener();

    /**
     * The constructor
     */
    public XQDTLaunchingPlugin() {
        plugin = this;
    }

    public void start(BundleContext context) throws Exception {
        super.start(context);

        DLTKCore.addElementChangedListener(fBuildPathListener, ElementChangedEvent.POST_CHANGE);
    }

    public void stop(BundleContext context) throws Exception {
        DLTKCore.removeElementChangedListener(fBuildPathListener);

        plugin = null;
        super.stop(context);
    }

    /**
     * Returns the shared instance
     * 
     * @return the shared instance
     */
    public static XQDTLaunchingPlugin getDefault() {
        return plugin;
    }

    public static void log(IStatus status) {
        getDefault().getLog().log(status);
    }
}