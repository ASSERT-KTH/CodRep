package org.eclipse.ecf.internal.provider.bittorrent.ui;

/****************************************************************************
 * Copyright (c) 2007 Remy Suen and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.msn.ui;

import java.io.File;

import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

final class BitTorrentConnectWizardPage extends WizardPage {

	private Text torrentText;

	private Text targetText;

	private Button browseTorrentBtn;

	private Button browseTargetBtn;

	BitTorrentConnectWizardPage() {
		super("");
		setTitle("BitTorrent File Sharing");
		setPageComplete(false);
	}

	private void addListeners() {
		torrentText.addModifyListener(new ModifyListener() {
			public void modifyText(ModifyEvent e) {
				String file = torrentText.getText().trim();
				if (file.equals("")) { //$NON-NLS-1$
					setErrorMessage("A torrent file must be entered.");
				} else {
					File torrent = new File(file);
					if (torrent.isDirectory()) {
						setErrorMessage("The path is mapped to a directory.");
					} else if (!torrent.canRead()) {
						setErrorMessage("The file cannot be read.");
					} else {
						setErrorMessage(null);
					}
				}
			}
		});

		browseTorrentBtn.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				FileDialog dialog = new FileDialog(browseTorrentBtn.getShell(),
						SWT.OPEN);
				dialog.setFilterExtensions(new String[] { "*.torrent" }); //$NON-NLS-1$
				String torrent = dialog.open();
				if (torrent != null) {
					torrentText.setText(torrent);
				}
			}
		});

		browseTargetBtn.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				FileDialog dialog = new FileDialog(browseTorrentBtn.getShell(),
						SWT.OPEN);
				String target = dialog.open();
				if (target != null) {
					targetText.setText(target);
				}
			}
		});
	}

	public void createControl(Composite parent) {
		parent.setLayout(new GridLayout(3, false));

		GridData data = new GridData(SWT.FILL, SWT.CENTER, true, false);

		Label label = new Label(parent, SWT.LEFT);
		label.setText("Torrent:");

		torrentText = new Text(parent, SWT.SINGLE | SWT.BORDER);
		torrentText.setLayoutData(data);

		browseTorrentBtn = new Button(parent, SWT.PUSH);
		browseTorrentBtn.setText("&Browse");

		label = new Label(parent, SWT.LEFT);
		label.setText("Target Path:");

		targetText = new Text(parent, SWT.SINGLE | SWT.BORDER);
		targetText.setLayoutData(data);

		browseTargetBtn = new Button(parent, SWT.PUSH);
		browseTargetBtn.setText("B&rowse");

		addListeners();
		setControl(parent);
	}

	String getTorrentName() {
		return torrentText.getText();
	}

	String getTargetName() {
		return targetText.getText();
	}

	public void setErrorMessage(String message) {
		super.setErrorMessage(message);
		setPageComplete(message == null);
	}

}