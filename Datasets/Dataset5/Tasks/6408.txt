Job job = new Job(Messages.Activator_AnalyzingProgress) {

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

package org.eclipse.xtend.shared.ui;

import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExtension;
import org.eclipse.core.runtime.IExtensionPoint;
import org.eclipse.core.runtime.IExtensionRegistry;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.internal.xtend.xtend.XtendFile;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.actions.WorkspaceModifyOperation;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.TypeSystemImpl;
import org.eclipse.xtend.shared.ui.core.IModelManager;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.builder.XtendXpandNature;
import org.eclipse.xtend.shared.ui.core.internal.XtendXpandModelManager;
import org.eclipse.xtend.shared.ui.core.metamodel.Contributor;
import org.eclipse.xtend.shared.ui.core.metamodel.MetamodelContributorRegistry;
import org.eclipse.xtend.shared.ui.expression.PluginExecutionContextImpl;
import org.eclipse.xtend.shared.ui.internal.XtendLog;
import org.eclipse.xtend.typesystem.MetaModel;
import org.osgi.framework.BundleContext;

/**
 * The main plugin class
 */
public class Activator extends AbstractUIPlugin {

	private static final String RESOURCE_CONTRIBUTOR_ID = "org.eclipse.xtend.shared.ui.resourceContributor";
	
	public static final String PLUGIN_ID = "org.eclipse.xtend.shared.ui"; 	

	public static final String getNatureId() {
		return XtendXpandNature.NATURE_ID;
	}

	// The shared instance.
	private static Activator plugin;

	private static HashMap<String, ResourceContributor> contributors;

	private IModelManager modelManager;

	/**
	 * The constructor.
	 */
	public Activator() {
		plugin = this;
		modelManager = new XtendXpandModelManager();
	}

	private final IPropertyChangeListener listener = new IPropertyChangeListener() {

		public void propertyChange(PropertyChangeEvent event) {
			Job job = new Job("Analyzing workspace...") {

				@Override
				protected IStatus run(IProgressMonitor monitor) {
					try {
						new WorkspaceModifyOperation() {
							@Override
							protected void execute(IProgressMonitor monitor) throws CoreException, java.lang.reflect.InvocationTargetException,
									InterruptedException {
								Activator.getExtXptModelManager().analyze(monitor);
							}
						}.run(monitor);
					} catch (InvocationTargetException e) {
						XtendLog.logError(e);
					} catch (InterruptedException e) {
						XtendLog.logError(e);
					}
					return Status.OK_STATUS;
				}

			};
			job.schedule();
		}
	};

	/**
	 * This method is called upon plug-in activation
	 */
	@Override
	public void start(final BundleContext context) throws Exception {
		super.start(context);
		getPreferenceStore().addPropertyChangeListener(listener);

		// initialize mm contributors
		Map<String, Contributor> registeredMetamodelContributors = MetamodelContributorRegistry.getRegisteredMetamodelContributors();
		for (Contributor c  : registeredMetamodelContributors.values()) {
			c.getMetaModelContributor();
		}
	}

	/**
	 * This method is called when the plug-in is stopped
	 */
	@Override
	public void stop(final BundleContext context) throws Exception {
		super.stop(context);
		getPreferenceStore().removePropertyChangeListener(listener);
		plugin = null;
	}

	/**
	 * Returns the shared instance.
	 */
	public static Activator getDefault() {
		return plugin;
	}

	/**
	 * Returns an image descriptor for the image file at the given plug-in
	 * relative path.
	 * 
	 * @param path
	 *            the path
	 * @return the image descriptor
	 */
	public static ImageDescriptor getImageDescriptor(final String path) {
		return AbstractUIPlugin.imageDescriptorFromPlugin(getId(), path);
	}

	/**
	 * Returns the standard display to be used. The method first checks, if the
	 * thread calling this method has an associated display. If so, this display
	 * is returned. Otherwise the method returns the default display.
	 */
	public static Display getStandardDisplay() {
		Display display = Display.getCurrent();
		if (display == null) {
			display = Display.getDefault();
		}
		return display;
	}

	public static String getId() {
		return getDefault().getBundle().getSymbolicName();
	}

	public static ResourceContributor[] getRegisteredResourceContributors() {
		final IExtensionRegistry registry = Platform.getExtensionRegistry();
		final IExtensionPoint point = registry.getExtensionPoint(Activator.RESOURCE_CONTRIBUTOR_ID);
		final Set<ResourceContributor> contrs = new HashSet<ResourceContributor>();
		if (point != null) {
			final IExtension[] extensions = point.getExtensions();
			for (int i = 0; i < extensions.length; i++) {
				final IExtension extension = extensions[i];
				final IConfigurationElement[] configs = extension.getConfigurationElements();
				for (int j = 0; j < configs.length; j++) {
					final IConfigurationElement element = configs[j];
					try {
						contrs.add((ResourceContributor) element.createExecutableExtension("class"));
					} catch (final CoreException e) {
						XtendLog.logError(e);
					}
				}
			}
		}
		return contrs.toArray(new ResourceContributor[contrs.size()]);
	}

	public static IModelManager getExtXptModelManager() {
		return getDefault().modelManager;
	}

	public static ExecutionContext getExecutionContext(final IJavaProject project) {
		final IXtendXpandProject xp = Activator.getExtXptModelManager().findProject(project.getPath());
		final ExecutionContextImpl ctx = new PluginExecutionContextImpl(xp, new TypeSystemImpl());

		final List<? extends MetamodelContributor> contr = MetamodelContributorRegistry.getActiveMetamodelContributors(project);
		for (MetamodelContributor contributor : contr) {
			final MetaModel[] metamodels = contributor.getMetamodels(project, ctx);
			for (int i = 0; i < metamodels.length; i++) {
				ctx.registerMetaModel(metamodels[i]);
			}
		}
		return ctx;
	}

	public final static boolean isXtendFile(final Object object) {
		if (object instanceof IFile)
			return XtendFile.FILE_EXTENSION.equals(((IFile) object).getFileExtension());
		return false;
	}

	public static ResourceContributor getRegisteredResourceContributorFor(String fileExtension) {
		if (contributors == null) {
			contributors = new HashMap<String, ResourceContributor>();
			for (ResourceContributor contr : getRegisteredResourceContributors()) {
				contributors.put(contr.getFileExtension(), contr);
			}
		}

		return contributors.get(fileExtension);
	}

	public static void logError(String string, Exception e) {
		getDefault().getLog().log(new Status(IStatus.ERROR,PLUGIN_ID, string,e));
		
	}
}