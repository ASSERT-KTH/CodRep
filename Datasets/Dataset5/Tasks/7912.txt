getPreferenceStore().setDefault(CONTAINER_TYPE, "ecf.generic.client");

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

package org.eclipse.ecf.example.collab.editor.preferences;

import java.net.Inet4Address;
import java.net.UnknownHostException;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.example.collab.editor.Activator;
import org.eclipse.jface.preference.FieldEditorPreferencePage;
import org.eclipse.jface.preference.StringFieldEditor;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPreferencePage;

public class ClientPreferencePage extends FieldEditorPreferencePage implements
		IWorkbenchPreferencePage {


	public static final String CONTAINER_TYPE = "CONTAINER_TYPE";
	public static final String TARGET_SERVER = "TARGET_SERVER";
	public static final String CHANNEL_ID = "CHANNEL_ID";
	public static final String LOCAL_NAME = "LOCAL_NAME";
	
	/* (non-Javadoc)
	 * @see org.eclipse.jface.preference.PreferencePage#performDefaults()
	 */
	protected void performDefaults() {
		super.performDefaults();
		
		getPreferenceStore().setDefault(CONTAINER_TYPE, "ecf.generic.channel");
		getPreferenceStore().setDefault(TARGET_SERVER, "ecftcp://localhost:3282/server");
		getPreferenceStore().setDefault(CHANNEL_ID, "collab.editor");
		try {
			getPreferenceStore().setDefault(LOCAL_NAME, Inet4Address.getLocalHost().getHostName());
		} catch (UnknownHostException e) {
			Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, 0, e.getLocalizedMessage(), e));
		}
	}
	
	public ClientPreferencePage() {
		super(GRID);
		setPreferenceStore(Activator.getDefault().getPreferenceStore());
	}
	
	public void createFieldEditors() {
		addField(new StringFieldEditor(CONTAINER_TYPE, "Container Type:", this.getFieldEditorParent()));
		addField(new StringFieldEditor(TARGET_SERVER, "ECF Server URL:", this.getFieldEditorParent()));
		addField(new StringFieldEditor(CHANNEL_ID, "ChatRoomTab (Group) Name:", this.getFieldEditorParent()));
		addField(new StringFieldEditor(LOCAL_NAME, "Your Name:", this.getFieldEditorParent()));
		
	}
	
	public void init(IWorkbench workbench) {
		
	}
	
	public void initializeDefaults() {
		performDefaults();
	}	
}
 No newline at end of file