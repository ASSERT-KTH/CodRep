NewSearchUI.runQueryInBackground(query);

/*******************************************************************************
 * Copyright (c) 2005 - 2007 committers of openArchitectureWare and others. All
 * rights reserved. This program and the accompanying materials are made
 * available under the terms of the Eclipse Public License v1.0 which
 * accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: committers of openArchitectureWare - initial API and
 * implementation
 ******************************************************************************/
package org.eclipse.xtend.shared.ui.editor.search.actions;

import org.eclipse.core.resources.IFile;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.search.ui.ISearchQuery;
import org.eclipse.search.ui.NewSearchUI;
import org.eclipse.ui.IWorkbenchSite;
import org.eclipse.xtend.shared.ui.Activator;
import org.eclipse.xtend.shared.ui.core.IXtendXpandProject;
import org.eclipse.xtend.shared.ui.core.action.SelectionDispatchAction;
import org.eclipse.xtend.shared.ui.editor.AbstractXtendXpandEditor;

/**
 * Abstract class for Xtend search actions.
 * 
 * Note: This class is for internal use only. Clients should not use this class.
 */
public abstract class FindAction extends SelectionDispatchAction {

	private AbstractXtendXpandEditor editor;

	/**
	 * Creates a new <code>FindAction</code>.
	 * 
	 * @param site
	 *            The current workbench site.
	 */
	protected FindAction(IWorkbenchSite site) {
		super(site);
		init();
	}

	/**
	 * Creates a new <code>FindAction</code>.
	 * 
	 * @param editor
	 *            The hosting editor.
	 */
	protected FindAction(AbstractXtendXpandEditor editor) {
		this(editor.getSite());
		this.editor = editor;
	}

	/**
	 * Called once by the constructors to initialize label, tooltip, image and
	 * help support of the action. To be overridden by implementors of this
	 * action.
	 */
	abstract void init();

	/**
	 * Returns the Xtend project associated with the currently edited file.
	 * 
	 * @return A reference to the current Xtend project.
	 */
	protected IXtendXpandProject getXtendXpandProject() {
		IFile file = getActiveFile();
		if (file == null) {
			return null;
		}
		return Activator.getExtXptModelManager().findProject(file);
	}

	/**
	 * Retrieve the currently edited file.
	 * 
	 * @return A reference to teh currently edited file.
	 */
	protected IFile getActiveFile() {
		return (IFile) getEditor().getEditorInput().getAdapter(IFile.class);
	}

	/**
	 * Provide access to the editor.
	 * 
	 * @return Editor reference.
	 */
	public AbstractXtendXpandEditor getEditor() {
		return editor;
	}

	@Override
	public void run(ITextSelection selection) {
		String selectedText = selection.getText();
		IXtendXpandProject project = getXtendXpandProject();

		ISearchQuery query = createSearchQuery(selectedText, project);
		NewSearchUI.runQuery(query);
	}

	protected abstract ISearchQuery createSearchQuery(String selectedText, IXtendXpandProject project);

}