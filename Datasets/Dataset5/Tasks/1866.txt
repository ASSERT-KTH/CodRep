null, null, null, null);

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

import java.util.HashMap;
import java.util.Map;

import org.eclipse.emf.mwe.core.monitor.ProgressMonitor;
import org.eclipse.internal.xpand2.pr.ProtectedRegionResolver;
import org.eclipse.xpand2.output.Output;
import org.eclipse.xtend.expression.Resource;
import org.eclipse.xtend.expression.ResourceManager;
import org.eclipse.xtend.expression.ResourceParser;
import org.eclipse.xtend.expression.TypeSystemImpl;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;

public class XpandPluginExecutionContext extends org.eclipse.xpand2.XpandExecutionContextImpl {
	private final IXtendXpandProject project;

	public XpandPluginExecutionContext(final IXtendXpandProject xp) {
		this(new PluginResourceManager(xp), null, new TypeSystemImpl(), new HashMap<String, Variable>(),
				new HashMap<String, Variable>(), null, null, null, xp);
	}

	protected XpandPluginExecutionContext(ResourceManager resourceManager, Resource currentResource,
			TypeSystemImpl typeSystem, Map<String, Variable> vars, Map<String, Variable> globalVars, Output output,
			ProtectedRegionResolver prs, ProgressMonitor monitor, IXtendXpandProject xp) {
		super(resourceManager, currentResource, typeSystem, vars, globalVars, output, prs, monitor, null, null, null,
				null, null, null);
		this.project = xp;
	}

	@Override
	public XpandPluginExecutionContext cloneContext() {
		return new XpandPluginExecutionContext(resourceManager, currentResource(), typeSystem, getVisibleVariables(),
				getGlobalVariables(), output, protectedRegionResolver, getMonitor(), project);
	}

	public static class PluginResourceManager implements ResourceManager {
		private IXtendXpandProject project;

		public PluginResourceManager(final IXtendXpandProject project) {
            assert project!=null;
			this.project = project;
		}

		public Resource loadResource(final String fullyQualifiedName, final String extension) {
			return project.findExtXptResource(fullyQualifiedName, extension);
		}

		public void setFileEncoding(final String fileEncoding) {
		}

		public void registerParser(final String template_extension, final ResourceParser parser) {
		}
	};
}