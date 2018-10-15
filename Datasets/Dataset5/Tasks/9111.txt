private static final String BULKLOAD_PATH = "bulkload";

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
package org.eclipse.wst.xquery.set.internal.launching.jobs;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IResourceVisitor;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;

public class SETImportDataJob extends SETCoreSDKCommandJob {

    private static final String BULKLOAD_PATH = "test/data/bulkload";

    public SETImportDataJob(IProject project, OutputStream output) {
        super("Importing project data", project, output);
    }

    protected List<String> getCommandParameters() {
        List<String> params = new ArrayList<String>();
        params.add("import");
        params.add("data");
        params.add("-d");
        params.add(fProject.getLocation().toOSString());

        return params;
    }

    @Override
    protected int getJobTaskSize() {
        final IFolder folder = fProject.getFolder(BULKLOAD_PATH);
        if (!folder.exists()) {
            return 0;
        }

        final Set<String> names = new HashSet<String>();

        try {
            folder.accept(new IResourceVisitor() {
                public boolean visit(IResource resource) throws CoreException {
                    if (resource.getType() == IResource.FILE) {
                        IPath path = resource.getFullPath();
                        String ext = path.getFileExtension();
                        if (ext.equals("xq") || ext.equals("xml")) {
                            names.add(path.removeFileExtension().removeFirstSegments(4).toPortableString());
                        }
                        return false;
                    }
                    return true;
                }
            }, IResource.DEPTH_INFINITE, IResource.FILE);
        } catch (CoreException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        return names.size();
    }

    @Override
    protected String getJobTaskName() {
        return "Importing data for project: " + fProject.getName();
    }

    @Override
    protected void readCommandOutput(InputStream inputStream) throws IOException {
        OutputStream output = getOutputStream();

        BufferedReader ir = new BufferedReader(new InputStreamReader(inputStream));
        String line = null;
        while ((line = ir.readLine()) != null) {
            if (line.startsWith("Importing file ")) {
                updateMonitorTaskName(line);
            } else if (line.startsWith("  done") || line.startsWith("  failed")) {
                updateMonitorWork(1);
            }
            if (output != null) {
                output.write((line + "\n").getBytes());
            }
        }

    }

    protected boolean useConsole() {
        return true;
    }

}