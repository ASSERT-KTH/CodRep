+ "' not connected to any collaboration session.  To connect project, open context menu for project and choose Communications->Connect Project to Collaboration Group...");

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.example.collab.actions;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.internal.example.collab.ClientEntry;
import org.eclipse.ecf.internal.example.collab.CollabClient;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.ui.IObjectActionDelegate;
import org.eclipse.ui.IWorkbenchPart;

public class OpenSharedEditorAction implements IObjectActionDelegate {

	private IWorkbenchPart targetPart;

	private IFile file;

	public void setActivePart(IAction action, IWorkbenchPart targetPart) {
		this.targetPart = targetPart;
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
		if (file == null) {
			return;
		}
		IProject project = file.getProject();
		ClientEntry entry = isConnected(project);
		if (entry == null) {
			MessageDialog
					.openInformation(
							targetPart.getSite().getWorkbenchWindow()
									.getShell(),
							"Project Not Connected to Collaboration Group",
							"Project '"
									+ project.getName()
									+ "' not connected to any collaboration group.  To connect, open context menu for resource and choose ECF->Join ECF Collaboration...");
			return;
		}
		EclipseCollabSharedObject collabsharedobject = entry.getSharedObject();
		if (collabsharedobject != null) {
			collabsharedobject.sendLaunchEditorForFile(null, file
					.getProjectRelativePath().toString());
		}
	}

	public void selectionChanged(IAction action, ISelection selection) {
		action.setEnabled(false);
		file = null;
		if (selection instanceof IStructuredSelection) {
			IStructuredSelection ss = (IStructuredSelection) selection;
			Object obj = ss.getFirstElement();
			// now try to set relevant file
			if (obj instanceof IFile) {
				file = (IFile) obj;
				action.setEnabled(true);
			} else if (obj instanceof IAdaptable) {
				file = (IFile) ((IAdaptable) obj).getAdapter(IFile.class);
				if (file != null) {
					action.setEnabled(true);
				}
			}
		}
	}
}