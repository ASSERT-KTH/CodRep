super(resourceManager, currentResource, typeSystem, vars, globalVars, null, null, null, null, null, null,null);

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

package org.eclipse.xtend.shared.ui.expression;

import java.util.Map;

import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.Resource;
import org.eclipse.xtend.expression.ResourceManager;
import org.eclipse.xtend.expression.ResourceParser;
import org.eclipse.xtend.expression.TypeSystemImpl;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.PluginExecutionContext;

public class PluginExecutionContextImpl extends ExecutionContextImpl implements PluginExecutionContext {
	private final IXtendXpandProject project;

	public PluginExecutionContextImpl(final IXtendXpandProject xp, final TypeSystemImpl ts) {
		super(new PluginResourceManager(xp), ts, null);
		project = xp;
	}

	protected PluginExecutionContextImpl(ResourceManager resourceManager, Resource currentResource,
			TypeSystemImpl typeSystem, Map<String, Variable> vars, Map<String, Variable> globalVars,
			IXtendXpandProject xp) {
		super(resourceManager, currentResource, typeSystem, vars, globalVars, null, null, null, null, null, null);
		project = xp;
	}

	@Override
	public PluginExecutionContextImpl cloneContext() {
		final PluginExecutionContextImpl result = new PluginExecutionContextImpl(resourceManager, currentResource(),
				typeSystem, getVisibleVariables(), getGlobalVariables(), project);
		return result;
	}

	public static class PluginResourceManager implements ResourceManager {
		private IXtendXpandProject project;

		public PluginResourceManager(final IXtendXpandProject project) {
			this.project = project;
		}

		public Resource loadResource(final String fullyQualifiedName, final String extension) {
			return project.findExtXptResource(fullyQualifiedName, extension);
		}

		public void setFileEncoding(final String fileEncoding) {
		}

		public void registerParser(final String template_extension, final ResourceParser parser) {
		}
	}

}