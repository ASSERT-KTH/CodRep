new Rfc822Parser().parse(decryptedBodyPart, null);

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
package org.columba.mail.gui.message.command;

import java.io.FileNotFoundException;
import java.util.LinkedList;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.config.PGPItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.attachment.AttachmentSelectionHandler;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;
import org.columba.mail.parser.Rfc822Parser;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 *
 */
public class ViewMessageCommand extends FolderCommand {

	MimePart bodyPart;
	MimePartTree mimePartTree;
	HeaderInterface header;
	Folder srcFolder;
	Object uid;
	Object[] uids;
	// true if we view an encrypted message
	boolean encryptedMessage = false;

	/**
	 * Constructor for ViewMessageCommand.
	 * @param references
	 */
	public ViewMessageCommand(
		AbstractFrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);

		//priority = Command.REALTIME_PRIORITY;
		commandType = Command.NORMAL_OPERATION;
	}

	protected void encryptMessage() {
		//		Example message:
		//
		//			  From: Michael Elkins <elkins@aero.org>
		//			  To: Michael Elkins <elkins@aero.org>
		//			  Mime-Version: 1.0
		//
		//			  Content-Type: multipart/encrypted; boundary=foo;
		//				 protocol="application/pgp-encrypted"
		//
		//			  --foo
		//			  Content-Type: application/pgp-encrypted
		//
		//			  Version: 1
		//
		//			  --foo
		//			  Content-Type: application/octet-stream
		//
		//			  -----BEGIN PGP MESSAGE-----
		//			  Version: 2.6.2
		//
		//			  hIwDY32hYGCE8MkBA/wOu7d45aUxF4Q0RKJprD3v5Z9K1YcRJ2fve87lMlDlx4Oj
		//			  eW4GDdBfLbJE7VUpp13N19GL8e/AqbyyjHH4aS0YoTk10QQ9nnRvjY8nZL3MPXSZ
		//			  g9VGQxFeGqzykzmykU6A26MSMexR4ApeeON6xzZWfo+0yOqAq6lb46wsvldZ96YA
		//			  AABH78hyX7YX4uT1tNCWEIIBoqqvCeIMpp7UQ2IzBrXg6GtukS8NxbukLeamqVW3
		//			  1yt21DYOjuLzcMNe/JNsD9vDVCvOOG3OCi8=
		//			  =zzaA
		//			  -----END PGP MESSAGE-----
		//
		//			  --foo--
		//			

		// get all MimeParts with contentType="application/octet-stream"
		LinkedList list =
			mimePartTree.getLeafsWithContentType(
				mimePartTree.getRootMimeNode(),
				"application/octet-stream");

		// get first one -> this is the one we need to decrypt
		MimePart mimePart = (MimePart) list.getFirst();

		// get encrypted string
		String encryptedBodyPart = mimePart.getBody();

		// get PGPItem, use To-headerfield and search through
		// all accounts to find a matching PGP id
		String to = (String) header.get("To");
		PGPItem pgpItem = MailConfig.getAccountList().getPGPItem(to);

		// decrypt string
		String decryptedBodyPart = "";
		//String decryptedBodyPart = PGPController.getInstance().decrypt(encryptedBodyPart, pgpItem);

		// construct new Message from decrypted string
		AbstractMessage message =
			new Rfc822Parser().parse(decryptedBodyPart, true, null, 0);

		mimePartTree = message.getMimePartTree();

		header = message.getHeader();
	}

	protected void verifyMessage() {
		//		Example message:
		//
		//				From: Michael Elkins <elkins@aero.org>
		//				To: Michael Elkins <elkins@aero.org>
		//				Mime-Version: 1.0
		//
		//				Content-Type: multipart/signed; boundary=bar; micalg=pgp-md5;
		//				  protocol="application/pgp-signature"
		//
		//				--bar
		//			 & Content-Type: text/plain; charset=iso-8859-1
		//			 & Content-Transfer-Encoding: quoted-printable
		//			 &
		//			 & =A1Hola!
		//			 &
		//			 & Did you know that talking to yourself is a sign of senility?
		//			 &
		//			 & It's generally a good idea to encode lines that begin with
		//			 & From=20because some mail transport agents will insert a greater-
		//			 & than (>) sign, thus invalidating the signature.
		//			 &
		//			 & Also, in some cases it might be desirable to encode any   =20
		//			 & trailing whitespace that occurs on lines in order to ensure  =20
		//			 & that the message signature is not invalidated when passing =20
		//			 & a gateway that modifies such whitespace (like BITNET). =20
		//			 &
		//			 & me
		//
		//			 --bar
		//
		//			 Content-Type: application/pgp-signature
		//
		//			 -----BEGIN PGP MESSAGE-----
		//			 Version: 2.6.2
		//
		//			 iQCVAwUBMJrRF2N9oWBghPDJAQE9UQQAtl7LuRVndBjrk4EqYBIb3h5QXIX/LC//
		//			 jJV5bNvkZIGPIcEmI5iFd9boEgvpirHtIREEqLQRkYNoBActFBZmh9GC3C041WGq
		//			 uMbrbxc+nIs1TIKlA08rVi9ig/2Yh7LFrK5Ein57U/W72vgSxLhe/zhdfolT9Brn
		//			 HOxEa44b+EI=
		//			 =ndaj
		//			 -----END PGP MESSAGE-----
		//
		//			 --bar--
		//			

		// The "&"s in the previous example indicate the portion of the data
		// over which the signature was calculated.
	}

	protected void handlePGPMessage(HeaderInterface header, Worker wsc) {
		String contentType = (String) header.get("Content-Type");

		// extract protocol key/value from contentType
		// example:
		//
		// Content-Type: multipart/encrypted; boundary=foo;
		//				 protocol="application/pgp-encrypted"
		//
		//

		// FIXME: little hack, need to do this right another time
		String protocolType = null;

		if (contentType.indexOf("pgp-encrypted") != -1)
			protocolType = "pgp-encrypted";
		else if (contentType.indexOf("pgp-signature") != -1)
			protocolType = "pgp-signature";

		if (protocolType.equals("pgp-encrypted")) {
			// RFC3156-conform encrypted message

			encryptMessage();

		} else if (protocolType.equals("pgp-signature")) {
			// RFC3156-conform signed message

			verifyMessage();
		}

	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {

		AttachmentSelectionHandler h =
			((AttachmentSelectionHandler) frameController
				.getSelectionManager()
				.getHandler("mail.attachment"));

		// show headerfields
		if (h != null)
			h.setMessage(srcFolder, uid);

		if (header != null && bodyPart != null) {
			(
			// show message in gui component
			(
				AbstractMailFrameController) frameController)
					.messageController
					.showMessage(
				header,
				bodyPart,
				mimePartTree);
				
				// TODO: cleanup markAsRead-Timer
				/*
			if (header.getFlags().getSeen() == false) {
				// restart timer which marks the message as read
				// after a user configurable time interval
				((AbstractMailFrameController) frameController)
					.tableController
					.getMarkAsReadTimer()
					.restart((FolderCommandReference) getReferences()[0]);
					
			}
			*/
		}
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker wsc) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		srcFolder = (Folder) r[0].getFolder();
		uid = r[0].getUids()[0];

		bodyPart = null;

		

		// get attachment structure
		try
		{	
			mimePartTree = srcFolder.getMimePartTree(uid, wsc);
		}
		catch ( FileNotFoundException ex)
		{
			// message doesn't exist anymore
			return;
		}
		
		//	get RFC822-header
		header = srcFolder.getMessageHeader(uid, wsc);

		// if this message is signed/encrypted we have to use
		// GnuPG to extract the decrypted bodypart
		//
		// we basically replace the Message object we
		// just got from Folder with the decrypted 
		// Message object, this includes header, bodyPart,
		// and mimePartTree

		// interesting for the PGP stuff are:
		// - multipart/encrypted
		// - multipart/signed
		String contentType = (String) header.get("Content-Type");
		ColumbaLogger.log.debug("contentType=" + contentType);

		if ((contentType != null ) && ((contentType.equals("multipart/encrypted"))
			|| (contentType.equals("multipart/signature"))))
			handlePGPMessage(header, wsc);

		if (mimePartTree != null) {

			// user prefers html/text messages
			XmlElement html =
				MailConfig.getMainFrameOptionsConfig().getRoot().getElement(
					"/options/html");
			boolean viewhtml =
				new Boolean(html.getAttribute("prefer")).booleanValue();

			// Which Bodypart shall be shown? (html/plain)

			if (viewhtml)
				bodyPart = mimePartTree.getFirstTextPart("html");
			else
				bodyPart = mimePartTree.getFirstTextPart("plain");

			if (bodyPart == null) {
				bodyPart = new MimePart();
				bodyPart.setBody(new String("<No Message-Text>"));
			} else if (encryptedMessage == true) {

				// meaning, bodyPart already contains the correct
				// message bodytext

			} else {

				bodyPart =
					srcFolder.getMimePart(uid, bodyPart.getAddress(), wsc);
			}
		}
	}

}