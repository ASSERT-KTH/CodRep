final IMenuManager menuManager = new MenuManager(Messages.ReferencesSearchGroup_Label, IContextMenuConstants.GROUP_SEARCH);

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

import org.eclipse.core.runtime.Assert;
import org.eclipse.jdt.ui.actions.IJavaEditorActionDefinitionIds;
import org.eclipse.jdt.ui.actions.JdtActionConstants;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.search.ui.IContextMenuConstants;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.IWorkbenchSite;
import org.eclipse.ui.actions.ActionGroup;
import org.eclipse.ui.texteditor.ITextEditorActionConstants;
import org.eclipse.xtend.shared.ui.core.action.SelectionDispatchAction;
import org.eclipse.xtend.shared.ui.editor.AbstractXtendXpandEditor;

/**
 * Action group that adds the search for declarations actions to a context menu
 * and the global menu bar.
 * 
 * This class may be instantiated; it is not intended to be subclassed.
 */
public class ReferencesSearchGroup extends ActionGroup {

	private final IWorkbenchSite site;
	private IActionBars actionBars;

	private final String groupId;

	private SelectionDispatchAction findReferencesAction;

	/**
	 * Creates a new {@link DeclarationsSearchGroup}. The group requires that
	 * the selection provided by the site's selection provider is of type
	 * {@link IStructuredSelection}.
	 * 
	 * @param site
	 *            The workbench site that owns this action group
	 */
	public ReferencesSearchGroup(final IWorkbenchSite site) {
		this.site = site;
		groupId = IContextMenuConstants.GROUP_SEARCH;

		findReferencesAction = new FindReferencesAction(site);
		findReferencesAction.setActionDefinitionId(IJavaEditorActionDefinitionIds.SEARCH_REFERENCES_IN_WORKSPACE);

		// register the actions as selection listeners
		final ISelectionProvider provider = site.getSelectionProvider();
		final ISelection selection = provider.getSelection();
		registerAction(findReferencesAction, provider, selection);
	}

	/**
	 * Note: This constructor is for internal use only. Clients should not call
	 * this constructor.
	 * 
	 * @param editor
	 *            ehe editor
	 */
	protected ReferencesSearchGroup(final AbstractXtendXpandEditor editor) {
		Assert.isNotNull(editor);
		site = editor.getSite();
		groupId = ITextEditorActionConstants.GROUP_FIND;

		findReferencesAction = new FindReferencesAction(editor);
		findReferencesAction.setActionDefinitionId(IJavaEditorActionDefinitionIds.SEARCH_REFERENCES_IN_WORKSPACE);
		editor.setAction("SearchReferencesInWorkspace", findReferencesAction); //$NON-NLS-1$

	}

	private void registerAction(final SelectionDispatchAction action, final ISelectionProvider provider,
			final ISelection selection) {
		action.update(selection);
		provider.addSelectionChangedListener(action);
	}

	private void addAction(final IAction action, final IMenuManager manager) {
		if (action.isEnabled()) {
			manager.add(action);
		}
	}

	@Override
	public void fillActionBars(final IActionBars actionBars) {
		Assert.isNotNull(actionBars);
		super.fillActionBars(actionBars);
		this.actionBars = actionBars;
		updateGlobalActionHandlers();
	}

	@Override
	public void fillContextMenu(final IMenuManager manager) {
		final IMenuManager menuManager = new MenuManager("Re&ferences", IContextMenuConstants.GROUP_SEARCH);
		addAction(findReferencesAction, menuManager);

		menuManager.add(new Separator());

		if (!menuManager.isEmpty()) {
			manager.appendToGroup(groupId, menuManager);
		}
	}

	@Override
	public void dispose() {
		final ISelectionProvider provider = site.getSelectionProvider();
		if (provider != null) {
			disposeAction(findReferencesAction, provider);
		}
		findReferencesAction = null;
		updateGlobalActionHandlers();
		super.dispose();
	}

	private void updateGlobalActionHandlers() {
		if (actionBars != null) {
			actionBars.setGlobalActionHandler(JdtActionConstants.FIND_REFERENCES_IN_WORKSPACE, findReferencesAction);
		}
	}

	private void disposeAction(final ISelectionChangedListener action, final ISelectionProvider provider) {
		if (action != null) {
			provider.removeSelectionChangedListener(action);
		}
	}
}