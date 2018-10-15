getSite().getPage().showView("org.eclipse.m2t.common.recipe.recipeBrowser.RecipeBrowserView");

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
package org.eclipse.m2t.common.recipe.ui.recipeBrowser;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.m2t.common.recipe.ui.RecipePlugin;
import org.eclipse.m2t.common.recipe.ui.action.OpenRecipesAction;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorSite;
import org.eclipse.ui.IPathEditorInput;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.part.EditorPart;
import org.eclipse.ui.progress.UIJob;

public class RecipeViewHelper extends EditorPart {

	public RecipeViewHelper() {
	}

	@Override
	public void doSave(IProgressMonitor monitor) {

	}

	@Override
	public void doSaveAs() {

	}

	@Override
	public void init(IEditorSite site, IEditorInput input) throws PartInitException {
		setSite(site);
		setInput(input);
	}

	@Override
	public boolean isDirty() {
		return false;
	}

	@Override
	public boolean isSaveAsAllowed() {
		return false;
	}

	@Override
	public void createPartControl(Composite parent) {
		if (getEditorInput() instanceof IPathEditorInput) {
			IPathEditorInput pei = (IPathEditorInput) getEditorInput();
			IFile file = ResourcesPlugin.getWorkspace().getRoot().getFile(pei.getPath());
			new OpenRecipesAction(file).run(null);
			try {
				getSite().getPage().showView("org.openarchitectureware.eclipse.recipeBrowser.RecipeBrowserView");
			} catch (PartInitException e) {
				RecipePlugin.log(e.getStatus());
			}
		}
		new UIJob("Close editor") {

			@Override
			public IStatus runInUIThread(IProgressMonitor monitor) {
				getSite().getPage().closeEditor(RecipeViewHelper.this, false);
				return Status.OK_STATUS;
			}
		}.schedule();
	}

	@Override
	public void setFocus() {

	}

}