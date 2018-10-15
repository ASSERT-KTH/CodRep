return wizard.getContainerConfigurationResult();

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
package org.eclipse.ecf.ui.dialogs;

import org.eclipse.ecf.ui.ContainerConfigurationResult;
import org.eclipse.ecf.ui.wizards.ConfigurationWizardSelectionWizard;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IWorkbench;

public class ConfigurationWizardDialog extends WizardDialog {

	ConfigurationWizardSelectionWizard wizard = null;

	public ConfigurationWizardDialog(Shell shell, IWorkbench workbench,
			IStructuredSelection selection) {
		super(shell, new ConfigurationWizardSelectionWizard());
		this.wizard = (ConfigurationWizardSelectionWizard) getWizard();
		wizard.init(workbench, selection);
	}

	public ConfigurationWizardDialog(Shell shell, IWorkbench workbench) {
		this(shell, workbench, null);
	}

	public ContainerConfigurationResult getResult() {
		return wizard.getResult();
	}
}