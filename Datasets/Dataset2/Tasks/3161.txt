POP3Protocol pop3Connection = new POP3Protocol(accountItem.getPopItem().get("host"), accountItem.getPopItem().getInteger("port"));

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
//(the "License"); you may not use this file except in compliance with the
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.smtp;

import java.net.UnknownHostException;

import org.columba.addressbook.parser.AddressParser;
import org.columba.core.command.StatusObservable;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.IdentityItem;
import org.columba.mail.config.ImapItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.config.SmtpItem;
import org.columba.mail.config.SpecialFoldersItem;
import org.columba.mail.gui.util.PasswordDialog;
import org.columba.ristretto.pop3.protocol.POP3Protocol;
import org.columba.ristretto.progress.ProgressObserver;
import org.columba.ristretto.smtp.SMTPProtocol;

/**
 * @author fdietz
 * 
 * SMTPServer makes use of <class>SMTPProtocol</class> to add a higher
 * abstraction layer for sending messages.
 * 
 * It takes care of authentication all the details.
 * 
 * To send a message just create a <class>SendableMessage</class> object and
 * use <method>sendMessage</method>.
 * 
 *  
 */
public class SMTPServer {

	protected SMTPProtocol smtpProtocol;
	protected AccountItem accountItem;
	protected IdentityItem identityItem;
	protected String fromAddress;

	protected Object observer;

	/**
	 * Constructor for SMTPServer.
	 */
	public SMTPServer(AccountItem accountItem) {
		super();

		this.accountItem = accountItem;

		identityItem = accountItem.getIdentityItem();
	}

	/**
	 * Open connection to SMTP server and login if needed.
	 * 
	 * @return true if connection was successful, false otherwise
	 */
	public boolean openConnection() {
		String username;
		String password;
		String method;

		int smtpMode;
		boolean authenticate;
		boolean cont = false;

		PasswordDialog passDialog = new PasswordDialog();

		// Init Values

		// user's email address
		fromAddress = identityItem.get("address");

		// POP3 server host name
		SmtpItem smtpItem = accountItem.getSmtpItem();
		String host = smtpItem.get("host");

		// Sent Folder
		SpecialFoldersItem specialFoldersItem =
			accountItem.getSpecialFoldersItem();
		Integer i = new Integer(specialFoldersItem.get("sent"));
		int sentFolder = i.intValue();

		String authType = accountItem.getSmtpItem().get("login_method");
		authenticate = !authType.equals("NONE");

		boolean popbeforesmtp = false;
		if (authType.equalsIgnoreCase("POP before SMTP"))
			popbeforesmtp = true;

		if (popbeforesmtp) {
			// no esmtp - use POP3-before-SMTP instead
			try {
				pop3Authentification();
			} catch (Exception e) {
				if (e instanceof UnknownHostException) {
					Exception ex =
						new Exception(
							"Unknown host: "
								+ e.getMessage()
								+ "\nAre you  online?");
					NotifyDialog dialog = new NotifyDialog();
					dialog.showDialog(ex);

				} else {
					NotifyDialog dialog = new NotifyDialog();
					dialog.showDialog(e);
				}

				return false;
			}
		}

		// initialise protocol layer
		try {
			smtpProtocol =
				new SMTPProtocol(
					host,
					smtpItem.getInteger("port"),
					smtpItem.getBoolean("enable_ssl", true));

			// add observable
			setObservable(new StatusObservableImpl());

		} catch (Exception e) {
			if (e instanceof UnknownHostException) {
				Exception ex =
					new Exception(
						"Unknown host: "
							+ e.getMessage()
							+ "\nAre you  online?");

			} else {
				NotifyDialog dialog = new NotifyDialog();
				dialog.showDialog(e);
			}

			return false;
		}

		// Start login procedure
		try {

			smtpMode = smtpProtocol.openPort();
		} catch (Exception e) {
			NotifyDialog dialog = new NotifyDialog();
			dialog.showDialog(e);

			return false;
		}

		if ((authenticate) && (popbeforesmtp == false)) {
			username = accountItem.getSmtpItem().get("user");
			password = accountItem.getSmtpItem().get("password");
			method = accountItem.getSmtpItem().get("login_method");

			if (username.length() == 0) {
				// there seems to be no username set in the smtp-options
				//  -> use username from pop3 or imap options
				if (accountItem.isPopAccount()) {

					PopItem pop3Item = accountItem.getPopItem();
					username = pop3Item.get("user");
				} else {
					ImapItem imapItem = accountItem.getImapItem();
					username = imapItem.get("user");
				}

			}

			// ask password from user
			if (password.length() == 0) {

				passDialog.showDialog(
					accountItem.getSmtpItem().get("user"),
					accountItem.getSmtpItem().get("host"),
					password,
					accountItem.getSmtpItem().getBoolean("save_password"));

				if (passDialog.success()) {
					password = new String(passDialog.getPassword());

				} else {
					return false;
				}

			}

			// try to authenticate
			while (!cont) {

				cont = true;

				try {
					smtpProtocol.authenticate(username, password, method);
				} catch (Exception e) {
					cont = false;

					passDialog.showDialog(
						accountItem.getSmtpItem().get("user"),
						accountItem.getSmtpItem().get("host"),
						password,
						accountItem.getSmtpItem().getBoolean("save_password"));

					if (!passDialog.success())
						return false;
					else {

						password = new String(passDialog.getPassword());

					}

				}
			}

			// authentication was successful
			// -> save name/password
			accountItem.getSmtpItem().set("user", username);
			accountItem.getSmtpItem().set("password", password);
			accountItem.getSmtpItem().set(
				"save_password",
				passDialog.getSave());

		}

		return true;
	}

