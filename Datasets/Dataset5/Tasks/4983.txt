Platform.getDebugOption(PLUGIN_ID + "/debug/documentPartitioner")).booleanValue();

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
package org.eclipse.wst.xquery.core;

import java.text.MessageFormat;
import java.util.Date;

import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Plugin;
import org.osgi.framework.BundleContext;

/**
 * The activator class controls the plug-in life cycle
 */
public class XQDTCorePlugin extends Plugin {

    // The plug-in ID
    public static final String PLUGIN_ID = "org.eclipse.wst.xquery.core";

    // The shared instance
    private static XQDTCorePlugin plugin;

    public static final boolean DEBUG = Boolean.valueOf(Platform.getDebugOption(PLUGIN_ID + "/debug")).booleanValue();
    public static final boolean DEBUG_PARSER_ACTIONS = Boolean.valueOf(
            Platform.getDebugOption(PLUGIN_ID + "/debug/parser/actions")).booleanValue();
    public static final boolean DEBUG_PARSER_RESULTS = Boolean.valueOf(
            Platform.getDebugOption(PLUGIN_ID + "/debug/parser/results")).booleanValue();
    public static final boolean DEBUG_DOCUMENT_PARTITIONER = Boolean.valueOf(
            Platform.getDebugOption(PLUGIN_ID + "/debug/document_partitioner")).booleanValue();

    private static IXQDTUriResolver fUriResolver;

    /**
     * The constructor
     */
    public XQDTCorePlugin() {
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.core.runtime.Plugins#start(org.osgi.framework.BundleContext)
     */
    public void start(BundleContext context) throws Exception {
        super.start(context);
        plugin = this;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.core.runtime.Plugin#stop(org.osgi.framework.BundleContext)
     */
    public void stop(BundleContext context) throws Exception {
        plugin = null;
        super.stop(context);
    }

    /**
     * Returns the shared instance
     * 
     * @return the shared instance
     */
    public static XQDTCorePlugin getDefault() {
        return plugin;
    }

    public static void trace(String msg) {
        System.out.println(MessageFormat.format("[{0,date,yyyy-MM-dd} {0,time,HH:mm:ss}] {1}", new Object[] {
                new Date(), msg }));
    }

    public IXQDTUriResolver getUriResolver() {
        if (fUriResolver == null) {
            fUriResolver = new XQDTUriResolver();
        }
        return fUriResolver;
    }
}