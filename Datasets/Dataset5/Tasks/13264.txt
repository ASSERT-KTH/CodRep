import org.eclipse.wst.xquery.core.codeassist.IImplicitImportActivator;

/*******************************************************************************
 * Copyright (c) 2009 Mark Logic Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Sam Neth (Mark Logic) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.launching.marklogic;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.dltk.launching.ScriptRuntime;
import org.eclipse.wst.xquery.internal.core.codeassist.IImplicitImportActivator;

public class MarkLogicCompletionPrefixActivator implements IImplicitImportActivator {

    /*
     * (non-Javadoc)
     * 
     * @see
     * org.eclipse.wst.xquery.internal.launching.marklogic.IImplicitImportActivator#activateForModule
     * (org.eclipse.dltk.core.ISourceModule)
     */
    public boolean activateForProject(IScriptProject project) {
        try {
            IInterpreterInstall install = ScriptRuntime.getInterpreterInstall(project);
            return install.getInterpreterInstallType().getId().equals(MarkLogicInstallType.INSTALL_TYPE_ID);
        } catch (CoreException e) {
        }

        return false;
    }
}