	/**
	 * 
	 * close the connection to the SMTP server
	 *  
	 */
	public void closeConnection() {
		// Close Port

		try {
			smtpProtocol.closePort();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * 
	 * POP-before-SMTP authentication makes use of the POP3 authentication
	 * mechanism, before sending mail.
	 * 
	 * Basically you authenticate with the POP3 server, which allows you to use
	 * the SMTP server for sending mail for a specific amount of time.
	 * 
	 * @throws Exception
	 */
	protected void pop3Authentification() throws Exception {
		String password = new String("");
		//String user = "";
		String method = new String("");
		boolean save = false;
		boolean login = false;
		boolean cancel = false;
		PopItem item = accountItem.getPopItem();
		PasswordDialog dialog = null;

		// try to login until success or user cancels authentication
		while (!login && !cancel) {
			if (item.get("password").length() == 0) {

				// open password dialog
				dialog = new PasswordDialog();

				dialog.showDialog(
					accountItem.getPopItem().get("user"),
					accountItem.getPopItem().get("host"),
					password,
					accountItem.getPopItem().getBoolean("save_password"));

				char[] name;

				if (dialog.success()) {
					// ok pressed
					name = dialog.getPassword();
					password = new String(name);

					save = dialog.getSave();

					cancel = false;
				} else {
					// cancel pressed
					cancel = true;
				}
			} else {
				password = item.get("password");

				save = item.getBoolean("save_password");

			}

			if (!cancel) {

				// authenticate
				POP3Protocol pop3Connection = new POP3Protocol();
				// open socket, query for host
				pop3Connection.openPort();

				pop3Connection.setLoginMethod(method);
				login = pop3Connection.login(item.get("user"), password);

				if (!login) {
					NotifyDialog d = new NotifyDialog();
					d.showDialog("Authentification failed");

					item.set("password", "");
				}
			}
		}

		// logged in successfully
		// -> save password in config file
		if (login) {

			item.set("save_password", save);
			item.set("login_method", method);

			if (save) {
				// save plain text password in config file
				// this is a security risk !!!
				item.set("password", password);
			}
		}
	}

	/**
	 * Send a message
	 * 
	 * For an complete example of creating a <class>SendableMessage</class>
	 * object see <class>MessageComposer</class>
	 * 
	 * @param message
	 * @param workerStatusController
	 * @throws Exception
	 */
	public void sendMessage(
		SendableMessage message,
		WorkerStatusController workerStatusController)
		throws Exception {

		// send from address and recipient list to SMTP server
		// ->all addresses have to be normalized
		smtpProtocol.setupMessage(
			AddressParser.normalizeAddress(fromAddress),
			message.getRecipients());

		// now send message source
		smtpProtocol.sendMessage(message.getSourceStream());
	}

	/**
	 * @return status notification observable
	 */
	public StatusObservable getObservable() {
		return (StatusObservable) observer;
	}

	public void setObservable(ProgressObserver observable) {
		observer = observable;
		smtpProtocol.registerInterest(observable);
	}
}