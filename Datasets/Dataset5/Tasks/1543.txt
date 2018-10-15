import org.eclipse.wst.xquery.set.launching.deploy.DeployInfo;

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
import java.util.HashSet;
import java.util.Set;

import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IResourceVisitor;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.wst.xquery.set.internal.launching.deploy.DeployInfo;

public class SETDeployDataJob extends SETCoreSDKDeployCommandJob {

    private static final String BULKLOAD_PATH = "test/data/bulkload";

    public SETDeployDataJob(DeployInfo info, OutputStream output) {
        super("Deploying project data", info, output);
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
                            names.add(path.removeFileExtension().lastSegment());
                        }
                        return false;
                    }
                    return true;
                }
            }, IResource.DEPTH_ONE, IResource.FILE);
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

    protected void readCommandOutput(InputStream inputStream) throws IOException {
        OutputStream output = getOutputStream();

        BufferedReader ir = new BufferedReader(new InputStreamReader(inputStream));
        String line = null;
        while ((line = ir.readLine()) != null) {
            if (line.startsWith("Deploying file ")) {
                updateMonitorTaskName(line);
            } else if (line.startsWith("  done") || line.startsWith("  failed")) {
                updateMonitorWork(1);
            }
            if (output != null) {
                output.write((line + "\n").getBytes());
            }
        }
    }

    protected DeployType getDeployType() {
        return DeployType.DEPLOY_DATA;
    }
}