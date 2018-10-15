package org.eclipse.wst.xquery.core.facets;

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
package org.eclipse.wst.xquery.internal.core.facets;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.ProjectScope;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.preferences.IEclipsePreferences;
import org.eclipse.wst.common.project.facet.core.IDelegate;
import org.eclipse.wst.common.project.facet.core.IProjectFacetVersion;
import org.osgi.service.prefs.BackingStoreException;
import org.eclipse.wst.xquery.core.IXQDTCorePreferences;
import org.eclipse.wst.xquery.core.XQDTCorePlugin;

public final class UriResolverFacetInstallActionDelegate implements IDelegate {

    final public void execute(IProject project, IProjectFacetVersion fv, Object config, IProgressMonitor monitor)
            throws CoreException {
        IEclipsePreferences preferences = new ProjectScope(project).getNode(XQDTCorePlugin.PLUGIN_ID);
        String resolverId = fv.getPluginId() + '.' + fv.getProjectFacet().getId();
        preferences.put(IXQDTCorePreferences.URI_RESOLVER_PREFERENCE_KEY, resolverId);
        try {
            preferences.flush();
        } catch (BackingStoreException bse) {
            throw new CoreException(new Status(IStatus.ERROR, XQDTCorePlugin.PLUGIN_ID, bse.getMessage(), bse));
        }
    }
}