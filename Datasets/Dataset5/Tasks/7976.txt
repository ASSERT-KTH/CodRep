final IPath pPath2 = env.addProject("test2-"+System.currentTimeMillis());

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
package org.eclipse.xtend.shared.ui.test.xpand2.emf;

import org.eclipse.core.runtime.IPath;
import org.eclipse.jdt.core.IClasspathEntry;
import org.eclipse.xtend.shared.ui.test.xpand2.core.XpandCoreTestBase;

public class EmfXpandTest extends XpandCoreTestBase {

	// An example meta model which we will extract in our project and use in our templates
	// It has one type "MetaType" with attribute "name:String"
	private final String ECORE_MMODEL = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			+ "<ecore:EPackage xmi:version=\"2.0\" "
			+ " xmlns:xmi=\"http://www.omg.org/XMI\" " +
					" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
			+

			" xmlns:ecore=\"http://www.eclipse.org/emf/2002/Ecore\" name=\"mm\" "
			+

			" nsURI=\"http://www.eclipse.org/mm/test/mm\" nsPrefix=\"mm\">"
			+ "<eClassifiers xsi:type=\"ecore:EClass\" name=\"MetaType\">"
			+ "<eStructuralFeatures xsi:type=\"ecore:EAttribute\" name=\"name\" eType=\"ecore:EDataType http://www.eclipse.org/emf/2002/Ecore#//EString\"/>"
			+ "</eClassifiers>" + "</ecore:EPackage>";

	/**
	 * This test uses an Xpand Template which uses an ECore Meta-Model not
	 * being registered as plugin but only part of the current classpath.
	 * The template should not have errors after the build
	 * @throws Exception
	 */
	public final void testECoreMetaModelOnSourceFolders() throws
Exception {
		env.openEmptyWorkspace();
		final IPath pPath = env.addProject("test-"+System.currentTimeMillis());
		// Clear classpath, we set it up on our own...
		env.setClasspath(pPath, new IClasspathEntry[0]);
		env.addExternalJars(pPath, env.getJavaClassLibs());
		final IPath templatesFolder = env.addPackage(pPath,
"templates");
		env.addFolderToSourceFolders(pPath, templatesFolder);
		IPath tpl = env
				.addFile(
						templatesFolder,
						"Template.xpt",
						tag("IMPORT mm")+"\n"+
						tag("DEFINE Root FOR MetaType")+"\n"+
						tag("ENDDEFINE"));

		env.fullBuild();
		assertTrue ("Errors expected during build as the metamodel is not on the claspath any more", env.getMarkersFor(tpl).length > 0);
		
		final IPath mmFolder = env.addFolder(pPath, "models");
		env.addFile(mmFolder,"mm.ecore",ECORE_MMODEL);
		IClasspathEntry sourceEntry = env.addFolderToSourceFolders(pPath, mmFolder);
		env.fullBuild();
		assertEquals ("No errors expected for dynamically loaded ECore Model", 0, env.getMarkersFor(tpl).length);
		
		env.removeClasspathEntry(pPath, sourceEntry);
		env.fullBuild();
		assertTrue ("Errors expected during build as the metamodel is not on the claspath any more", env.getMarkersFor(tpl).length > 0);
	}

	/**
	 * This test uses an Xpand Template which uses an ECore Meta-Model not
	 * being registered as plugin but only part of the current classpath.
	 * It is the same test as above, but after deleting the meta-model ecore file
	 * we should get errors in the template
	 * @throws Exception
	 */
	public final void testUseAfterDeleteECoreMetaModel() throws Exception {
		env.openEmptyWorkspace();
		final IPath pPath = env.addProject("test-"+System.currentTimeMillis());
		env.addExternalJars(pPath, env.getJavaClassLibs());
		env.removePackageFragmentRoot(pPath, "");
		final IPath root = env.addPackageFragmentRoot(pPath, "templates");
		final IPath pack = env.addPackage(root, "templates");
		IPath tpl = env.addFile(pack, "Template.xpt", tag("IMPORT mm") + "\n"
				+ tag("DEFINE Root FOR MetaType") + "\n" + tag("ENDDEFINE"));
		
		env.fullBuild();
		assertTrue(
				"Errors expected in the template as the metamodel does not exist",
				env.getMarkersFor(tpl).length > 0);
		
		IPath mmFile = env.addFile(pack, "mm.ecore", ECORE_MMODEL);
		env.fullBuild();
		assertEquals("No errors expected for dynamically loaded ECore Model",
				0, env.getMarkersFor(tpl).length);
		
		
		env.removeFile(mmFile);
		env.fullBuild();
		assertTrue(
				"Errors expected in the template as the metamodel is not existing any longer",
				env.getMarkersFor(tpl).length > 0);
	}

