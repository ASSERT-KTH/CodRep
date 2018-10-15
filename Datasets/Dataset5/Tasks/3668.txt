contextTypeRegistry.addContextType("org.eclipse.xpand.ui.editor.context.Default");

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

package org.eclipse.xpand.ui;

import java.io.IOException;
import java.util.List;

import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.text.templates.ContextTypeRegistry;
import org.eclipse.jface.text.templates.persistence.TemplateStore;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.editors.text.templates.ContributionContextTypeRegistry;
import org.eclipse.ui.editors.text.templates.ContributionTemplateStore;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.eclipse.xpand.ui.editor.PreferencesConstants;
import org.eclipse.xpand.ui.editor.color.ColorProvider;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xpand2.XpandExecutionContextImpl;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.MetamodelContributor;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.metamodel.MetamodelContributorRegistry;
import org.eclipse.xtend.typesystem.MetaModel;
import org.osgi.framework.BundleContext;

public class XpandEditorPlugin extends AbstractUIPlugin {
	// The shared instance.
	private static XpandEditorPlugin plugin;

	private ColorProvider colorProvider;

	private ContributionTemplateStore templateStore;

	private ContributionContextTypeRegistry contextTypeRegistry;

	public XpandEditorPlugin() {
		XpandEditorPlugin.plugin = this;
		colorProvider = new ColorProvider();
	}

	/**
	 * This method is called upon plug-in activation
	 */
	@Override
	public void start(final BundleContext context) throws Exception {
		super.start(context);
		Activator.getDefault();
		PreferencesConstants.initializeDefaultValues(getPreferenceStore());
	}

	/**
	 * This method is called when the plug-in is stopped
	 */
	@Override
	public void stop(final BundleContext context) throws Exception {
		super.stop(context);
		XpandEditorPlugin.plugin = null;
		colorProvider.dispose();
		colorProvider = null;
	}

	public static XpandEditorPlugin getDefault() {
		return XpandEditorPlugin.plugin;
	}

	public static ImageDescriptor getImageDescriptor(final String path) {
		return AbstractUIPlugin.imageDescriptorFromPlugin(getId(), path);
	}

	public static String getId() {
		return getDefault().getBundle().getSymbolicName();
	}

	public static ColorProvider getColorProvider() {
		return getDefault().colorProvider;
	}

	public static Shell getActiveWorkbenchShell() {
		final IWorkbenchWindow window = getActiveWorkbenchWindow();
		if (window != null) {
			return window.getShell();
		}
		return null;
	}

	private static IWorkbenchWindow getActiveWorkbenchWindow() {
		return getDefault().getWorkbench().getActiveWorkbenchWindow();
	}

	public static XpandExecutionContext getExecutionContext(final IJavaProject project) {
		final IXtendXpandProject xp = Activator.getExtXptModelManager().findProject(project.getPath());
		if (xp == null)
			return null;
		final XpandExecutionContextImpl ctx = new XpandPluginExecutionContext(xp);

		final List<? extends MetamodelContributor> contr = MetamodelContributorRegistry
				.getActiveMetamodelContributors(project);
		for (MetamodelContributor contributor : contr) {
			final MetaModel[] metamodels = contributor.getMetamodels(project, ctx);
			for (MetaModel element : metamodels) {
				ctx.registerMetaModel(element);
			}
		}
		return ctx;
	}

	public TemplateStore getTemplateStore() {
		if (templateStore == null) {
			templateStore = new ContributionTemplateStore(getContextTypeRegistry(), getDefault().getPreferenceStore(),
					"templates");
			try {
				templateStore.load();
			}
			catch (IOException e) {
				e.printStackTrace();
			}
		}

		return templateStore;
	}

	public ContextTypeRegistry getContextTypeRegistry() {
		if (contextTypeRegistry == null) {
			contextTypeRegistry = new ContributionContextTypeRegistry();
			contextTypeRegistry.addContextType("org.eclipse.internal.xtend.xpand2.editor.context.Default");
		}
		return contextTypeRegistry;
	}

}