if (!overwrite && packages.containsKey(pack.getNsURI())) {//packageRegistry.containsKey(pack.getNsURI())) {

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
package org.eclipse.xtend.typesystem.emf.ui;

import java.io.IOException;
import java.util.Collection;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IResourceVisitor;
import org.eclipse.core.resources.IStorage;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EcorePackage;
import org.eclipse.emf.ecore.EPackage.Registry;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.ResourceSet;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.emf.ecore.util.EcoreUtil;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IPackageFragmentRoot;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.internal.core.ExternalPackageFragmentRoot;
import org.eclipse.jdt.internal.core.JarPackageFragmentRoot;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.core.internal.JDTUtil;
import org.eclipse.xtend.shared.ui.core.internal.ResourceID;
import org.eclipse.xtend.typesystem.emf.ui.internal.EmfToolsLog;

/**
 * Analyzes a project's classpath for ecore metamodels. We need to take care of Ecore files
 * <ul>
 * <li>directly contained in the classpath</li>
 * <li>in JARs within the classpath</li>
 * <li>in the classpath of projects referenced by this project (recursively)</li>
 * <li>in plugins referenced by the project, either within the target platform or as referenced plugin projects
 * (recursively)</li>
 * </ul>
 * <p>
 * Reading Ecore files occurs in background Jobs. Each Job uses its own ResourceSet. This avoids concurrency issues.
 * </p>
 */
final class ProjectAnalyzer extends Job {
	private final IJavaProject project;
	private ResourceSet rs;
	private Map<IStorage, Resource> mapping;
	private Map<String, EPackage> packages;

	public ProjectAnalyzer(final IJavaProject project) {
		super("Analyzing accessible EMF metamodels for project " + project.getProject().getProject().getName());
		// see bug https://bugs.eclipse.org/bugs/show_bug.cgi?id=268516
		setRule(ResourcesPlugin.getWorkspace().getRoot());
		this.project = project;
	}

	@Override
	protected IStatus run(final IProgressMonitor monitor) {
		if (EmfToolsPlugin.trace) {
			System.out.println("Analyzing EMF metamodels for project " + project.getProject().getProject().getName());
		}

		// load models
		rs = new ResourceSetImpl();
		mapping = new HashMap<IStorage, Resource>();
		packages = new HashMap<String, EPackage>();
		loadMetamodelsForProject(project, rs, monitor);
		
		// always add ecore
		packages.put(EcorePackage.eNS_URI, EcorePackage.eINSTANCE);

		// done. now trigger build for the project.
		// only do this if it is an Xpand project
		// do not build referencing projects. the EmfToolsPlugin will take care
		// of this
		if (Activator.getExtXptModelManager().findProject(project.getProject()) != null) {
			new BuildJob(project.getProject()).schedule();
		}

		return Status.OK_STATUS;
	}

	@SuppressWarnings("restriction")
	private void loadMetamodelsForProject(final IJavaProject javaProject, final ResourceSet rs,
			final IProgressMonitor monitor) {
		try {
			final String ext = "ecore";
			for (final IPackageFragmentRoot root : javaProject.getPackageFragmentRoots()) {
				if (!root.isArchive()) {
					IResource rootResource = null;
					if (root instanceof ExternalPackageFragmentRoot) {
						rootResource = ((ExternalPackageFragmentRoot) root).resource();
					}
					else {
						rootResource = root.getUnderlyingResource();
					}
					if (rootResource != null) {
						try {
							rootResource.accept(new IResourceVisitor() {
								public boolean visit(final IResource resource) throws CoreException {
									if (resource instanceof IFile && ext.equals(((IFile) resource).getFileExtension())) {
										loadModelFromStorage(rs, (IFile) resource);
									}
									return true;
								}
							});
						}
						catch (final CoreException e) {
							EmfToolsLog.logError(e);
						}
					}
				}
				else {
					// skip JRE jars
					if (((JarPackageFragmentRoot) root).getPath().toString().contains("jre/lib")) {
						if (EmfToolsPlugin.trace) {
							System.out.println("Skipping " + ((JarPackageFragmentRoot) root).getPath().toString());
						}
						continue;
					}

					root.open(monitor);
					try {
						final ZipFile zip = ((JarPackageFragmentRoot) root).getJar();

						final Enumeration<? extends ZipEntry> entries = zip.entries();
						while (entries.hasMoreElements()) {
							final ZipEntry entry = entries.nextElement();
							final String name = entry.getName();
							if (name.endsWith(ext)) {
								final String fqn = name.substring(0, name.length() - ext.length() - 1).replaceAll("/",
										"::");
								final ResourceID resourceID = new ResourceID(fqn, ext);
								final IStorage findStorage = JDTUtil.loadFromJar(resourceID, root);
								if (findStorage != null) {
									loadModelFromStorage(rs, findStorage);
								}
							}
						}
					}
					catch (final CoreException e) {
						EmfToolsLog.logError(e);
					}
					finally {
						root.close();
					}
				}
			}
		}
		catch (final JavaModelException e) {
			EmfToolsLog.logError(e);
		}
	}

	private void loadModelFromStorage(final ResourceSet rs, final IStorage storage) {
		final URI uri = URI.createPlatformResourceURI(storage.getFullPath().toString(), true);
		if (EmfToolsPlugin.trace) {
			System.out.println("Loading EMF metamodel " + storage.getFullPath().toString());
		}

		final Resource r = rs.createResource(uri);
		if (r.isLoaded() && !r.isModified())
			return;
		try {
			r.load(storage.getContents(), Collections.EMPTY_MAP);
			mapping.put(storage, r);
			registerEPackages(rs, r, false);
		}
		catch (final IOException e) {
			EmfToolsLog.logError(e);
		}
		catch (final CoreException e) {
			EmfToolsLog.logError(e);
		}
	}

	private void registerEPackages(final ResourceSet rs, final Resource r, boolean overwrite) {
		final Collection<EPackage> packages = EcoreUtil.getObjectsByType(r.getContents(),
				EcorePackage.Literals.EPACKAGE);
		for (final EPackage pack : packages) {
			registerPackage(pack, rs, overwrite);
		}
	}

	private void registerPackage(final EPackage pack, ResourceSet rs, boolean overwrite) {
		Registry packageRegistry = rs.getPackageRegistry();
		// finding duplicates by nsURI is better than by name since package
		// names may be used across MMs
		if (!overwrite && packageRegistry.containsKey(pack.getNsURI())) {
			if (EmfToolsPlugin.trace) {
				System.out.println("Did not register '" + pack.getName() //+ "' from " + storage.getFullPath()
						+ " because an EPackage with the same nsURI has already been registered.");
			}
		}
		else {
			packageRegistry.put(pack.getNsURI(), pack);
			packages.put(pack.getNsURI(), pack);
		}
		// recurse into subpackages
		for (final EPackage p : pack.getESubpackages()) {
			registerPackage(p, rs, overwrite);
		}
	}

	public Map<String, EPackage> getNamedEPackageMap() {
		if (packages == null) {
			run(new NullProgressMonitor());
		}
		return Collections.unmodifiableMap(packages);
	}
}
 No newline at end of file