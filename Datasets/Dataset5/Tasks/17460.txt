package org.eclipse.ecf.internal.ui.deprecated;

/*******************************************************************************
 * Copyright (c) 2004, 2007 Remy Suen, Composent, Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.ui;

import org.eclipse.ecf.internal.ui.Activator;
import org.eclipse.jface.preference.FieldEditorPreferencePage;
import org.eclipse.jface.preference.RadioGroupFieldEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPreferencePage;

public class ChatPreferencePage extends FieldEditorPreferencePage implements
		IWorkbenchPreferencePage {

	public static final String PREF_BROWSER_FOR_CHAT = "chatBrowser"; //$NON-NLS-1$

	public static final String VIEW = "view"; //$NON-NLS-1$

	public static final String EDITOR = "editor"; //$NON-NLS-1$

	public static final String EXTERNAL = "external"; //$NON-NLS-1$

	public ChatPreferencePage() {
		super(GRID);
		setPreferenceStore(Activator.getDefault().getPreferenceStore());
	}

	protected void createFieldEditors() {
		Label label = new Label(getFieldEditorParent(), SWT.WRAP);
		label.setText("If the preferences in 'General - Web Browser' has "
				+ "set the workbench to use an external browser, the settings "
				+ "below will be ignored.");
		addField(new RadioGroupFieldEditor(PREF_BROWSER_FOR_CHAT,
				"Browser to use for chat window hyperlinks", 1, new String[][] {
						{ "View", VIEW }, { "Editor", EDITOR },
						{ "External", EXTERNAL } }, getFieldEditorParent(),
				true));
	}

	public void init(IWorkbench workbench) {
		// nothing to do
	}
}