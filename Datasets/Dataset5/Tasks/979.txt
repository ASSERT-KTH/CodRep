action.setEnabled(resource == null ? false : resource.isAccessible());

/****************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.example.collab.actions;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.internal.example.collab.ClientEntry;
import org.eclipse.ecf.internal.example.collab.CollabClient;
import org.eclipse.ecf.internal.example.collab.ui.JoinGroupWizard;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.ui.IObjectActionDelegate;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.PlatformUI;

public class JoinGroupWizardAction implements IObjectActionDelegate {

	private static final String CONNECT_PROJECT_MENU_TEXT = "Connect Project to Collaboration Group...";
	private static final String DISCONNECT_PROJECT_MENU_TEXT = "Disconnect Project";

	private IResource resource;
	private boolean connected = false;
	private IWorkbenchPart targetPart;

	private ClientEntry isConnected(IResource res) {
		if (res == null)
			return null;
		CollabClient client = CollabClient.getDefault();
		ClientEntry entry = client.isConnected(res,
				CollabClient.GENERIC_CONTAINER_CLIENT_NAME);
		return entry;
	}

	private void setAction(IAction action, IResource resource) {
		if (isConnected(resource) != null) {
			action.setText(DISCONNECT_PROJECT_MENU_TEXT);
			connected = true;
		} else {
			action.setText(CONNECT_PROJECT_MENU_TEXT);
			connected = false;
		}
		action.setEnabled(resource.isAccessible());
	}

	public void setActivePart(IAction action, IWorkbenchPart targetPart) {
		this.targetPart = targetPart;
	}

	public void run(IAction action) {
		if (!connected) {
			JoinGroupWizard wizard = new JoinGroupWizard(resource, PlatformUI
					.getWorkbench());
			// Create the wizard dialog
			WizardDialog dialog = new WizardDialog(targetPart.getSite()
					.getShell(), wizard);
			// Open the wizard dialog
			dialog.open();
		} else {
			ClientEntry client = isConnected(resource);
			if (client == null) {
				connected = false;
				action.setText(CONNECT_PROJECT_MENU_TEXT);
			} else {
				EclipseCollabSharedObject collab = client.getSharedObject();
				if (collab != null) {
					collab.chatGUIDestroy();
				}
			}
		}
	}

	public void selectionChanged(IAction action, ISelection selection) {
		if (selection instanceof IStructuredSelection) {
			IStructuredSelection iss = (IStructuredSelection) selection;
			Object obj = iss.getFirstElement();
			if (obj instanceof IProject) {
				resource = (IProject) obj;
			} else if (obj instanceof IAdaptable) {
				resource = (IProject) ((IAdaptable) obj)
						.getAdapter(IProject.class);
			} else {
				resource = null;
			}
		} else {
			resource = null;
		}
		setAction(action, resource);
	}
}