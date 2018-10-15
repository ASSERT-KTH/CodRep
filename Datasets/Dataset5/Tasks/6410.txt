super(Messages.BuildJob_JobName + project.getName());

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xtend.typesystem.emf.ui;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IncrementalProjectBuilder;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.xtend.shared.ui.core.builder.XtendXpandBuilder;

public class BuildJob extends Job {
	private final IProject project;

	public BuildJob(final IProject project) {
		super("Building " + project.getName());
		setRule(ResourcesPlugin.getWorkspace().getRuleFactory().buildRule());
		this.project = project;
	}

	@Override
	protected IStatus run(final IProgressMonitor monitor) {
		if (EmfToolsPlugin.trace) {
			System.out.println("Running Xtend/Xpand builder for project " + project.getName());
		}

		try {
			project.getProject().build(IncrementalProjectBuilder.CLEAN_BUILD, XtendXpandBuilder.getBUILDER_ID(), null,
					monitor);
		}
		catch (final CoreException e) {
			if (EmfToolsPlugin.trace) {
				e.printStackTrace();
			}
		}
		return Status.OK_STATUS;
	}
}