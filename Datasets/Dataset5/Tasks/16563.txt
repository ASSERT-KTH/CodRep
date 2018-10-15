public String getAccountCreationInstructions() throws ECFException;

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
package org.eclipse.ecf.presence;

import java.util.Map;

import org.eclipse.ecf.core.util.ECFException;

/**
 * Presence account management. Access to instances implementing this interface
 * is provided by calling {@link IPresenceContainerAdapter#getAccountManager()}
 * 
 * @see IPresenceContainerAdapter
 */
public interface IAccountManager {

	/**
	 * Change account password to use new password. Upon next authenticated
	 * login, new password will be required for accessing account
	 * 
	 * @param newpassword
	 *            new password to use for this account
	 * @return true if password changed, false if not changed
	 * @throws ECFException
	 *             thrown if not connected, or if password change fails due to
	 *             network failure or server failure
	 */
	public boolean changePassword(String newpassword) throws ECFException;

	/**
	 * Determine whether account creation is supported for this account manager
	 * 
	 * @return true if account creation supported, false otherwise
	 * @throws ECFException
	 *             thrown if not connected, or if query fails due to network
	 *             failure or server failure
	 */
	public boolean isAccountCreationSupported() throws ECFException;

	/**
	 * Create a new account. Create a new account using given username,
	 * password, and attributes. If account creation succeeds, the method will
	 * return successfully. If fails, or is not supported, ECFException will be
	 * thrown
	 * 
	 * @param username
	 *            the fully qualified username to use for the new account
	 * @param password
	 *            the password to use with the new account
	 * @param attributes
	 *            attributes to associate with the new account
	 * @return true if account created, false if not created
	 * @throws ECFException
	 *             thrown if account creation is not supported, or if fails for
	 *             some reason (network failure or server failure)
	 */
	public boolean createAccount(String username, String password,
			Map attributes) throws ECFException;

	/**
	 * Delete an account. Deletes this account. If successful deletion, the
	 * method will return successfully. If account deletion is not supported,
	 * network failure, or some server error then an ECFException will be
	 * thrown.
	 * 
	 * @return true if account deleted, false if not deleted
	 * @throws ECFException
	 *             thrown if account deletion is not supported, or if fails for
	 *             some reason (network failure or server failure)
	 */
	public boolean deleteAccount() throws ECFException;

	/**
	 * Get any instructions for account
	 * 
	 * @return instructions for account
	 * @throws ECFException
	 *             thrown if account account instructions not supported, or if
	 *             fails for some reason (network failure or server failure)
	 */
	public String getAccountInstructions() throws ECFException;

	/**
	 * Get account attribute names for this account
	 * 
	 * @return String[] attribute names. Will return empty array if no attribute
	 *         names for account.
	 * @throws ECFException
	 *             thrown if get account attribute names not supported, or if
	 *             fails for some reason (network failure or server failure)
	 */
	public String[] getAccountAttributeNames() throws ECFException;

	/**
	 * Get the value of given
	 * 
	 * @param attributeName
	 *            the attribute name to return the value for
	 * @return Object value for the given attribute
	 * @throws ECFException
	 *             thrown if get account attribute not supported, or if fails
	 *             for some reason (network failure or server failure)
	 */
	public Object getAccountAttribute(String attributeName) throws ECFException;
}