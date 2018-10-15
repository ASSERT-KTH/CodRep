return "ecftcp://<server>:<port>/<groupname>";

/****************************************************************************
 * Copyright (c) 2006 Remy Suen, Composent, Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.provider.ui.wizards;

import org.eclipse.ecf.ui.wizards.AbstractConnectWizardPage;

public class GenericClientContainerConnectWizardPage extends AbstractConnectWizardPage {

	public boolean shouldRequestUsername() {
		return true;
	}

	public boolean shouldRequestPassword() {
		return true;
	}

	public String getExampleID() {
		return "<protocol>://<machinename>:<port>/<servicename>";
	}

	protected String getProviderTitle() {
		return "ECF Generic Client Connection";
	}

	protected String getProviderDescription() {
		return "Creates a connection to the specified ECF Generic Server.";
	}

}