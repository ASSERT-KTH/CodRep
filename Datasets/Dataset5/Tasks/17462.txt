package org.eclipse.ecf.internal.ui.deprecated.views;

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
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

public class ChangePasswordDialog extends Dialog {

	private Text p1;

	private Text p2;

	private int result = Window.CANCEL;

	private String pass1 = "";

	private String pass2 = "";

	Button okButton = null;

	public ChangePasswordDialog(Shell parentShell) {
		super(parentShell);
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

		final Label label_3 = new Label(composite, SWT.NONE);
		label_3.setText("New Password:");

		p1 = new Text(composite, SWT.BORDER);
		p1.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_FILL));
		p1.setEchoChar('*');
		final Label label_2 = new Label(composite, SWT.NONE);
		label_2.setText("Re-enter Password:");

		p2 = new Text(composite, SWT.BORDER);
		final GridData gridData_1 = new GridData(GridData.FILL_HORIZONTAL);
		gridData_1.widthHint = 192;
		p2.setLayoutData(gridData_1);
		p2.setEchoChar('*');
		//
		return container;
	}

	protected void createButtonsForButtonBar(Composite parent) {
		createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL,
				false);
		createButton(parent, IDialogConstants.CANCEL_ID,
				IDialogConstants.CANCEL_LABEL, true);
		okButton = getButton(IDialogConstants.OK_ID);
		okButton.setEnabled(true);
	}

	public String getNewPassword() {
		return pass1;
	}

	protected Point getInitialSize() {
		return new Point(330, 157);
	}

	public void buttonPressed(int button) {
		result = button;
		if (button == Window.OK) {
			pass1 = p1.getText();
			pass2 = p2.getText();
			if (!pass1.equals(pass2)) {
				// message box that passwords do not match
				MessageDialog.openError(getShell(), "Passwords do not match",
						"Passwords do not match.  Please try again");
				p1.setText("");
				p2.setText("");
				p1.setFocus();
				return;
			}
		}
		close();
	}

	public int getResult() {
		return result;
	}

	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText("Change Password");
	}

}