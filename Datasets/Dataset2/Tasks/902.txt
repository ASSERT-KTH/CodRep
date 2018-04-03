dialog.showDialog( "PGP-"+item.get("id"), "", false);

//The contents of this file are subject to the Mozilla Public License Version 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.
package org.columba.mail.pgp;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

import javax.swing.JOptionPane;

import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.config.PGPItem;
import org.columba.mail.gui.util.PasswordDialog;

public class PGPController {
	public final static int GPG = 0;
	public final static int PGP2 = 1;
	public final static int PGP5 = 2;
	public final static int PGP6 = 3;

	public final static int DECRYPT_ACTION = 0;
	public final static int ENCRYPT_ACTION = 1;
	public final static int SIGN_ACTION = 2;
	public final static int VERIFY_ACTION = 3;
	public final static int ENCRYPTSIGN_ACTION = 4;

	private int type;
	private String path;
	private String id;
	private int exitVal;

	private boolean save = false;

	private static PGPController myInstance;

	private String pgpMessage;
	
	private Map passwords;
	
	/**
	 * here are the utils, from which you can sign, verify, encrypt and decrypt messages
	 * at the moment there are only one tool - gpg, the gnu pgp programm which
	 * comes with an commandline tool to do things with your pgp key
	 * @see DefaultUtil
	 */
	private DefaultUtil[] utils = { new GnuPGUtil(),
		// Enter new DefaultUtils here
	};
	/**
	 * The default constructor for this class. The exit value is default 0
	 */
	protected PGPController() {
		exitVal = 0;
		
		passwords = new HashMap();
	}
	/**
	 * Gives back an Instance of PGPController. This function controls, that only
	 * one Instance is created in on columba session. If never before an Instance
	 * is created, an Instance of Type PGPController is created and returned. Is
	 * there is alrady an Instance, this instance is returned.
	 * @return PGPController a new PGPController if there is no one created in one
	 * columba session, or an alrady existing PGPConstroller, so only one Controller
	 * is used in one columba session.
	 */
	public static PGPController getInstance() {
		if (myInstance == null)
			myInstance = new PGPController();
		ColumbaLogger.log.debug(myInstance.toString());
		return myInstance;
	}

	/**
	 * gives the return value from the pgp-program back. This can used for
	 * controlling errors when signing ... messages
	 * @return int exitValue, 0 means all ok, all other exit vlaues identifying errors
	 */
	public int getReturnValue() {
		return exitVal;
	}

	public InputStream decrypt(InputStream cryptMessage, PGPItem item)
		throws PGPException {

		int exitVal = -1;

		this.getPassphrase(item);

		String error = null;
		String output = null;
		try {
			exitVal = utils[GPG].decrypt(item, cryptMessage);

			error = utils[GPG].parse(utils[GPG].getErrorString());
		} catch (Exception e) {
			e.printStackTrace();

			throw new PGPException(error);
		}
		
		pgpMessage = new String(error);
		
		if ( exitVal == 2 ) throw new WrongPassphraseException(error);
		
		return utils[GPG].getStreamResult();
	}
	/**
	 * Verify a given message with a given signature. Can the signature for the given message be verified the method
	 * returns true, elso false. The given item should holding the path to the pgp-tool. While gpg dosn't yet supporting
	 * a real stream based process to verify a given detached signature with a message the method creates a temporary
	 * file which holds the signature. After the verify process the temporary file is deleted.
	 * @param item PGPItem wich should holding the path to the pgp-tool
	 * @param message The message for wich the given signature should be verify.
	 * @param signature Signature wich should be verify for the given message.
	 * @return true if the signature can be verify for the given message, else false.
	 */
	public void verifySignature(
		InputStream message,
		InputStream signature,
		PGPItem item)
		throws PGPException {

		int exitVal = -1;
		String error = null;
		String output = null;
		try {
			exitVal = utils[GPG].verify(item, message, signature);

			error = utils[GPG].parse(utils[GPG].getErrorString());

		} catch (Exception e) {
			e.printStackTrace();

			throw new PGPException(error);
		}

		pgpMessage = error;
		
		if ( exitVal == 1 ) throw new VerificationException(error);
		
		if (exitVal == 2)
			throw new MissingPublicKeyException(error);

	}
	/** 
	 * Encryptes a given message  and returnes the encrypted Stream. The given pgp-item should have a entry with
	 * all recipients seperated via space. The entry is called recipients. If an error occurse the error result is
	 * shown to the user via a dialog.
	 * @param message The message to be encrypt
	 * @param item the item which holds information like path to pgp-tool and recipients for which the message should be
	 * encrypted.
	 * @return the encrypted message if all is ok, else an empty input-stream
	 * TODO better using the exception mechanism instead of showing th user a dialog from this component.
	 */
	public InputStream encrypt(InputStream message, PGPItem item) {
		int exitVal = -1;
		
		this.getPassphrase(item);
		
		try {
			exitVal = utils[GPG].encrypt(item, message);
		} catch (Exception e) {
			JOptionPane.showMessageDialog(null, utils[GPG].getErrorString());
		}
		return utils[GPG].getStreamResult();
	}

