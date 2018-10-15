collabsharedobject.sendOpenAndSelectForFile(null, project.getName() + "/" + file.getProjectRelativePath().toString(), textSelection.getOffset(), textSelection.getLength()); //$NON-NLS-1$

package org.eclipse.ecf.internal.example.collab;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.ActionContributionItem;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IContributionItem;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPartSite;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.CompoundContributionItem;
import org.eclipse.ui.part.FileEditorInput;

public class EditorCompoundContributionItem extends CompoundContributionItem {

	private static final IContributionItem[] EMPTY = new IContributionItem[] {};

	public EditorCompoundContributionItem() {
	}

	public EditorCompoundContributionItem(String id) {
		super(id);
	}

	protected IFile getFileForPart(IEditorPart editorPart) {
		final IEditorInput input = editorPart.getEditorInput();
		if (input instanceof FileEditorInput) {
			final FileEditorInput fei = (FileEditorInput) input;
			return fei.getFile();
		}
		return null;
	}

	protected ClientEntry isConnected(IResource res) {
		if (res == null)
			return null;
		final CollabClient client = CollabClient.getDefault();
		final ClientEntry entry = client.isConnected(res, CollabClient.GENERIC_CONTAINER_CLIENT_NAME);
		return entry;
	}

	protected IEditorPart getEditorPart() {
		final IWorkbench workbench = PlatformUI.getWorkbench();
		if (workbench == null)
			return null;
		final IWorkbenchWindow ww = workbench.getActiveWorkbenchWindow();
		if (ww == null)
			return null;
		final IWorkbenchPage wp = ww.getActivePage();
		if (wp == null)
			return null;
		return wp.getActiveEditor();
	}

	protected ITextSelection getSelection() {
		final IEditorPart ep = getEditorPart();
		if (ep == null)
			return null;
		final IWorkbenchPartSite ws = ep.getEditorSite();
		if (ws == null)
			return null;
		final ISelectionProvider sp = ws.getSelectionProvider();
		if (sp == null)
			return null;
		final ISelection sel = sp.getSelection();
		if (sel == null || !(sel instanceof ITextSelection))
			return null;
		return (ITextSelection) sel;
	}

	protected IContributionItem[] getContributionItems() {
		final ITextSelection textSelection = getSelection();
		if (textSelection == null)
			return EMPTY;
		final IEditorPart editorPart = getEditorPart();
		if (editorPart == null)
			return EMPTY;
		final IFile file = getFileForPart(editorPart);
		if (file == null)
			return EMPTY;
		final IProject project = file.getProject();
		if (isConnected(project.getWorkspace().getRoot()) == null)
			return EMPTY;

		final IAction action = new Action() {
			public void run() {
				final ClientEntry entry = isConnected(project.getWorkspace().getRoot());
				if (entry == null) {
					MessageDialog.openInformation(PlatformUI.getWorkbench().getDisplay().getActiveShell(), Messages.EditorCompoundContributionItem_EXCEPTION_NOT_CONNECTED_TITLE, Messages.EditorCompoundContributionItem_EXCEPTION_NOT_CONNECTED_MESSAGE);
					return;
				}
				final EclipseCollabSharedObject collabsharedobject = entry.getSharedObject();
				if (collabsharedobject != null) {
					collabsharedobject.sendOpenAndSelectForFile(null, project.getName() + "/" + file.getProjectRelativePath().toString(), textSelection.getOffset(), textSelection.getLength());
				}
			}
		};

		action.setText(Messages.EditorCompoundContributionItem_SHARE_SELECTION_MENU_ITEM_NAME);
		//action.setAccelerator(SWT.CTRL | SWT.SHIFT | '1');
		return new IContributionItem[] {new Separator(), new ActionContributionItem(action)};
	}
}