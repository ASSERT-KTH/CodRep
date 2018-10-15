import org.eclipse.wst.xquery.launching.XQDTInterpreterInstallType;

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

import org.eclipse.dltk.core.environment.EnvironmentManager;
import org.eclipse.dltk.core.environment.IEnvironment;
import org.eclipse.dltk.launching.IInterpreterInstall;
import org.eclipse.wst.xquery.internal.launching.XQDTInterpreterInstallType;

public class ZorbaInstallType extends XQDTInterpreterInstallType {

    public static final String INSTALL_TYPE_ID = "org.eclipse.wst.xquery.launching.ZorbaInstallType"; //$NON-NLS-1$
    private static final String INSTALL_TYPE_NAME = "Zorba XQuery Engine"; //$NON-NLS-1$

    public String getName() {
        return INSTALL_TYPE_NAME;
    }

    @Override
    protected String[] getPossibleInterpreterNames() {
        return new String[] { "zorba" };
    }

    protected IInterpreterInstall doCreateInterpreterInstall(String id) {
        return new ZorbaInstall(this, id);
    }

    @Override
    public IEnvironment getEnvironment() {
        return EnvironmentManager.getLocalEnvironment();
    }

    @Override
    public String getResolverFacetId() {
        return IZorbaConstants.ZORBA_RESOLVER_FACET_ID;
    }

    // @Override
    // protected String[] buildCommandLine(IFileHandle installLocation, IFileHandle pathFile) {
    // String interpreterPath = installLocation.getCanonicalPath();
    // String scriptPath = pathFile.getCanonicalPath();
    // return new String[] { interpreterPath, "--omit-xml-declaration", "-f", "-q", scriptPath };
    // }

}
 No newline at end of file