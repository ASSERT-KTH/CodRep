folder = project.findScriptFolder(project.getPath().append(packageRelativePath));

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

import java.io.File;
import java.net.URI;

import org.eclipse.core.resources.IContainer;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.Path;
import org.eclipse.dltk.core.DLTKCore;
import org.eclipse.dltk.core.IModelElement;
import org.eclipse.dltk.core.IScriptProject;
import org.eclipse.dltk.core.ISourceModule;
import org.eclipse.dltk.core.ModelException;

public class XQDTUriResolver implements IXQDTUriResolver {

    public URI resolveModuleImport(URI baseUri, String uri, String[] hints) {
        if (hints.length == 0) {
            return resolveUri(baseUri, uri);
        }
        for (int i = 0; i < hints.length; i++) {
            URI u = resolveUri(baseUri, hints[i]);
            if (u != null) {
                return u;
            }
        }
        return resolveUri(baseUri, uri);
    }

    public URI resolveUri(URI baseUri, String uriString) {
        try {
            return baseUri.resolve(uriString);
        } catch (IllegalArgumentException iae) {
            iae.printStackTrace();
        }
        return null;
    }

    public ISourceModule locateSourceModule(URI uri, IScriptProject project) {
        IPath projectLoc = project.getProject().getLocation();
        IPath path = new Path(uri.getPath());

        // only resolve file system locations that are located inside the project
        if (projectLoc.isPrefixOf(path)) {
            IPath packageAbolutePath = path.removeLastSegments(1);
            IPath packageRelativePath = packageAbolutePath.removeFirstSegments(projectLoc.segmentCount())
                    .makeRelative().setDevice(null);

            // check if there is a script folder for the given module URI
            IModelElement folder = null;
            if (packageRelativePath.segmentCount() == 0) {
                folder = project;
            } else {
                try {
                    folder = project.findScriptFolder(packageRelativePath.makeAbsolute());
                } catch (ModelException e) {
                    e.printStackTrace();
                }
            }
            if (folder != null) {
                // check if the file actually exists
                File f = new File(path.toOSString());
                if (f.exists()) {
                    return DLTKCore.createSourceModuleFrom(((IContainer)folder.getResource()).getFile(new Path(path
                            .lastSegment())));
                }
            }

        }

        return null;
    }
}