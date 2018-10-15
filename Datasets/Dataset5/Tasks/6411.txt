MessageDialog.openError(shell, Messages.AbstractCoreModelTransformerAction_PluginName, e.getMessage());

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
package org.eclipse.xtend.typesystem.emf.ui.actions;

import java.io.IOException;

import org.eclipse.core.resources.IFile;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IActionDelegate;
import org.eclipse.ui.IObjectActionDelegate;
import org.eclipse.ui.IWorkbenchPart;

public abstract class AbstractCoreModelTransformerAction implements IObjectActionDelegate {

	private IFile file;

	protected static final String ANNO_SOURCE = "http://www.eclipse.org/emf/2002/GenModel";

	protected static final String ANNO_KEY = "body";

	/**
	 * Constructor for Action1.
	 */
	public AbstractCoreModelTransformerAction() {
		super();
	}

	/**
	 * @see IObjectActionDelegate#setActivePart(IAction, IWorkbenchPart)
	 */
	public void setActivePart(final IAction action, final IWorkbenchPart targetPart) {
	}

	/**
	 * @see IActionDelegate#run(IAction)
	 */
	public void run(final IAction action) {
		final URI fileURI = URI.createPlatformResourceURI(file.getFullPath().toPortableString(), true);

		final Resource r = new ResourceSetImpl().createResource(fileURI);
		try {
			r.load(null);
		}
		catch (final IOException e) {
			throwE(e);
		}
		transform(r);
		try {
			r.save(null);
		}
		catch (final IOException e) {
			throwE(e);
		}
	}

	public abstract void transform(Resource r);

	public void throwE(final IOException e) {
		final Shell shell = new Shell();
		MessageDialog.openError(shell, "Xtend EMF Eclipse Plug-in", e.getMessage());
		throw new RuntimeException(e);
	}

	/**
	 * @see IActionDelegate#selectionChanged(IAction, ISelection)
	 */
	public void selectionChanged(final IAction action, final ISelection selection) {
		if (selection instanceof IStructuredSelection) {
			final IStructuredSelection structuredSelection = (IStructuredSelection) selection;
			final Object object = structuredSelection.getFirstElement();
			if (object instanceof IFile) {
				file = (IFile) object;
			}
		}
	}

}