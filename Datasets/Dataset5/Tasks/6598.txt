client = new URIClientConnectAction(containerType,groupName,nickName,password,project,false);

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
package org.eclipse.ecf.example.collab.ui;

import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.ISchedulingRule;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.actions.URIClientConnectAction;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.wizard.Wizard;
import org.eclipse.ui.IWorkbench;

public class JoinGroupWizard extends Wizard {
	
	protected static final String PAGE_TITLE = "ECF Connect";

	private static final String DIALOG_SETTINGS = JoinGroupWizard.class.getName();
	
    JoinGroupWizardPage mainPage;
    private IResource project;

    public JoinGroupWizard(IResource project, IWorkbench workbench) {
        super();
        this.project = project;
        setWindowTitle(PAGE_TITLE);
        IDialogSettings dialogSettings = ClientPlugin.getDefault().getDialogSettings();
        IDialogSettings wizardSettings = dialogSettings.getSection(DIALOG_SETTINGS);
        if (wizardSettings == null)
        	wizardSettings = dialogSettings.addNewSection(DIALOG_SETTINGS);
        
        setDialogSettings(wizardSettings);
    }

    protected ISchedulingRule getSchedulingRule() {
        return project;
    }
    public void addPages() {
        super.addPages();
        mainPage = new JoinGroupWizardPage();
        addPage(mainPage);
    }

    public boolean performFinish() {
        try {
            finishPage(new NullProgressMonitor());
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    protected void finishPage(final IProgressMonitor monitor)
            throws InterruptedException, CoreException {
        
    	mainPage.saveDialogSettings();
    	URIClientConnectAction client = null;
        String groupName = mainPage.getJoinGroupText();
        String nickName = mainPage.getNicknameText();
        String containerType = mainPage.getContainerType();
        String password = mainPage.getPasswordText();
		//String namespace = mainPage.getNamespace();
        try {
        	/*
			ID groupID = null;
			if (namespace != null) {
				groupID = IDFactory.getDefault().createID(namespace,new Object[] { groupName });
			} else groupID = IDFactory.getDefault().createStringID(groupName);
            client = new ClientConnectAction();
            client.setProject(project);
            client.setUsername(nickName);
            client.setTargetID(groupID);
            client.setContainerType(containerType);
            client.setData(password);
            client.run(null);
            */
        	//URI uri = new URI(groupName);
        	//URI fullURI = new URI(namespace+":"+groupName);
        	client = new URIClientConnectAction(containerType,groupName,nickName,password,project);
        	client.run(null);
        } catch (Exception e) {
            String id = ClientPlugin.getDefault().getBundle().getSymbolicName();
            throw new CoreException(new Status(Status.ERROR, id, 100, "Could not connect to "+groupName, e));
        }
    }
}