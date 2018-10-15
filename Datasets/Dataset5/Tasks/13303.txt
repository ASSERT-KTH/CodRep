private AccountManager accountManager = null;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.xmpp;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.IAccountManager;
import org.jivesoftware.smack.AccountManager;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.XMPPException;

public class XMPPContainerAccountManager implements IAccountManager {

	private static final String NOT_CONNECTED = "not connected";

	AccountManager accountManager = null;

	protected void traceAndThrow(String msg, Throwable t) throws ECFException {
		throw new ECFException(msg, t);
	}

	protected AccountManager getAccountManagerOrThrowIfNull()
			throws ECFException {
		if (accountManager == null)
			throw new ECFException(NOT_CONNECTED);
		return accountManager;
	}

	public XMPPContainerAccountManager() {
	}

	public void dispose() {
		accountManager = null;
	}

	public void setConnection(XMPPConnection connection) {
		this.accountManager = (connection == null) ? null : new AccountManager(
				connection);
	}

	public boolean changePassword(String newpassword) throws ECFException {
		try {
			getAccountManagerOrThrowIfNull().changePassword(newpassword);
		} catch (XMPPException e) {
			traceAndThrow("server exception changing password", e);
		}
		return true;
	}

	public boolean createAccount(String username, String password,
			Map attributes) throws ECFException {
		try {
			getAccountManagerOrThrowIfNull().createAccount(username, password,
					attributes);
		} catch (XMPPException e) {
			traceAndThrow("server exception creating account for " + username,
					e);
		}
		return true;
	}

	public boolean deleteAccount() throws ECFException {
		try {
			getAccountManagerOrThrowIfNull().deleteAccount();
		} catch (XMPPException e) {
			traceAndThrow("server exception deleting account", e);
		}
		return true;
	}

	public String getAccountCreationInstructions() {
		if (accountManager == null)
			return "";
		return accountManager.getAccountInstructions();
	}

	public String[] getAccountAttributeNames() {
		if (accountManager == null)
			return new String[0];
		Iterator i = accountManager.getAccountAttributes();
		List l = new ArrayList();
		for (; i.hasNext();) {
			l.add(i.next());
		}
		return (String[]) l.toArray(new String[] {});
	}

	public Object getAccountAttribute(String name) {
		if (accountManager == null)
			return null;
		return accountManager.getAccountAttribute(name);
	}

	public boolean isAccountCreationSupported() {
		if (accountManager == null)
			return false;
		return accountManager.supportsAccountCreation();
	}

}