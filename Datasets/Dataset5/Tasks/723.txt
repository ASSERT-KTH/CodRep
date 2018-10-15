URIClientConnectAction action = new URIClientConnectAction();

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.example.collab.actions;

import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.ecf.example.collab.ui.JoinGroupWizard;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.IWorkbenchWindowActionDelegate;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.ActionDelegate;

/**
 * @author slewis
 *
 */
public class WorkbenchAction extends ActionDelegate implements IWorkbenchWindowActionDelegate {
    
    public void run() {
        IResource resource = ResourcesPlugin.getWorkspace().getRoot();
        ClientConnectAction action = new ClientConnectAction();
        action.setProject(resource);
    }

    protected IWorkbench getWorkbench() {
        return PlatformUI.getWorkbench();
    }

    /* (non-Javadoc)
     * @see org.eclipse.ui.IWorkbenchWindowActionDelegate#dispose()
     */
    public void dispose() {
    }

    /* (non-Javadoc)
     * @see org.eclipse.ui.IWorkbenchWindowActionDelegate#init(org.eclipse.ui.IWorkbenchWindow)
     */
    public void init(IWorkbenchWindow window) {
    }

    /* (non-Javadoc)
     * @see org.eclipse.ui.IActionDelegate#run(org.eclipse.jface.action.IAction)
     */
    public void run(IAction action) {
        IResource resource = ResourcesPlugin.getWorkspace().getRoot();
        JoinGroupWizard wizard = new JoinGroupWizard(resource,getWorkbench());
        // Create the wizard dialog
        WizardDialog dialog = new WizardDialog
         (getWorkbench().getActiveWorkbenchWindow().getShell(),wizard);
        // Open the wizard dialog
        dialog.open();
    }

    /* (non-Javadoc)
     * @see org.eclipse.ui.IActionDelegate#selectionChanged(org.eclipse.jface.action.IAction, org.eclipse.jface.viewers.ISelection)
     */
    public void selectionChanged(IAction action, ISelection selection) {
    }
}