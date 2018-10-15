//final Label l = new Label(composite, SWT.NONE);

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

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

public class AddBuddyDialog extends Dialog {

	private Text usertext;
	private Text nicknametext;
	private Combo groups;
	
	private String user = null;
	
	private int result = Window.CANCEL;
	
	private String userresult = "";
	private String nicknameresult = "";
	private String groupsresult = "";
	
	Button okButton = null;
	
	public AddBuddyDialog(Shell parentShell, String [] existingGroups, int selectedGroup) {
		this(parentShell, null, existingGroups, selectedGroup);
	}
	public AddBuddyDialog(Shell parentShell,String username, String [] existingGroups, int selectedGroup) {
		super(parentShell);
		this.user = username;
	}
	protected Control createDialogArea(Composite parent) {
		Composite container = (Composite) super.createDialogArea(parent);
		final GridLayout gridLayout = new GridLayout();
		gridLayout.horizontalSpacing = 0;
		container.setLayout(gridLayout);

		final Composite composite = new Composite(container, SWT.NONE);
		final GridLayout gridLayout_2 = new GridLayout();
		gridLayout_2.numColumns = 2;
		composite.setLayout(gridLayout_2);

		final Label l = new Label(composite, SWT.NONE);
		
		final Label label_4 = new Label(composite, SWT.NONE);
		label_4.setText("<user>@<jabberserver>");

		final Label label_3 = new Label(composite, SWT.NONE);
		label_3.setText("Jabber User ID:");

		usertext = new Text(composite, SWT.BORDER);
		usertext.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_FILL));
		if (user != null) {
			usertext.setText(user);
			usertext.setEnabled(false);
		}
		usertext.addModifyListener(new ModifyListener() {

			public void modifyText(ModifyEvent e) {
				if (user != null || (usertext.getText().length() > 3 && usertext.getText().indexOf("@") != -1)) {
					okButton.setEnabled(true);
				} else {
					okButton.setEnabled(false);
				}
			}});
		/*
		final Label label_1 = new Label(composite, SWT.NONE);
		label_1.setText("Group:");

		groups = new Combo(composite, SWT.NONE);
		groups.setToolTipText("Select group or enter new group");
		final GridData gridData = new GridData(GridData.FILL_HORIZONTAL);
		gridData.widthHint = 141;
		groups.setLayoutData(gridData);
		if (existing != null) {
			for(int i=0; i < existing.length; i++) {
				groups.add(existing[i]);
			}
			if (selectedGroup != -1) groups.select(selectedGroup);
			else groups.select(0);
		}
		*/
		final Label label_2 = new Label(composite, SWT.NONE);
		label_2.setText("Nickname:");

		nicknametext = new Text(composite, SWT.BORDER);
		final GridData gridData_1 = new GridData(GridData.FILL_HORIZONTAL);
		gridData_1.widthHint = 192;
		nicknametext.setLayoutData(gridData_1);
		if (user != null) {
			nicknametext.setFocus();
		}
		//
		return container;
	}

	protected void createButtonsForButtonBar(Composite parent) {
		createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL,
				false);
		createButton(parent, IDialogConstants.CANCEL_ID,
				IDialogConstants.CANCEL_LABEL, true);
		okButton = getButton(IDialogConstants.OK_ID);
		if (okButton != null) {
			if (user != null) okButton.setEnabled(true);
			else okButton.setEnabled(false);
		}
	}
	public String getGroup() {
		return groupsresult;
	}
	public String getUser() {
		return userresult;
	}
	public String getNickname() {
		return nicknameresult;
	}
	protected Point getInitialSize() {
		return new Point(310, 197);
	}
	public void buttonPressed(int button) {
		result = button;
		userresult = usertext.getText();
		nicknameresult = nicknametext.getText();
		if (groups != null) {
			groupsresult = groups.getText();
		}
		close();
	}
	public int getResult() {
		return result;
	}
	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText("Add Buddy");
	}

}