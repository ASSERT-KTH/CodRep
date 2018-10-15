cachePassword(page.getPasswordKeyFromUserName(connectID),password);

/****************************************************************************
 * Copyright (c) 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *    Scott Lewis <slewis@composent.com>
 *****************************************************************************/
package org.eclipse.ecf.internal.irc.ui.wizards;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.internal.irc.ui.IRCUI;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.ui.IConnectWizard;
import org.eclipse.ecf.ui.actions.AsynchContainerConnectAction;
import org.eclipse.ecf.ui.dialogs.IDCreateErrorDialog;
import org.eclipse.ecf.ui.util.PasswordCacheHelper;
import org.eclipse.jface.wizard.Wizard;
import org.eclipse.ui.IWorkbench;

public final class IRCConnectWizard extends Wizard implements IConnectWizard {

	public static final String DEFAULT_GUEST_USER = "guest";
	
	private IRCConnectWizardPage page;

	private IContainer container;

	private ID targetID;

	private IConnectContext connectContext;

	private String authorityAndPath = null;

	public IRCConnectWizard() {
		super();
	}

	public IRCConnectWizard(String authorityAndPart) {
		super();
		this.authorityAndPath = authorityAndPart;
	}

	public void addPages() {
		page = new IRCConnectWizardPage(authorityAndPath);
		addPage(page);
	}

	public void init(IWorkbench workbench, IContainer container) {
		this.container = container;
	}

	public boolean performFinish() {
		
		final String connectID = page.getConnectID();
		final String password = page.getPassword();
		
		connectContext = ConnectContextFactory
				.createPasswordConnectContext(password);

		page.saveComboText();
		
		try {
			targetID = IDFactory.getDefault().createID(
					container.getConnectNamespace(), connectID);
		} catch (IDCreateException e) {
			new IDCreateErrorDialog(null,connectID,e).open();
			return false;
		}

		IChatRoomManager manager = (IChatRoomManager) this.container
				.getAdapter(IChatRoomManager.class);

		IRCUI ui = new IRCUI(this.container, manager, null);
		ui.showForTarget(targetID);
		// If it's not already connected, then we connect this new container
		if (!ui.isContainerConnected()) {
			page.saveComboItems();
			new AsynchContainerConnectAction(container, targetID, connectContext, null, new Runnable() {
				public void run() {
					cachePassword(connectID,password);
				}}).run();

		}


		return true;
	}

	protected void cachePassword(final String connectID, String password) {
		if (password != null && !password.equals("")) {
			PasswordCacheHelper pwStorage = new PasswordCacheHelper(connectID);
			pwStorage.savePassword(password);
		}
	}
	
}