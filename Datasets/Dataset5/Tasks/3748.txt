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


public final class XMPPSConnectWizard extends XMPPConnectWizard {

	public void addPages() {
		page = new XMPPSConnectWizardPage();
		addPage(page);
	}

}