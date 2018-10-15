new JoinGroupWizardAction(getURI().toString()).run(null);

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

package org.eclipse.ecf.internal.example.collab.ui.hyperlink;

import java.net.URI;

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.internal.example.collab.actions.JoinGroupWizardAction;
import org.eclipse.ecf.ui.IConnectWizard;
import org.eclipse.ecf.ui.hyperlink.AbstractURLHyperlink;
import org.eclipse.jface.text.IRegion;

/**
 * 
 */
public class ECFGenericHyperlink extends AbstractURLHyperlink {

	/**
	 * Creates a new URL hyperlink.
	 * 
	 * @param region
	 * @param urlString
	 */
	public ECFGenericHyperlink(IRegion region, URI uri) {
		super(region, uri);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.ui.hyperlink.AbstractURLHyperlink#createConnectWizard()
	 */
	protected IConnectWizard createConnectWizard() {
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.ui.hyperlink.AbstractURLHyperlink#createContainer()
	 */
	protected IContainer createContainer() throws ContainerCreateException {
		return null;
	}

	public void open() {
		new JoinGroupWizardAction().run(null);
	}

}