import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;

/*******************************************************************************
 * Copyright (c) 2004 Peter Nehrer and Composent, Inc.
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Peter Nehrer - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.sdo;

import java.util.Hashtable;

import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.util.ECFException;

/**
 * @author pnehrer
 */
public class DataGraphSharingFactory {

    public static final String TRACE_TAG = "DataGraphSharingFactory";

    private static final Hashtable managers = new Hashtable();

    private DataGraphSharingFactory() {
    }

    public static final IDataGraphSharing getDataGraphSharing(
            ISharedObjectContainer container, String name) throws ECFException {

        IDataGraphSharingManager instantiator = (IDataGraphSharingManager) managers
                .get(name);
        if (instantiator == null)
            return null;
        else
            return instantiator.getInstance(container);
    }

    public static void registerManager(String name,
            IDataGraphSharingManager manager) {
        if (SDOPlugin.isTracing(TRACE_TAG))
            SDOPlugin.getTraceLog().println("registerManager: " + name);

        managers.put(name, manager);
    }

    public static void unregisterManager(String name) {
        if (SDOPlugin.isTracing(TRACE_TAG))
            SDOPlugin.getTraceLog().println("unregisterManager: " + name);

        managers.remove(name);
    }

    static void unregisterAllManagers() {
        if (SDOPlugin.isTracing(TRACE_TAG))
            SDOPlugin.getTraceLog().println("unregisterAllManagers");

        managers.clear();
    }
}