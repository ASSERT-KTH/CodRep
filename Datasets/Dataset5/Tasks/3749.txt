package org.eclipse.ecf.internal.provider.xmpp.ui;

/****************************************************************************
 * Copyright (c) 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.provider.xmpp.ui.wizards;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

final class XMPPSConnectWizardPage extends XMPPConnectWizardPage {

	XMPPSConnectWizardPage() {
		super();
		setTitle("XMPPS Connection Wizard");
		setDescription("Specify a XMPP account to connect to.");
		setPageComplete(false);
	}

	public void createControl(Composite parent) {
		parent.setLayout(new GridLayout());
		GridData fillData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		GridData endData = new GridData(SWT.FILL, SWT.CENTER, true, false, 2, 1);

		Label label = new Label(parent, SWT.LEFT);
		label.setText("User ID:");

		connectText = new Text(parent, SWT.SINGLE | SWT.BORDER);
		connectText.setLayoutData(fillData);
		connectText.addModifyListener(new ModifyListener() {
			public void modifyText(ModifyEvent e) {
				if (!connectText.getText().equals("")) { //$NON-NLS-1$
					updateStatus(null);
				} else {
					updateStatus("An connect ID must be specified.");
				}
			}
		});

		label = new Label(parent, SWT.RIGHT);
		label.setText("<user>@<xmppserver>[:port]");
		label.setLayoutData(endData);

		label = new Label(parent, SWT.LEFT);
		label.setText("Password:");
		passwordText = new Text(parent, SWT.SINGLE | SWT.PASSWORD | SWT.BORDER);
		passwordText.setLayoutData(fillData);

		setControl(parent);
	}

}