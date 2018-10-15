import org.eclipse.ecf.internal.ui.UiPlugin;

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
package org.eclipse.ecf.ui.wizards;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.ui.UiPlugin;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.wizard.Wizard;
import org.eclipse.ui.IWorkbench;

public class JoinGroupWizard extends Wizard {
	
	private static final String DIALOG_SETTINGS = JoinGroupWizard.class.getName();
	
    protected JoinGroupWizardPage mainPage;
    protected ContainerTypeDescription [] descriptions = null;
    
    public JoinGroupWizard(IWorkbench workbench, String title, ContainerTypeDescription [] descriptions) {
        super();
        setWindowTitle(title);
        this.descriptions = descriptions;
        IDialogSettings dialogSettings = UiPlugin.getDefault().getDialogSettings();
        IDialogSettings wizardSettings = dialogSettings.getSection(DIALOG_SETTINGS);
        if (wizardSettings == null)
        	wizardSettings = dialogSettings.addNewSection(DIALOG_SETTINGS);
        
        setDialogSettings(wizardSettings);
        
    }

    public JoinGroupWizard(IWorkbench workbench, String title) {
    	this(workbench,title,null);
    }
    public void addPages() {
        super.addPages();
        mainPage = new JoinGroupWizardPage(descriptions);
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
        
    }
}