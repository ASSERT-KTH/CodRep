+ "' not connected to any collaboration group.  To connect, open context menu for resource and choose ECF->Join ECF Collaboration...");

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.example.collab.actions;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.ecf.example.collab.ClientEntry;
import org.eclipse.ecf.example.collab.CollabClient;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.ui.IEditorActionDelegate;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.FileEditorInput;
import org.eclipse.ui.texteditor.ITextEditor;

public class SetSharedEditorSelectionAction implements IEditorActionDelegate {
	ITextEditor editor = null;

	public void setActiveEditor(IAction action, IEditorPart targetEditor) {
		action.setEnabled(false);
		if (targetEditor instanceof ITextEditor) {
			// Got one
			editor = (ITextEditor) targetEditor;
			setEnabled(action);
		}
	}
	
	protected void setEnabled(IAction action) {
		action.setEnabled(false);
		if (editor == null) return;
		IFile file = getFileForPart(editor);
		if (file != null) {
			ClientEntry client = isConnected(file.getProject());
			if (client != null) {
				action.setEnabled(true);
			}
		}
	}
	protected IFile getFileForPart(ITextEditor editor) {
		IEditorInput input = editor.getEditorInput();
		if (input instanceof FileEditorInput) {
			FileEditorInput fei = (FileEditorInput) input;
			return fei.getFile();
		}
		return null;
	}
	protected IProject getProjectForResource(IResource res) {
		IProject proj = res.getProject();
		return proj;
	}
	protected IWorkbench getWorkbench() {
		return PlatformUI.getWorkbench();
	}
	protected ClientEntry isConnected(IResource res) {
		if (res == null)
			return null;
		CollabClient client = CollabClient.getDefault();
		ClientEntry entry = client.isConnected(res,
				CollabClient.GENERIC_CONTAINER_CLIENT_NAME);
		return entry;
	}
	public void run(IAction action) {
		if (editor == null)
			return;
		ISelection s = editor.getSelectionProvider().getSelection();
		ITextSelection textSelection = null;
		if (s instanceof ITextSelection) {
			textSelection = (ITextSelection) s;
		}
		if (textSelection == null)
			return;
		IFile file = getFileForPart(editor);
		if (file == null)
			return;
		IProject project = getProjectForResource(file);
		ClientEntry entry = isConnected(project);
		if (entry == null) {
			MessageDialog
					.openInformation(
							getWorkbench().getDisplay().getActiveShell(),
							"Project Not Connected to Collaboration Group",
							"Project '"
									+ project.getName()
									+ "' not connected to any collaboration group.  To connect, open context menu for project and choose ECF->Join ECF Collaboration...");
			return;
		}
		EclipseCollabSharedObject collabsharedobject = entry.getObject();
		if (collabsharedobject != null) {
			collabsharedobject.sendOpenAndSelectForFile(null, file
					.getProjectRelativePath().toString(), textSelection
					.getOffset(), textSelection.getLength());
//			collabsharedobject.sendAddMarkerForFile(null, file
//					.getProjectRelativePath().toString(), textSelection
//					.getOffset(), textSelection.getLength());
		}
	}
	public void selectionChanged(IAction action, ISelection selection) {
		setEnabled(action);
	}
}