	/**
	 * signs an message and gives the signed message as an InputStream back to the application. This method call the 
	 * GPG-Util to sign the message. if the passphrase is currently not stored in the PGPItem the user is called for
	 * a new passphrase. If the user dosn't give a passphrase (he cancel the dialog) the method returns null.
	 * The Util (in this case GPG is called to sign the message with the user-id. The exit-value from the sign-process is
	 * stored in the global exit value. In the case, that the exit-value is 2 then the error-message from the gpg-program is 
	 * printed to the user in an dialog. The value null is then returned. 
	 * If the value is equal to 1 null is returned. If an exception occurrs, the exception-message is shown to the
	 * user in a dialog and null is returned.
	 * @param pgpMessage the message that is to signed
	 * @param item the item wich holds the userid for the pgp key. Eventual the passphrase is also stored in the item. Then
	 * stored passphrase is used.
	 * @return The signed message as an InputStream. Null, when
	 * an error occurse or the exit-value is not equal to 0 from the whole gpg-util is returned.
	 */
	public InputStream sign(InputStream pgpMessage, PGPItem item) {
		exitVal = -1;
		path = item.get("path");
		id = item.get("id");

		this.getPassphrase(item);
		try {
			exitVal = utils[GPG].sign(item, pgpMessage);
		} catch (Exception ex) {
			ex.printStackTrace();
			JOptionPane.showMessageDialog(null, utils[GPG].getErrorString());
		}
		if (save == false) {
			item.clearPassphrase();
		}
		return utils[GPG].getStreamResult();
	}

	/**
	 * signs an message and gives the signed message string back to the application. This method call the GPG-Util to sign 
	 * the message. If no passphrase is given, an empty String is returned. If the passphrase String
	 * has an length > 0, a new Passphrase-Dialog is opend and asked the user for
	 * input the password for his key. The Util (in this case GPG is called to
	 * sign the message with the user-id. The exit-value from the sign-process is
	 * stored in the global exit value. In the case, that the exit-value is 2 then
	 * the error-message from the gpg-program is printed to the user in an dialog.
	 * The value null is then returned. If the value is equal to 1 null is
	 * returned. If an exception occurrs, the exception-message is shown to the
	 * user in dialog and null is returned
	 * @param pgpMessage the message that is to signed
	 * @param item the item wich holds the passphrase (the userid for the pgp key)
	 * @return String the signed message with the sign string inside. Null, when
	 * an error or an exit-value not equal 0 from the whole gpg-util is returned
	 * @deprecated After ristretto is used in columba only Streams instead of Strings supported. Use 
	 * sign(InputStream message, PGPItem item). 
	 */
	public String sign(String pgpMessage, PGPItem item) {
		exitVal = -1;
		// this is, if we have more then one pgp-type
		//type = item.getInteger("type");
		path = item.get("path");
		id = item.get("id");

		if (!this.getPassphrase(item)) {
			return null;
		}

		try {
			ColumbaLogger.log.debug("pgpmessage: !!" + pgpMessage + "!!");
			exitVal = utils[GPG].sign(item, pgpMessage);
			if (!checkError(exitVal, item)) {
				return null;
			}

		} catch (Exception ex) {
			ex.printStackTrace();
			JOptionPane.showMessageDialog(null, utils[GPG].getErrorString());
			if (save == false)
				item.clearPassphrase();
			return null;
		}

		if (save == false)
			item.clearPassphrase();
		ColumbaLogger.log.debug(utils[GPG].getResult());
		return utils[GPG].getResult();
	}

	private boolean getPassphrase(PGPItem item) {
		String passphrase = item.getPassphrase();
		boolean save = false;
		boolean ret = false;

		PasswordDialog dialog = new PasswordDialog();
		if (passphrase.length() == 0) {
			//PGPPassphraseDialog dialog = new PGPPassphraseDialog(id, false);
			
			dialog.showDialog(item.get("id"), "", false);
			
			if (dialog.success()) {				
				passphrase =
					new String(
						dialog.getPassword(),
						0,
						dialog.getPassword().length);									
				item.setPassphrase(passphrase);
				save = dialog.getSave();
				ret = true;
			}
		}
		return ret;
	}

	private boolean checkError(int exitVal, PGPItem item) {
		boolean ret = true;
		if (exitVal == 2) {
			JOptionPane.showMessageDialog(null, utils[GPG].getErrorString());
			ret = false;
		}
		return ret;
	}

	/**
	 * Returnes the Result from the GPG Util as an InputStream. On each operation with the GPG Util this Stream is
	 *  overidden. The ResultStream can be empty if it has earliyer readed out.
	 * @return The Result from the GPG Util as an InputStream.
	 */
	public InputStream getPGPResultStream() {
		return utils[GPG].getStreamResult();
	}

	/**
	 * Returns the ErrorResult from the GPG Util as an InputStream. On each operation with the GPG Util this Stream is
	 *  overidden. The ResultStream can be empty if it has earliyer readed out.
	 * @return The ErrorResult from the GPG Util as an InputStream.
	 */
	public InputStream getPGPErrorStream() {
		return utils[GPG].getErrorStream();
	}

	/**
	 * Gets the pgp commandline output.
	 * 
	 * @return	output of the commandline
	 */
	public String getPgpMessage() {
		return pgpMessage;
	}

}