protected static final String PAGE_TITLE = "Collaboration Connect";

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
package org.eclipse.ecf.internal.example.collab.ui;

import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.ISchedulingRule;
import org.eclipse.ecf.internal.example.collab.ClientPlugin;
import org.eclipse.ecf.internal.example.collab.actions.URIClientConnectAction;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.wizard.Wizard;
import org.eclipse.ui.IWorkbench;

public class JoinGroupWizard extends Wizard {

	protected static final String PAGE_TITLE = "ECF Collaboration Connect";

	private static final String DIALOG_SETTINGS = JoinGroupWizard.class
			.getName();

	JoinGroupWizardPage mainPage;
	private IResource resource;

	public JoinGroupWizard(IResource resource, IWorkbench workbench) {
		super();
		this.resource = resource;
		setWindowTitle(PAGE_TITLE);
		IDialogSettings dialogSettings = ClientPlugin.getDefault()
				.getDialogSettings();
		IDialogSettings wizardSettings = dialogSettings
				.getSection(DIALOG_SETTINGS);
		if (wizardSettings == null)
			wizardSettings = dialogSettings.addNewSection(DIALOG_SETTINGS);

		setDialogSettings(wizardSettings);
	}

	protected ISchedulingRule getSchedulingRule() {
		return resource;
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
		boolean autoLogin = mainPage.getAutoLoginFlag();
		try {
			client = new URIClientConnectAction(containerType, groupName,
					nickName, "", resource, autoLogin);
			client.run(null);
		} catch (Exception e) {
			String id = ClientPlugin.getDefault().getBundle().getSymbolicName();
			throw new CoreException(new Status(Status.ERROR, id, IStatus.ERROR,
					"Could not connect to " + groupName, e));
		}
	}
}