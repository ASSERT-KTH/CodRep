} else

/*******************************************************************************
 * Copyright (c) 2008 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.internal.filetransfer.ui;

import java.io.File;
import java.net.URL;
import org.eclipse.core.runtime.Platform;
import org.eclipse.jface.dialogs.*;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.*;

public class StartFileDownloadDialog extends InputDialog {

	private Text useridText;
	private Text passwordText;
	public String userid;
	public String passwd;
	public String filename;
	protected Text fileLocation;

	static private IInputValidator inputValidator = new IInputValidator() {
		public String isValid(String newText) {
			try {
				new URL(newText);
				return null;
			} catch (Exception e) {
				return ("".equals(newText)) ? null : NLS.bind(Messages.getString("StartFileDownloadDialog.MalformedURLException"), newText); //$NON-NLS-1$ //$NON-NLS-2$
			}
		}
	};

	public StartFileDownloadDialog(Shell parentShell) {
		super(parentShell, Messages.getString("StartFileDownloadDialog.FileTransfer"), Messages.getString("StartFileDownloadDialog.Source"), null, inputValidator); //$NON-NLS-1$ //$NON-NLS-2$
	}

	Text getInputText() {
		return getText();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.jface.dialogs.Dialog#create()
	 */
	public void create() {
		super.create();
		Button okButton = getButton(IDialogConstants.OK_ID);
		okButton.setText(Messages.getString("StartFileDownloadDialog.DOWNLOAD_BUTTON")); //$NON-NLS-1$
		okButton.setToolTipText(Messages.getString("StartFileDownloadDialog.DOWNLOAD_BUTTON_TOOLTIP")); //$NON-NLS-1$
		okButton.setEnabled(false);
	}

	protected Control createDialogArea(Composite parent) {
		Composite composite = (Composite) super.createDialogArea(parent);
		Label label = new Label(composite, SWT.WRAP);
		label.setText(Messages.getString("StartFileDownloadDialog.OutputFile")); //$NON-NLS-1$
		GridData data = new GridData(GridData.GRAB_HORIZONTAL | GridData.GRAB_VERTICAL | GridData.HORIZONTAL_ALIGN_FILL | GridData.VERTICAL_ALIGN_CENTER);
		data.widthHint = convertHorizontalDLUsToPixels(IDialogConstants.MINIMUM_MESSAGE_AREA_WIDTH);
		label.setLayoutData(data);
		label.setFont(parent.getFont());

		String userhome = System.getProperty("user.home"); //$NON-NLS-1$
		if (Platform.getOS().startsWith("win")) { //$NON-NLS-1$
			userhome = userhome + File.separator + "Desktop"; //$NON-NLS-1$
		}
		final String path = userhome;

		fileLocation = new Text(composite, SWT.SINGLE | SWT.BORDER);
		fileLocation.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_FILL));
		fileLocation.setText(path);
		fileLocation.setSelection(fileLocation.getText().length());

		Text text = getInputText();
		text.addFocusListener(new FocusListener() {
			public void focusGained(FocusEvent e) {
				// nothing
			}

			public void focusLost(FocusEvent e) {
				String scp = ((Text) e.getSource()).getText();
				String fileName = ""; //$NON-NLS-1$
				if (scp != null && scp.length() > 0) {
					fileName = scp.substring(scp.lastIndexOf('/') + 1);
				}
				fileLocation.setText(path + File.separator + fileName);
				fileLocation.setSelection(fileLocation.getText().length());
			}
		});

		final Button fileBrowse = new Button(composite, SWT.PUSH);
		fileBrowse.setText(Messages.getString("StartFileDownloadDialog.Browse")); //$NON-NLS-1$
		fileBrowse.addListener(SWT.Selection, new Listener() {
			public void handleEvent(Event event) {
				if (event.type == SWT.Selection) {
					String scp = getInputText().getText();
					String fileName = ""; //$NON-NLS-1$
					if (scp != null && scp.length() > 0) {
						fileName = scp.substring(scp.lastIndexOf('/') + 1);
					}
					FileDialog fd = new FileDialog(fileBrowse.getShell(), SWT.SAVE);
					fd.setText(Messages.getString("StartFileDownloadDialog.OutputFile")); //$NON-NLS-1$
					fd.setFileName(fileName);
					fd.setFilterPath(path);
					String fname = fd.open();
					if (fname != null) {
						fileLocation.setText(fname);
						fileLocation.setSelection(fileLocation.getText().length());
					}
				}
			}
		});

		label = new Label(composite, SWT.WRAP);
		label.setText(Messages.getString("StartFileDownloadDialog.Userid")); //$NON-NLS-1$
		data = new GridData(GridData.GRAB_HORIZONTAL | GridData.GRAB_VERTICAL | GridData.HORIZONTAL_ALIGN_FILL | GridData.VERTICAL_ALIGN_CENTER);
		data.widthHint = convertHorizontalDLUsToPixels(IDialogConstants.MINIMUM_MESSAGE_AREA_WIDTH);
		label.setLayoutData(data);
		label.setFont(parent.getFont());
		useridText = new Text(composite, SWT.SINGLE | SWT.BORDER);
		useridText.setLayoutData(new GridData(GridData.GRAB_HORIZONTAL | GridData.HORIZONTAL_ALIGN_FILL));
		useridText.setText(System.getProperty("user.name")); //$NON-NLS-1$
		useridText.setSelection(useridText.getText().length());

		label = new Label(composite, SWT.WRAP);
		label.setText(Messages.getString("StartFileDownloadDialog.Password")); //$NON-NLS-1$
		data = new GridData(GridData.GRAB_HORIZONTAL | GridData.GRAB_VERTICAL | GridData.HORIZONTAL_ALIGN_FILL | GridData.VERTICAL_ALIGN_CENTER);
		data.widthHint = convertHorizontalDLUsToPixels(IDialogConstants.MINIMUM_MESSAGE_AREA_WIDTH);
		label.setLayoutData(data);
		label.setFont(parent.getFont());
		passwordText = new Text(composite, SWT.SINGLE | SWT.BORDER | SWT.PASSWORD);
		passwordText.setLayoutData(new GridData(GridData.GRAB_HORIZONTAL | GridData.HORIZONTAL_ALIGN_FILL));
		applyDialogFont(composite);
		return composite;
	}

	protected void buttonPressed(int buttonId) {
		if (buttonId == IDialogConstants.OK_ID) {
			userid = useridText.getText();
			passwd = passwordText.getText();
			filename = fileLocation.getText();
			File f = new File(filename);
			if (f.exists()) {
				if (MessageDialog.openQuestion(getShell(), Messages.getString("StartFileDownloadDialog.FILE_EXISTS_TITLE"), NLS.bind(Messages.getString("StartFileDownloadDialog.FILE_EXISTS_MESSAGE"), filename))) { //$NON-NLS-1$ //$NON-NLS-2$
					super.buttonPressed(buttonId);
				}
				fileLocation.setFocus();
				return;
			}
		}
		super.buttonPressed(buttonId);
	}
}