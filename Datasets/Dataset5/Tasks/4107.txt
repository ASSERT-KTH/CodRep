package org.eclipse.jst.ws.jaxws.core.tests;

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.jaxws.core.tests;

import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IProjectDescription;
import org.eclipse.core.resources.IWorkspaceDescription;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;

/**
 * 
 * @author sclarke
 *
 */
public class TestProject {
    IProgressMonitor monitor = new NullProgressMonitor();

    private IProject testProject;
    
    public TestProject(String projectName) throws CoreException {
        IWorkspaceRoot workspaceRoot = ResourcesPlugin.getWorkspace().getRoot();
        testProject = workspaceRoot.getProject(projectName);
        testProject.create(monitor);
        testProject.open(monitor);
        
        IWorkspaceDescription description = ResourcesPlugin.getWorkspace().getDescription();
        description.setAutoBuilding(false);
        ResourcesPlugin.getWorkspace().setDescription(description);

    }
    
    public IProject getProject() {
        return testProject;
    }
    
    public void addProjectNature(IProject project, String nature) {
        try {
            IProjectDescription projectDescription = project.getDescription();
            String[] previousNatures = projectDescription.getNatureIds();
            String[] newNatures = new String[previousNatures.length + 1];
            System.arraycopy(previousNatures, 0, newNatures, 0, previousNatures.length);
            newNatures[previousNatures.length] = nature;
            projectDescription.setNatureIds(newNatures);
            project.setDescription(projectDescription, null);
        } catch (CoreException ce) {
            ce.printStackTrace();
        }
    }
    
    public void mkdirs(final IFolder folder) throws CoreException {
        if (!folder.exists()) {
            if (folder.getParent() instanceof IFolder) {
                mkdirs((IFolder) folder.getParent());
            }
            folder.create(true, true, null);
        }
    }
}