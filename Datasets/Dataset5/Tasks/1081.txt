import org.eclipse.wst.xquery.core.XQDTUriResolver;

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
package org.eclipse.wst.xquery.set.internal.core;

import java.net.URI;

import org.eclipse.core.runtime.Path;
import org.eclipse.dltk.core.IExternalSourceModule;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.core.ISourceModule;
import org.eclipse.dltk.core.ModelException;
import org.eclipse.wst.xquery.internal.core.XQDTUriResolver;

public class SETResolver extends XQDTUriResolver {

    public ISourceModule locateSourceModule(URI uri, IScriptProject project) {
        String uriString = uri.toString();
        if (uriString.startsWith(ISETConstants.ZORBA_MODULE_PREFIX)) {
            try {
                String moduleName = new Path(uri.getPath()).lastSegment();
                IModelElement element = project.findElement(new Path(moduleName + ".xq"));
                if (element instanceof IExternalSourceModule) {
                    return (IExternalSourceModule)element;
                }
            } catch (ModelException e) {
                e.printStackTrace();
                return null;
            }
        } else if (uriString.startsWith(ISETConstants.SAUSALITO_MODULE_PREFIX)) {
            try {
                String moduleName = new Path(uri.getPath()).lastSegment() + ".xq";
                IModelElement element = project.findElement(new Path(moduleName));
                if (element instanceof IExternalSourceModule) {
                    return (IExternalSourceModule)element;
                }
            } catch (ModelException e) {
                e.printStackTrace();
            }
        }

        return super.locateSourceModule(uri, project);
    }
}
 No newline at end of file