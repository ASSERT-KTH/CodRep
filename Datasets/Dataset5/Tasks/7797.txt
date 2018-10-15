if ( !getFileName().endsWith("."+extension) ) return Messages.NewExtXptResourceWizardPage_Error+extension;

/*******************************************************************************
 * Copyright (c) 2005, 2006 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xtend.shared.ui.wizards;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.ui.dialogs.WizardNewFileCreationPage;
import org.eclipse.xtend.shared.ui.Messages;

public class NewExtXptResourceWizardPage extends WizardNewFileCreationPage {

	private String extension;
	private String initialContents;
	
	public NewExtXptResourceWizardPage(String pageName, IStructuredSelection selection, String initial, String extension, String initialContents ) {
		super(pageName, selection);
		setFileName(initial);
		this.extension = extension;
		this.initialContents = initialContents;
	}
	
	@Override
	public String getErrorMessage() {
		if ( !getFileName().endsWith("."+extension) ) return Messages.NewOAWResourcePage_Error+extension;
		return null;
	}
	
	@Override
	protected InputStream getInitialContents() {
		if ( initialContents == null ) initialContents = "";
		return new ByteArrayInputStream(initialContents.getBytes()); 
	}

}