return projects.get(ele);

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xtend.shared.ui.core.internal;

import java.util.Iterator;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IStorage;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.internal.xtend.util.Cache;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.Messages;
import org.eclipse.xtend.shared.ui.core.IModelManager;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.IXtendXpandResource;
import org.eclipse.xtend.shared.ui.core.builder.XtendXpandNature;
import org.eclipse.xtend.shared.ui.internal.XtendLog;

public class XtendXpandModelManager implements IModelManager {

    public XtendXpandModelManager() {

    }

    public final Cache<IJavaProject, XtendXpandProject> projects = new Cache<IJavaProject, XtendXpandProject>() {
        @Override
        protected XtendXpandProject createNew(IJavaProject ele) {
            return new XtendXpandProject(ele);
        }
    };

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.internal.xtend.core.IXpandModelManager#findProject(org.eclipse.core.runtime.IPath)
     */
    public IXtendXpandProject findProject(final IPath path) {
        return findProject(ResourcesPlugin.getWorkspace().getRoot().findMember(path));
    }

    public IXtendXpandProject findProject(final IResource res) {
        if (res == null)
            return null;
        final IJavaProject ele = JavaCore.create(res.getProject());
        try {
            if (ele != null && res.getProject().isAccessible() && res.getProject().isNatureEnabled(XtendXpandNature.NATURE_ID))
                return (IXtendXpandProject) projects.get(ele);
        } catch (final CoreException e) {
            XtendLog.logError(e);
        }
        return null;
    }

    public void analyze(final IProgressMonitor monitor) {
        monitor.beginTask(Messages.XtendXpandModelManager_AnalyzingPrompt, computeAmoutOfWork());
        for (final Iterator<?> iter = projects.getValues().iterator(); iter.hasNext();) {
            if (monitor.isCanceled())
                return;
            IXtendXpandProject project = (IXtendXpandProject) iter.next();
			project.analyze(monitor, Activator.getExecutionContext(project.getProject()));
        }
        monitor.done();
    }

    /**
     * Computes the amount of work that has to be done during a build.
     * @return the number of resources registered within all Xtend projects.
     */
    private int computeAmoutOfWork() {
        int i = 0;
        for (final Iterator<?> iter = projects.getValues().iterator(); iter.hasNext();) {
            final IXtendXpandProject element = (IXtendXpandProject) iter.next();
            i += element.getRegisteredResources().length;
        }
        return i;
    }

    /**
     * Tries to locate an Xtend resource by its underlying file.
     * @param underlying IStorage
     */
    public IXtendXpandResource findExtXptResource(IStorage file) {
    	// it can be that the resource is located within a jar, than scan the projects for the resource
    	if (!(file instanceof IFile)) {
    		for (Iterator<?> it=projects.getValues().iterator(); it.hasNext(); ) {
    			IXtendXpandProject p = (IXtendXpandProject) it.next();
    			IXtendXpandResource res = p.findXtendXpandResource(file);
    			if (res!=null) {
    				return res;
    			}
    		}
    	} else {
	        final IXtendXpandProject project = findProject((IFile)file);
	        if (project != null) {
	            return project.findXtendXpandResource(file);
	        }
        }
        return null;
    }

	public IXtendXpandResource findXtendXpandResource(String oawNamespace, String extension) {
		for (IXtendXpandProject p : projects.getValues()) {
			IXtendXpandResource res = p.findExtXptResource(oawNamespace, extension);
			if (res!=null)
				return res;
		}
		return null;
	}

}