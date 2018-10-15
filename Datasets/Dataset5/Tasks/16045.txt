public static final String DEFAULT_DEPLOYMENT_SERVER = "http://portal.28msec.com/";

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
package org.eclipse.wst.xquery.set.launching.deploy;

import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.wst.xquery.set.core.SETProjectConfig;

public class DeployInfo {

    public static enum DeployType {
        DATA, PROJECT, PROJECT_AND_DATA
    }

    private IScriptProject fProject;
    private String fApplicationName;
    private String fUserName;
    private String fPassword;
    private DeployType fDeployType;
    private SETProjectConfig fConfig;
    private String fHost = DEFAULT_DEPLOYMENT_SERVER;

    public static final String DEFAULT_DEPLOYMENT_SERVER = "http://28msec.dyndns.org:8080/28msec";

    public DeployInfo(IScriptProject project, SETProjectConfig config, String appName, String username,
            String password, DeployType type, String host) {
        fProject = project;
        fConfig = config;
        fApplicationName = appName;
        fUserName = username;
        fPassword = password;
        fDeployType = type;
        if (host != null && !host.equals("")) {
            fHost = host;
        }
    }

    public IScriptProject getProject() {
        return fProject;
    }

    public SETProjectConfig getProjectConfig() {
        return fConfig;
    }

    public String getApplicationName() {
        return fApplicationName;
    }

    public String getUserName() {
        return fUserName;
    }

    public String getPassword() {
        return fPassword;
    }

    public DeployType getDeployType() {
        return fDeployType;
    }

    public String getHost() {
        return fHost;
    }

}
 No newline at end of file