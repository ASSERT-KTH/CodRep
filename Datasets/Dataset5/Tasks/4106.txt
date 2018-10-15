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
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.IClasspathEntry;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IPackageFragment;
import org.eclipse.jdt.core.IPackageFragmentRoot;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.launching.JavaRuntime;

/**
 * 
 * @author sclarke
 *
 */
public class TestJavaProject extends TestProject {
    private IJavaProject javaProject;
    
    public TestJavaProject(String projectName) throws CoreException {
        super(projectName);
        javaProject = JavaCore.create(getProject());
        addProjectNature(getProject(), JavaCore.NATURE_ID);
        
        javaProject.setRawClasspath(new IClasspathEntry[0], null);

        createSourceFolder();
        addToClasspath(javaProject, JavaRuntime.getDefaultJREContainerEntry());
        createOutputFolder();
    }
    
    public ICompilationUnit createCompilationUnit(String packageName, String name, String contents) throws JavaModelException {
        return getPackageFragment(packageName).createCompilationUnit(name, contents, false, monitor);
    }
    
    private IPackageFragment getPackageFragment(String packageName) throws JavaModelException {
        return getPackageFragmentRoot().createPackageFragment(packageName, true, monitor);
    }
    
    private IPackageFragmentRoot getPackageFragmentRoot() {
        return getJavaProject().getPackageFragmentRoot(getProject().getFolder("src"));     
    }
    
    private void createSourceFolder() throws CoreException {
        IFolder srcDir = getProject().getFolder("src");
        mkdirs(srcDir);    
        addToClasspath(javaProject, JavaCore.newSourceEntry(srcDir.getFullPath()));
    }

    private void createOutputFolder() throws CoreException {
        IFolder outputDir = getProject().getFolder("bin");
        mkdirs(outputDir);
        getJavaProject().setOutputLocation(outputDir.getFullPath(), monitor);
    }

    public IJavaProject getJavaProject() {
        return javaProject;
    }
    
    public void addToClasspath(IJavaProject javaProject, IClasspathEntry classpathEntry) {
        try {
            IClasspathEntry[] currentClasspathEntries = javaProject.getRawClasspath();
            IClasspathEntry[] newClasspathEntries = new IClasspathEntry[currentClasspathEntries.length + 1];
            System.arraycopy(currentClasspathEntries, 0, newClasspathEntries, 0, 
                    currentClasspathEntries.length);
            newClasspathEntries[currentClasspathEntries.length] = classpathEntry;
            javaProject.setRawClasspath(newClasspathEntries, new NullProgressMonitor());
        } catch (JavaModelException jme) {
            jme.printStackTrace();
        }
    }

}