if (importedResource!=null && importedResource.equals(res)){

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

package org.eclipse.xtend.shared.ui.core.builder;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IResourceDelta;
import org.eclipse.core.resources.IResourceDeltaVisitor;
import org.eclipse.core.resources.IResourceVisitor;
import org.eclipse.core.resources.IStorage;
import org.eclipse.core.resources.IncrementalProjectBuilder;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.internal.xtend.xtend.XtendFile;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.IPackageFragmentRoot;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.internal.core.JarPackageFragmentRoot;
import org.eclipse.ui.preferences.ScopedPreferenceStore;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.ResourceContributor;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.IXtendXpandResource;
import org.eclipse.xtend.shared.ui.core.internal.BuildState;
import org.eclipse.xtend.shared.ui.core.internal.JDTUtil;
import org.eclipse.xtend.shared.ui.core.internal.ResourceID;
import org.eclipse.xtend.shared.ui.core.preferences.PreferenceConstants;
import org.eclipse.xtend.shared.ui.internal.XtendLog;

@SuppressWarnings("restriction")
public class XtendXpandBuilder extends IncrementalProjectBuilder {

	class XtendXpandDeltaVisitor implements IResourceDeltaVisitor, IResourceVisitor {
		private final IProgressMonitor monitor;
		private final Set<String> extensions;

		public XtendXpandDeltaVisitor(final IProgressMonitor monitor) {
			this.monitor = monitor;
			extensions = new HashSet<String>();
			final ResourceContributor[] contributors = Activator.getRegisteredResourceContributors();
			for (final ResourceContributor resourceContributor : contributors) {
				extensions.add(resourceContributor.getFileExtension());
			}
		}

		/*
		 * (non-Javadoc)
		 *
		 * @see
		 * org.eclipse.core.resources.IResourceDeltaVisitor#visit(org.eclipse
		 * .core.resources.IResourceDelta)
		 */
		public boolean visit(final IResourceDelta delta) throws CoreException {
			final IResource resource = delta.getResource();
			if (isXtendXpandResource(resource)) {
				switch (delta.getKind()) {
					case IResourceDelta.ADDED:
						// handle added resource
//						XtendXpandMarkerManager.deleteMarkers(resource);
						reloadResource((IFile) resource);
						break;
					case IResourceDelta.REMOVED:
						// handle removed resource
						handleRemovement((IFile) resource);
						break;
					case IResourceDelta.CHANGED:
						// handle changed resource
						reloadResource((IFile) resource);
						break;
				}
			}
			monitor.worked(1);
			return true;
		}

		private boolean isXtendXpandResource(final IResource resource) {
			return resource instanceof IFile && extensions.contains(((IFile) resource).getFileExtension())
					&& isOnJavaClassPath(resource);
		}

		public boolean visit(final IResource resource) {
			if (isXtendXpandResource(resource)) {
				reloadResource((IFile) resource);
			}
			monitor.worked(1);
			return true;
		}

	}

	private int incrementalAnalyzerStrategy;

	private void updateIncrementalAnalyzerStrategy() {
		final ScopedPreferenceStore scopedPreferenceStore = new ScopedPreferenceStore(new InstanceScope(), Activator
				.getId());
		incrementalAnalyzerStrategy = scopedPreferenceStore.getInt(PreferenceConstants.INCREMENTAL_ANALYZER_STRATEGY);
	}

	private boolean analyzeDependentProjectsWhenIncremental() {
		return incrementalAnalyzerStrategy == PreferenceConstants.INCREMENTAL_ANALYZER_STRATEGY_PROJECT_AND_DEPENDENT;
	}

	private boolean analyseReverseReferencedResources(){
		return incrementalAnalyzerStrategy == PreferenceConstants.INCREMENTAL_ANALYZER_STRATEGY_FILE_ONLY_WITH_REVERSE_REFERENCE;
	}

	private boolean analyzeWholeProjectWhenIncremental() {
		switch(incrementalAnalyzerStrategy) {
			case PreferenceConstants.INCREMENTAL_ANALYZER_STRATEGY_PROJECT:
			case PreferenceConstants.INCREMENTAL_ANALYZER_STRATEGY_PROJECT_AND_DEPENDENT:
				return true;
			default:
				return false;
		}
	}

	boolean isOnJavaClassPath(final IResource resource) {
		final IJavaProject jp = JavaCore.create(resource.getProject());
		if (jp != null)
			return jp.isOnClasspath(resource);
		return false;
	}

	public static final String getBUILDER_ID() {
		return Activator.getId() + ".xtendBuilder";
	}

	private Set<IXtendXpandResource> toAnalyze = null;

	/*
	 * (non-Javadoc)
	 *
	 * @see org.eclipse.core.internal.events.InternalBuilder#build(int,
	 * java.util.Map, org.eclipse.core.runtime.IProgressMonitor)
	 */
	@SuppressWarnings("unchecked")
	@Override
	protected IProject[] build(final int kind, final Map args, final IProgressMonitor monitor) throws CoreException {
		toAnalyze = new HashSet<IXtendXpandResource>();
		try {
			if (kind == FULL_BUILD) {
				fullBuild(monitor);
			}
			else {
				final IResourceDelta delta = getDelta(getProject());
				if (delta == null) {
					fullBuild(monitor);
				}
				else {
					incrementalBuild(delta, monitor);
				}
			}
		}
		catch (final Throwable e) {
			e.printStackTrace();
		}


		updateIncrementalAnalyzerStrategy();
		Map<IXtendXpandProject, ExecutionContext> projects = new HashMap<IXtendXpandProject, ExecutionContext>();
		if (analyseReverseReferencedResources()&& kind!=CLEAN_BUILD && kind!=FULL_BUILD){
			fillToAnalyseWithReverseReferencedResources();
		}
		for (final Object name : toAnalyze) {
			if(monitor.isCanceled())
				break;

			final IXtendXpandResource res = (IXtendXpandResource) name;
			final IResource resource = (IResource) res.getUnderlyingStorage();
			final IProject project = resource.getProject();

			if (!project.isLinked()) {
				final IXtendXpandProject xtdxptProject = Activator.getExtXptModelManager().findProject(project);

				if(xtdxptProject!=null && (kind==CLEAN_BUILD || kind==FULL_BUILD ||analyzeWholeProjectWhenIncremental()))
					addProject(projects, xtdxptProject);
				else {
					final ExecutionContext execCtx = Activator.getExecutionContext(JavaCore.create(project));
					BuildState.set(execCtx);
					try {
						res.analyze(execCtx);
					} finally {
						BuildState.remove(execCtx);
					}
				}

				monitor.worked(1);
			}
		}

		for (Entry<IXtendXpandProject, ExecutionContext> e : projects.entrySet()) {
			BuildState.set(e.getValue());
			try {
				e.getKey().analyze(monitor, e.getValue());
			} finally {
				BuildState.remove(e.getValue());
			}
		}
		XtendXpandMarkerManager.finishBuild();
		return null;
	}

	private void fillToAnalyseWithReverseReferencedResources() {
		Set<IXtendXpandResource> reverseReferences = new HashSet<IXtendXpandResource>();
		for (final Object name : toAnalyze) {
			final IXtendXpandResource res = (IXtendXpandResource) name;
			final IResource resource = (IResource) res.getUnderlyingStorage();
			final IProject project = resource.getProject();
			if (!project.isLinked()) {
				final IXtendXpandProject xtdxptProject = Activator.getExtXptModelManager().findProject(project);
				IXtendXpandResource[] resources = xtdxptProject.getAllRegisteredResources();
				for (IXtendXpandResource iXtendXpandResource : resources) {
					if (iXtendXpandResource != null) {
						for (String string : iXtendXpandResource.getImportedExtensions()) {
							IXtendXpandResource importedResource = xtdxptProject.findExtXptResource(string, XtendFile.FILE_EXTENSION);
							if (importedResource.equals(res)){
								reverseReferences.add(iXtendXpandResource);
								break;
							}
						}
					}
				}
			}
		}
		toAnalyze.addAll(reverseReferences);
	}

	private void addProject(final Map<IXtendXpandProject, ExecutionContext> projects, final IXtendXpandProject xtdxptProject) {
		if(projects.containsKey(xtdxptProject))
			return;

		projects.put(xtdxptProject, Activator.getExecutionContext(xtdxptProject.getProject()));

		if(analyzeDependentProjectsWhenIncremental()) {
			for(IXtendXpandProject dependent: getDependentProjects(xtdxptProject))
				if(!projects.containsKey(dependent))
					addProject(projects, dependent);
		}

	}

	private Collection<IXtendXpandProject> getDependentProjects(IXtendXpandProject xtdxptProject) {
		Collection<IXtendXpandProject> result = new ArrayList<IXtendXpandProject>();

		for (IProject project : ResourcesPlugin.getWorkspace().getRoot().getProjects()) {
			IXtendXpandProject p = Activator.getExtXptModelManager().findProject(project);
			if(p!=null && Arrays.asList(p.getReferencedProjects()).contains(xtdxptProject)) {
				result.add(p);
			}
		}

		return result;
	}

	void reloadResource(final IFile resource) {
		if (resource.exists()) {
			final IXtendXpandProject project = Activator.getExtXptModelManager().findProject(resource);
			if (project != null) {
				final IXtendXpandResource r = project.findXtendXpandResource(resource);
				if (r != null) {
					if (r.refresh()) {
						resource.getLocalTimeStamp();
					}
					toAnalyze.add(r);
				}
			}
		}
	}

	public void handleRemovement(final IFile resource) {
		final IXtendXpandProject project = Activator.getExtXptModelManager().findProject(resource);
		if (project != null) {
			project.unregisterXtendXpandResource(project.findXtendXpandResource(resource));
		}
		else {
			XtendLog.logInfo("No Xpand project found for " + resource.getProject().getName());
		}
	}

	protected void fullBuild(final IProgressMonitor monitor) throws CoreException {
		final IXtendXpandProject project = Activator.getExtXptModelManager().findProject(getProject().getFullPath());
		if (project != null) {
			getProject().accept(new XtendXpandDeltaVisitor(monitor));
			final IJavaProject jp = JavaCore.create(getProject());
			final IPackageFragmentRoot[] roots = jp.getPackageFragmentRoots();
			final Set<String> extensions = new HashSet<String>();
			final ResourceContributor[] contributors = Activator.getRegisteredResourceContributors();
			for (final ResourceContributor resourceContributor : contributors) {
				extensions.add(resourceContributor.getFileExtension());
			}
			for (final IPackageFragmentRoot root : roots) {
				if (root.isArchive()) {
					try {
						root.open(monitor);
						try {
							final ZipFile zip = ((JarPackageFragmentRoot) root).getJar();
							final Enumeration<? extends ZipEntry> entries = zip.entries();
							while (entries.hasMoreElements()) {
								final ZipEntry entry = entries.nextElement();
								for (final String ext : extensions) {
									final String name = entry.getName();
									if (name.endsWith(ext)) {
										final String fqn = name.substring(0, name.length() - ext.length() - 1).replaceAll(
												"/", "::");
										final ResourceID resourceID = new ResourceID(fqn, ext);
										final IStorage findStorage = JDTUtil.loadFromJar(resourceID, root);
										project.findXtendXpandResource(findStorage);
									}
								}
							}
						}
						finally {
							root.close();
						}
					} catch( CoreException ex) {
						XtendLog.logError(ex);
					}
				}
			}
		}
		else {
			XtendLog.logInfo("Couldn't create Xpand project for project " + getProject().getName());
		}
	}

	protected void incrementalBuild(final IResourceDelta delta, final IProgressMonitor monitor) throws CoreException {
		final XtendXpandDeltaVisitor visitor = new XtendXpandDeltaVisitor(monitor);
		delta.accept(visitor);
	}
}