+ "\" id=\"defaultSausalitoCoreSDK\" name=\"Sausalito CoreSDK 1.0.12\" path=\""

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
package org.eclipse.wst.xquery.set.launching;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Plugin;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.variables.VariablesPlugin;
import org.eclipse.dltk.core.environment.IFileHandle;
import org.eclipse.dltk.core.internal.environment.LocalEnvironment;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.launching.IInterpreterInstallChangedListener;
import org.eclipse.dltk.launching.PropertyChangeEvent;
import org.eclipse.dltk.launching.ScriptRuntime;
import org.eclipse.wst.xquery.set.internal.launching.CoreSDKInstall;
import org.osgi.framework.BundleContext;

/**
 * The activator class controls the plug-in life cycle
 */
public class SETLaunchingPlugin extends Plugin implements IInterpreterInstallChangedListener {

    // The plug-in ID
    public static final String PLUGIN_ID = "org.eclipse.wst.xquery.set.launching";

    // The shared instance
    private static SETLaunchingPlugin plugin;

    public static final boolean DEBUG_SERVER = Boolean.valueOf(Platform.getDebugOption(PLUGIN_ID + "/debug/server"))
            .booleanValue();

    /**
     * The constructor
     */
    public SETLaunchingPlugin() {
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.core.runtime.Plugins#start(org.osgi.framework.BundleContext)
     */
    public void start(BundleContext context) throws Exception {
        super.start(context);
        plugin = this;

        ScriptRuntime.addInterpreterInstallChangedListener(this);
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
    public static SETLaunchingPlugin getDefault() {
        return plugin;
    }

    public static void log(IStatus status) {
        getDefault().getLog().log(status);
    }

    public void defaultInterpreterInstallChanged(IInterpreterInstall previous, IInterpreterInstall current) {
        // TODO Auto-generated method stub

    }

    public void interpreterAdded(IInterpreterInstall interpreter) {
        if (interpreter instanceof CoreSDKInstall) {
            IFileHandle handle = interpreter.getInstallLocation();
            if (!handle.exists()) {
                Path path = new Path(handle.toOSString());
                StringBuffer pathSB = new StringBuffer(path.toPortableString());
                String xml = ScriptRuntime.getPreferences().getString(ScriptRuntime.PREF_INTERPRETER_XML);
                String newValue = "";
                try {
                    newValue = VariablesPlugin.getDefault().getStringVariableManager().performStringSubstitution(
                            "${sdk_loc}", false);
                } catch (CoreException ce) {
                }
                if (newValue == null || newValue.equals("")) {
                    String envId = LocalEnvironment.ENVIRONMENT_ID;
                    xml = xml.replace("<interpreter environmentId=\"" + envId
                            + "\" id=\"defaultSausalitoCoreSDK\" name=\"Sausalito CoreSDK 1.0.8\" path=\""
                            + pathSB.toString() + "\"/>", "");

                    log(new Status(IStatus.WARNING, PLUGIN_ID, "Could not a valid Sausalito Core SDK installation."));
                }
                xml = xml.replace(pathSB, newValue);
                ScriptRuntime.getPreferences().setValue(ScriptRuntime.PREF_INTERPRETER_XML, xml);

                ScriptRuntime.savePreferences();
            }
        }
    }

    public void interpreterChanged(PropertyChangeEvent event) {
    }

    public void interpreterRemoved(IInterpreterInstall interpreter) {
    }

}