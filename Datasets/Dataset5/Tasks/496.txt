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
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.ui.IObjectActionDelegate;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.ActionDelegate;
import org.eclipse.ui.part.IShowInSource;
import org.eclipse.ui.part.ShowInContext;

public class OpenSharedEditorAction extends ActionDelegate implements
		IObjectActionDelegate {
	
	IFile file;
	
	public OpenSharedEditorAction() {
		super();
	}
	protected IProject getProjectForResource(IResource res) {
		IProject proj = res.getProject();
		return proj;
	}
	protected void setFileForSelection(IAction action, ISelection s) {
		action.setEnabled(false);
		file = null;
		if (s instanceof IStructuredSelection) {
			IStructuredSelection ss = (IStructuredSelection) s;
			Object obj = ss.getFirstElement();
			// Then try to set relevant file
			if (obj instanceof IFile) {
				action.setEnabled(true);
				file = (IFile) obj;
			} else if (obj instanceof IJavaElement) {
				IJavaElement je = (IJavaElement) obj;
				IResource r = null;
				try {
					r = je.getCorrespondingResource();
				} catch (JavaModelException e) {
					r = null;;
				}
				if (r != null && r.getType() == IResource.FILE) {
					action.setEnabled(true);
					file = (IFile) r;
				}
			}
		} 
	}
	public void setActivePart(IAction action, IWorkbenchPart targetPart) {
		action.setEnabled(false);
		file = null;
		if (targetPart instanceof IViewPart) {
			Object o = targetPart.getAdapter(IShowInSource.class);
			if (o != null) {
				IShowInSource sis = (IShowInSource) o;
				ShowInContext sc = sis.getShowInContext();
				ISelection s = sc.getSelection();
				setFileForSelection(action, s);
			}
		}
	}
	protected IWorkbench getWorkbench() {
		return PlatformUI.getWorkbench();
	}
	
	protected ClientEntry isConnected(IResource res) {
		if (res == null) return null;
		CollabClient client = CollabClient.getDefault();
		ClientEntry entry = client.isConnected(res,
				CollabClient.GENERIC_CONTAINER_CLIENT_NAME);
		return entry;
	}
	
	public void run(IAction action) {
		if (file == null) {
			return;			
		}
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
			collabsharedobject.sendLaunchEditorForFile(null, file
					.getProjectRelativePath().toString());
		}
	}
}