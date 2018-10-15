import org.eclipse.wst.xquery.core.facets.CheckedUriResolverFacetInstallActionDelegate;

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
package org.eclipse.wst.xquery.internal.launching.zorba;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.dltk.core.DLTKCore;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.launching.ScriptRuntime;
import org.eclipse.wst.xquery.internal.core.facets.CheckedUriResolverFacetInstallActionDelegate;

public class ZorbaUriResolverFacetInstallActionDelegate extends CheckedUriResolverFacetInstallActionDelegate {

    protected boolean checkFacetForProject(IProject project) {
        IScriptProject sProject = DLTKCore.create(project);

        try {
            IInterpreterInstall install = ScriptRuntime.getInterpreterInstall(sProject);
            if (!install.getInterpreterInstallType().getId().equals(ZorbaInstallType.INSTALL_TYPE_ID)) {
                return false;
            }
        } catch (CoreException e) {
            return false;
        }

        return true;
    }

    protected String getErrorMessage() {
        return "The Zorba URI Resolver facet can only be installed on projects having a Zorba interpreter type.";
    }

}