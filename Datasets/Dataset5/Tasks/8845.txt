possiblePath = new Path("C:\\Program Files\\Sausalito CoreSDK 1.0.12");

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
package org.eclipse.wst.xquery.set.internal.launching.variables;

import java.io.File;
import java.io.IOException;
import java.net.URL;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.FileLocator;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.variables.IDynamicVariable;
import org.eclipse.core.variables.IDynamicVariableResolver;
import org.eclipse.wst.xquery.launching.XQDTLaunchingPlugin;
import org.eclipse.wst.xquery.set.launching.SETLaunchingPlugin;
import org.osgi.framework.Bundle;

public class CoreSdkLocationResolver implements IDynamicVariableResolver {

    public String resolveValue(IDynamicVariable variable, String argument) throws CoreException {
        String result = findStrategies();

        return result;
    }

    private String findStrategies() {
        String result = null;

        // I. first search for the shipped Sausalito CoreSDK
        // this case happens in the 28msec distribution of the plugins
        result = findShippedCoreSDK();
        if (result != null) {
            return result;
        }

        // II. if no CoreSDK is shipped (for some platforms)
        // go and search in some predefined install locations
        result = findInstalledCoreSDK();
        if (result != null) {
            return result;
        }

        return result;
    }

    private String findShippedCoreSDK() {
        String os = Platform.getOS();

        String osPart = "." + os;
        String archPart = "";

        // in case of non-Windows platforms we make have more versions of the CoreSDK
        if (!os.equals(Platform.OS_WIN32)) {
            archPart = "." + Platform.getOSArch();
        }

        String pluginID = "com.28msec.sausalito";
        String fragment = pluginID + osPart + archPart;

        Bundle[] bundles = Platform.getBundles(fragment, null);
        if (bundles == null || bundles.length == 0) {
            if (XQDTLaunchingPlugin.DEBUG_AUTOMATIC_PROCESSOR_DETECTION) {
                log(IStatus.INFO, "Could not find plug-in fragment: " + fragment
                        + ". No default Sausalito CoreSDK will be configured.", null);
            }
            return null;
        }
        if (XQDTLaunchingPlugin.DEBUG_AUTOMATIC_PROCESSOR_DETECTION) {
            log(IStatus.INFO, "Found Sausalito CoreSDK plug-in fragment: " + fragment, null);
        }

        Bundle bundle = bundles[0];
        URL coreSdkUrl = FileLocator.find(bundle, new Path("coresdk"), null);
        if (coreSdkUrl == null) {
            return null;
        }
        try {
            coreSdkUrl = FileLocator.toFileURL(coreSdkUrl);
        } catch (IOException ioe) {
            log(IStatus.ERROR, "Cound not retrieve the Eclipse bundle location: " + fragment, ioe);
            return null;
        }

        IPath coreSdkPath = new Path(coreSdkUrl.getPath());

        return locateScriptIn(coreSdkPath);
    }

    private String findInstalledCoreSDK() {
        String os = Platform.getOS();
        Path possiblePath = null;

        if (os.equals(Platform.OS_WIN32)) {
            possiblePath = new Path("C:\\Program Files\\Sausalito CoreSDK 1.0.0");
        } else {
            possiblePath = new Path("/opt/sausalito");
        }

        return locateScriptIn(possiblePath);
    }

    private String locateScriptIn(IPath coreSdkPath) {
        if (coreSdkPath == null) {
            NullPointerException npe = new NullPointerException();
            log(IStatus.ERROR, "Could not locate the Sausalito script.", npe);
            return null;
        }

        IPath scriptPath = coreSdkPath.append("bin").append("sausalito");
        if (Platform.getOS().equals(Platform.OS_WIN32)) {
            scriptPath = scriptPath.addFileExtension("bat");
        }

        File scrptFile = scriptPath.toFile();
        if (!scrptFile.exists()) {
            log(IStatus.ERROR, "Could not find the Sausalito script at location: " + coreSdkPath.toOSString(), null);
            return null;
        }

        return scriptPath.toOSString();
    }

    public static IStatus log(int severity, String message, Throwable t) {
        Status status = new Status(severity, SETLaunchingPlugin.PLUGIN_ID, message, t);
        SETLaunchingPlugin.log(status);
        return status;
    }

}