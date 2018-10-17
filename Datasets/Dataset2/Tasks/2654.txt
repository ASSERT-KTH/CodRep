import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.pgp;

import javax.swing.JOptionPane;

import org.columba.mail.config.PGPItem;
import org.columba.mail.gui.util.PGPPassphraseDialog;
import org.columba.main.MainInterface;
import org.columba.core.logging.ColumbaLogger;

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

	private static PGPController myInstance;

/**
 * here are the utils, which you can sign, verify, encrypt and decrypt messages
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
 * @return int exitValue, 0 means all ok, all other exit vlaues identifys errors
 */
	public int getReturnValue() {
		return exitVal;
	}

	/**
	 * Method sign.
	 * @param pgpMessage
	 * @param item
	 * @return String
	 */
	/*
	public String decrypt(String pgpMessage, PGPItem item) {
		DefaultUtil util;
		exitVal = -1;
	
		type = item.getType();
		path = item.getPath();
		id = item.getId();
	
		String passphrase = item.getPassphrase();
		boolean save = false;
	
		if (passphrase.length() == 0) {
			PGPPassphraseDialog dialog = new PGPPassphraseDialog(id, false);
			//dialog.showDialog( id, false );
	
			if (dialog.success()) {
				passphrase =
					new String(
						dialog.getPassword(),
						0,
						dialog.getPassword().length);
	
				save = dialog.getSave();
	
			} else {
				return new String("");
			}
		}
	
		try {
			util = utils[type];
	
			exitVal = util.decrypt(path, pgpMessage, passphrase);
	
			if (exitVal == 2) {
				// unknown error
	
				JOptionPane.showMessageDialog(
					MainInterface.mainFrame,
					util.getErrorString());
				if (save == false)
					item.clearPassphrase();
	
				return null;
			} else if (exitVal == 1) {
				// this means: decrypted message successfully, but
				// was not able to verify the signature
	
				JOptionPane.showMessageDialog(
					MainInterface.mainFrame,
					"Couldn't verify signature: " + util.getErrorString());
	
				if (save == false)
					item.clearPassphrase();
				return null;
			}
	
		} catch (Exception ex) {
			ex.printStackTrace();
	
			JOptionPane.showMessageDialog(
				MainInterface.mainFrame,
				util.getErrorString());
	
			if (save == false)
				item.clearPassphrase();
	
			return null;
		}
	
		if (save == false)
			item.clearPassphrase();
	
		return util.getOutputString();
	}
	
	public String verify(
		String pgpMessage,
		String signatureString,
		PGPItem item) {
		//System.out.println("message file:\n"+ pgpMessage );
		//System.out.println("signature file:\n"+ signatureString );
	
		exitVal = -1;
	
		type = item.getType();
		path = item.getPath();
		id = item.getId();
	
		File outputFile;
	
		String passphrase = item.getPassphrase();
		boolean save = false;
	
		if ((passphrase.length() == 0)) {
			PGPPassphraseDialog dialog = new PGPPassphraseDialog(id, false);
			//dialog.showDialog( id, false );
	
			if (dialog.success()) {
				passphrase =
					new String(
						dialog.getPassword(),
						0,
						dialog.getPassword().length);
	
				save = dialog.getSave();
	
			} else {
				return new String("");
			}
		}
	
		try {
	
			util = load(type);
	
			exitVal =
				util.verify(path, pgpMessage, signatureString, passphrase);
	
			System.out.println("exitvalue: " + exitVal);
	
		} catch (Exception ex) {
			ex.printStackTrace();
	
			JOptionPane.showMessageDialog(
				MainInterface.mainFrame,
				util.getErrorString());
		}
	
		if (exitVal > 0) {
			// error
			String errorString = util.errorStream.getBuffer();
	
			JOptionPane.showMessageDialog(
				MainInterface.mainFrame,
				util.getErrorString());
		}
	
		if (save == false)
			item.clearPassphrase();
	
		return util.getOutputString();
	}
	
	public String encrypt(
		String pgpMessage,
		boolean signValue,
		Vector recipients,
		PGPItem item) {
		System.out.println("pgpcontroller->encrypt");
		exitVal = -1;
	
		type = item.getType();
		path = item.getPath();
		id = item.getId();
	
	
		String passphrase = item.getPassphrase();
		boolean save = false;
	
		if (passphrase.length() == 0) {
			PGPPassphraseDialog dialog = new PGPPassphraseDialog(id, false);
			//dialog.showDialog( id, false );
	
			if (dialog.success()) {
				passphrase =
					new String(
						dialog.getPassword(),
						0,
						dialog.getPassword().length);
	
				save = dialog.getSave();
			} else {
				return new String("");
			}
		}
	
		try {
			util = load(type);
	
			exitVal =
				util.encrypt(
					path,
					pgpMessage,
					passphrase,
					signValue,
					recipients,
					id);
	
			if (exitVal == 2) {
				JOptionPane.showMessageDialog(
					MainInterface.mainFrame,
					util.getErrorString());
				if (save == false)
					item.clearPassphrase();
	
				return null;
			} else if (exitVal == 1) {
	
				if (save == false)
					item.clearPassphrase();
				return null;
			}
	
		} catch (Exception ex) {
			ex.printStackTrace();
	
			JOptionPane.showMessageDialog(
				MainInterface.mainFrame,
				util.getErrorString());
	
			if (save == false)
				item.clearPassphrase();
	
			return null;
		}
	
		//        }
	
		if (save == false)
			item.clearPassphrase();
	
		// now read encrypted message from File
		StringBuffer strbuf = null;
		try {
			BufferedReader in =
				new BufferedReader(new FileReader(util.outputFile));
			String str;
			strbuf = new StringBuffer();
	
			while ((str = in.readLine()) != null) {
				strbuf.append(str + "\n");
			}
	
			System.out.println(
				"----------------------->encrpted message:\n" + strbuf);
			in.close();
	
			// delete tmp file
			util.outputFile.delete();
		} catch (IOException ex) {
			ex.printStackTrace();
		}
	
		return strbuf.toString();
	}
	
	*/
  
  /**
   * signs an message and gives the signed message string back to the
   * application. This method call the GPG-Util to sign the message. If no
   * passphrase is given, an empty String is returned. If the passphrase String
   * has an length > 0, a new Passphrase-Dialog is opend and asked the user for
   * input the password for his key. The Util (in this case GPG is called to
   * sign the message with the user-id. The exit-value from the sign-process is
   * stored in the global exit value. In the case, that the exit-value is 2 then
   * the error-message from the gpg-program is printed to the user in an dialog.
   * The value null is then returned. If the value is equal to 1 null is
   * returned. If an exception occurring, the exception-message is shown to the
   * user in dialog and null is returned
   * @param pgpMessage the message that is to signed
   * @param item the item wich holds the passphrase (the userid for the pgp key)
   * @return String the signed message with the sign string inside. Null, when
   * an error or an exit-value not equal 0 from the whole gpg-util is returned
   */
	public String sign(String pgpMessage, PGPItem item) {
		exitVal = -1;

		type = item.getInteger("type");
		path = item.get("path");
		id = item.get("id");

		String passphrase = item.getPassphrase();
		boolean save = false;

		if (passphrase.length() == 0) {
			PGPPassphraseDialog dialog = new PGPPassphraseDialog(id, false);
			//dialog.showDialog( id, false );

			if (dialog.success()) {
				passphrase = new String(dialog.getPassword(), 0, dialog.getPassword().length);
        item.setPassphrase(passphrase);
				save = dialog.getSave();
			} else {
				return new String("");
			}
		}

		try {
			exitVal = utils[GPG].sign(item, pgpMessage);

			if (exitVal == 2) {
				JOptionPane.showMessageDialog(null, utils[GPG].getErrorString());
				if (save == false)
					item.clearPassphrase();

				return null;
			} else if (exitVal == 1) {

				if (save == false)
					item.clearPassphrase();
				return null;
			}

		} catch (Exception ex) {
			ex.printStackTrace();

			JOptionPane.showMessageDialog(null, utils[GPG].getErrorString());

			if (save == false)
				item.clearPassphrase();

			return null;
		}

		//        }

		if (save == false)
			item.clearPassphrase();

		return utils[GPG].getResult();
	}

}