	/**
	 * This test uses an Xpand Template which uses an ECore Meta-Model not
	 * being registered as plugin but only part of the current classpath.
	 * It is the same test as above, but after deleting the meta-model
	 * ecore file
	 * we should get errors in the template
	 * @throws Exception
	 */
	public final void testUseAfterModifyECoreMetaModel() throws Exception {
		env.openEmptyWorkspace();
		final IPath pPath = env.addProject("test-"+System.currentTimeMillis());
		env.addExternalJars(pPath, env.getJavaClassLibs());
		env.removePackageFragmentRoot(pPath, "");
		final IPath root = env.addPackageFragmentRoot(pPath, "templates");
		final IPath pack = env.addPackage(root, "templates");
		IPath mmFile = env.addFile(pack, "mm.ecore", ECORE_MMODEL);
		IPath tpl = env.addFile(pack, "Template.xpt", tag("IMPORT mm") + "\n"
				+ tag("DEFINE Root FOR MetaType") + "\n" + tag("ENDDEFINE"));
		env.fullBuild();
		assertEquals("No errors expected for dynamically loaded ECore Model",
				0, env.getMarkersFor(tpl).length);
		env.removeFile(mmFile);
		env.removeFile(tpl);
		env.fullBuild();
		assertTrue("Empty project has no errors",
				env.getMarkersFor(tpl).length == 0);
		// Now re-create the Ecore file with a modified class
		mmFile = env.addFile(pack, "mm.ecore", ECORE_MMODEL.replaceAll(
				"MetaType", "MetaType2"));
		tpl = env.addFile(pack, "Template.xpt", tag("IMPORT mm") + "\n"
				+ tag("DEFINE Root FOR MetaType2") + "\n" + tag("ENDDEFINE"));
		env.fullBuild();
		assertEquals("No errors expected for dynamically loaded ECore Model",
				0, env.getMarkersFor(tpl).length);
	}

	/**
	 * This test uses an Xpand Template which uses an ECore Meta-Model 
	 * In the first part, a second project is on our classpath
	 * containing the ECore MM -> Result: We should see the MM
	 * In the second part, we remove the project -> Result: We should
	 * not see the MM
	 * @throws Exception
	 */
	public final void testECoreMetaModelInDifferentProject() throws Exception {
		env.openEmptyWorkspace();
		final IPath pPath = env.addProject("test-"+System.currentTimeMillis());
		final IPath pPath2 = env.addProject("test-"+System.currentTimeMillis());
		env.addExternalJars(pPath, env.getJavaClassLibs());
		env.addExternalJars(pPath2, env.getJavaClassLibs());
		final IPath templatesFolder = env.addPackage(pPath, "templates");
		final IPath mmFolder = env.addPackage(pPath2, "models");
		env.addFile(mmFolder, "mm.ecore", ECORE_MMODEL);
		IPath tpl = env.addFile(templatesFolder, "Template.xpt",
				tag("IMPORT mm") + "\n" + tag("DEFINE Root FOR MetaType")
						+ "\n" + tag("ENDDEFINE"));
		env.addRequiredProject(pPath, pPath2);
		env.fullBuild();
		assertEquals("No errors expected for referenced ECore MM", 0, env
				.getMarkersFor(tpl).length);

		env.removeRequiredProject(pPath, pPath2);
		env.fullBuild();
		assertTrue("Errors expected for non referenced ECore MM", env
				.getMarkersFor(tpl).length > 0);
	}

}