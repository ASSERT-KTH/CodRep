public final void testFindExtXptResourceInJar() throws JavaModelException {

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

package org.eclipse.xtend.shared.ui.test.xpand2.core;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

import org.eclipse.core.internal.utils.FileUtil;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.IXtendXpandResource;

public class Bug155018Test extends XpandCoreTestBase {

	/**
	 * Test for Bug#155018: The bug concerns loading resources from Jar files.
	 */
    public final void testFindOawResourceInJar() throws JavaModelException {
        env.openEmptyWorkspace();
        // create a test project and add a Jar file to its classpath. The Jar 'ExtensionInJar.jar' contains the 
        // extension 'org::openarchitectureware::util::IO.ext'
        final IProject proj = env.createProject("test-"+System.currentTimeMillis());
        env.addExternalJars(proj.getFullPath(), env.getJavaClassLibs());
        
        env.addInternalJar(proj.getFullPath(), "ExtensionInJar.jar", readJar(), false);
        env.fullBuild();
        IXtendXpandProject project = Activator.getExtXptModelManager().findProject(proj.getFullPath());
        assertNotNull(JavaCore.create(proj).findType("org.eclipse.xtend.expression.Analyzable"));
        IXtendXpandResource res = project.findExtXptResource("org::eclipse::xtend::util::stdlib::io","ext");
        assertNotNull(res);
        assertNotNull(res.getFullyQualifiedName());
        assertNotNull("AbstractExtension from Jar not found (Bug155018)", res);
    }

    /**
     * Retrieve the example Jar as byte array
     */
    @SuppressWarnings("restriction")
	private byte[] readJar () {
    	String path = "org/eclipse/xtend/shared/ui/test/xpand2/core/ExtensionInJar.jar";
        InputStream is =getClass().getClassLoader().getResourceAsStream(path);
        ByteArrayOutputStream os = new ByteArrayOutputStream();
        try {
			FileUtil.transferStreams(is, os, path, new NullProgressMonitor());
		} catch (CoreException e) {
			fail(e.getMessage());
		}
        assertNotNull(is);
        return os.toByteArray();
    }
}