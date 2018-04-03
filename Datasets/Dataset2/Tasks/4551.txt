header.set("columba.attachment", Boolean.TRUE);

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

package org.columba.mail.composer;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Date;
import java.util.Iterator;
import java.util.List;

import org.columba.addressbook.parser.ListParser;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.IdentityItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.config.PGPItem;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.message.PGPMimePart;
import org.columba.mail.message.SendableHeader;
import org.columba.mail.parser.text.HtmlParser;
import org.columba.ristretto.coder.EncodedWord;
import org.columba.ristretto.composer.MimeTreeRenderer;
import org.columba.ristretto.message.Address;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.MessageIDGenerator;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.RFC822Date;
import org.columba.ristretto.message.StreamableMimePart;
import org.columba.ristretto.message.io.CharSequenceSource;

public class MessageComposer {
	private ComposerModel model;

	private int accountUid;

	public MessageComposer(ComposerModel model) {

		this.model = model;
	}

	protected SendableHeader initHeader() {
		SendableHeader header = new SendableHeader();

		// RFC822 - Header

		if (model.getToList().size() > 0)
			header.set("To", ListParser.parse(model.getToList()));

		if (model.getCcList().size() > 0)
			header.set("Cc", ListParser.parse(model.getCcList()));

		if (model.getBccList().size() > 0)
			header.set("Bcc", ListParser.parse(model.getBccList()));

		header.set("Subject", EncodedWord.encode(model.getSubject(), Charset.forName(model.getCharsetName()), EncodedWord.QUOTED_PRINTABLE).toString());

		AccountItem item = model.getAccountItem();
		IdentityItem identity = item.getIdentityItem();

		header.set("From", identity.get("address"));
		header.set("X-Priority", model.getPriority());

		/*
		String priority = controller.getModel().getPriority();
		
		if (priority != null) {
			header.set("columba.priority", new Integer(priority));
		} else {
			header.set("columba.priority", new Integer(3));
		}
		*/

		header.set("Mime-Version", "1.0");

		String organisation = identity.get("organisation");
		if (organisation.length() > 0)
			header.set("Organisation", organisation);

		// reply-to
		String replyAddress = identity.get("reply_address");
		if (replyAddress.length() > 0)
			header.set("Reply-To", replyAddress);

		String messageID = MessageIDGenerator.generate();
		header.set("Message-ID", messageID);

		String inreply = model.getHeaderField("In-Reply-To");
		if (inreply != null)
			header.set("In-Reply-To", inreply);

		String references = model.getHeaderField("References");
		if (references != null)
			header.set("References", references);

		header.set(
			"X-Mailer",
			"Columba v" + org.columba.core.main.MainInterface.version);

		// shortFrom
		/*
		String shortFrom = model.getHeaderField("From");
		if (shortFrom != null) {
			if (shortFrom.indexOf("<") != -1) {
				shortFrom = shortFrom.substring(0, shortFrom.indexOf("<"));
				if (shortFrom.length() > 0) {
					if (shortFrom.startsWith("\""))
						shortFrom =
							shortFrom.substring(1, shortFrom.length() - 1);
					if (shortFrom.endsWith("\""))
						shortFrom =
							shortFrom.substring(0, shortFrom.length() - 1);
				}
		
			}
		
			header.set("columba.from", shortFrom);
		} else {
			header.set("columba.from", new String(""));
		}
		*/
		header.set("columba.from", new Address(identity.get("address")));

		// date
		Date date = new Date();
		header.set("columba.date", date);
		header.set("Date", RFC822Date.toString(date));

		return header;
	}

	private boolean needQPEncoding(String input) {

		for (int i = 0; i < input.length(); i++) {
			if (input.charAt(i) > 127)
				return true;
		}

		return false;
	}

	/**
	 * gives the signature for this Mail back. This signature is NOT a pgp-signature but a real mail-signature.
	 * @param item The item wich holds the signature-file
	 * @return The signature for the mail as a String. The Signature is character encoded with the caracter set from the 
	 * model
	 */
	protected String getSignature(IdentityItem item) {

		File file = new File(item.get("signature_file"));
		StringBuffer strbuf = new StringBuffer();
		try {
			BufferedReader in = new BufferedReader(new FileReader(file));
			/*
			BufferedReader in =
				new BufferedReader(
					new InputStreamReader(
						new FileInputStream(file),
						model.getCharsetName()));
					*/
			String str;

			while ((str = in.readLine()) != null) {
				strbuf.append(str + "\n");
			}

			in.close();
		} catch (IOException ex) {
			ex.printStackTrace();
			return "";
		}

		try {
			return new String(
				strbuf.toString().getBytes(),
				model.getCharsetName());
		} catch (UnsupportedEncodingException e) {
		}

		return null;
	}

	/*
		protected String getSignature(IdentityItem item) {
			
			File file = new File(item.getSignatureFile());
			StringBuffer strbuf = new StringBuffer();
			try {
				//BufferedReader in = new BufferedReader(new FileReader(file));
				BufferedReader in =
					new BufferedReader(
						new InputStreamReader(
							new FileInputStream(file),
							model.getCharsetName()));
				String str;
	
				while ((str = in.readLine()) != null) {
					strbuf.append(str + "\n");
				}
	
				in.close();
			} catch (IOException ex) {
				ex.printStackTrace();
				return "";
			}
	
			return strbuf.toString();
	
		}
	*/

	/**
	 * Composes a multipart/alternative mime part for the body of a message
	 * containing a text part and a html part.
	 * <br>
	 * This is to be used for sending html messages, when an alternative
	 * text part - to be read by users not able to read html - is required.
	 * <br>
	 * Pre-condition: It is assumed that the model contains a message
	 * in html format.
	 *  
	 * @return	The composed mime part for the message body
	 * @author	Karl Peder Olesen (karlpeder)
	 */
	private StreamableMimePart composeMultipartAlternativeMimePart() {

		// compose text part
		StreamableMimePart textPart = composeTextMimePart();

		// compose html part
		StreamableMimePart htmlPart = composeHtmlMimePart();

		// merge mimeparts and return
		LocalMimePart bodyPart =
			new LocalMimePart(new MimeHeader("multipart", "alternative"));
		bodyPart.addChild(textPart);
		bodyPart.addChild(htmlPart);

		return bodyPart;

	}

	/**
	 * Composes a text/html mime part from the body contained in
	 * the composer model. This could be for a pure html message or
	 * for the html part of a multipart/alternative.
	 * <br>
	 * If a signature is defined, it is added to the body.
	 * <br>
	 * Pre-condition: It is assumed that the model contains
	 * a html message.
	 * 
	 * @return	The composed text/html mime part
	 * @author	Karl Peder Olesen (karlpeder)
	 */
	private StreamableMimePart composeHtmlMimePart() {
		LocalMimePart bodyPart =
			new LocalMimePart(new MimeHeader("text", "html"));
		// Init Mime-Header with Default-Values (text/html)	

		// Set Default Charset or selected		
		String charsetName = model.getCharsetName();
		bodyPart.getHeader().putContentParameter("charset", charsetName);

		StringBuffer buf = new StringBuffer();
		String body = model.getBodyText();

		// insert link tags for urls and email addresses
		body = HtmlParser.substituteURL(body, false);
		body = HtmlParser.substituteEmailAddress(body, false);

		String lcase = body.toLowerCase(); // for text comparisons

		// insert document type decl.
		if (lcase.indexOf("<!doctype") == -1) {

			// TODO: Is 3.2 the proper version of html to refer to? 

			buf.append(
				"<!DOCTYPE HTML PUBLIC " + "\"-//W3C//DTD HTML 3.2//EN\">\r\n");

		}

		// insert head section with charset def.
		String meta =
			"<meta "
				+ "http-equiv=\"Content-Type\" "
				+ "content=\"text/html; charset="
				+ charsetName
				+ "\">";
		int pos = lcase.indexOf("<head");
		int bodyStart;
		if (pos == -1) {
			// add <head> section
			pos = lcase.indexOf("<html") + 6;
			buf.append(body.substring(0, pos));
			buf.append("<head>");
			buf.append(meta);
			buf.append("</head>");

			bodyStart = pos;

		} else {
			// replace <head> section
			pos = lcase.indexOf('>', pos) + 1;
			buf.append(body.substring(0, pos));
			buf.append(meta);

			// TODO: If existing meta tags are to be kept, code changes are necessary

			bodyStart = lcase.indexOf("</head");

		}

		// add rest of body until start of </body>
		int bodyEnd = lcase.indexOf("</body");
		buf.append(body.substring(bodyStart, bodyEnd));

		// add signature if defined
		AccountItem item = model.getAccountItem();
		IdentityItem identity = item.getIdentityItem();
		boolean appendSignature = identity.getBoolean("attach_signature");

		if (appendSignature == true) {
			String signature = getSignature(identity);

			if (signature != null) {
				buf.append("\r\n\r\n");

				// TODO: Should we take some action to ensure signature is valid html?

				buf.append(signature);
			}
		}

		// add the rest of the original body - and transfer back to body var.
		buf.append(body.substring(bodyEnd));
		body = buf.toString();

		// add encoding if necessary
		if (needQPEncoding(body))
			bodyPart.getHeader().setContentTransferEncoding("quoted-printable");

		// to allow empty messages
		if (body.length() == 0) {
			body = " ";
		}

		bodyPart.setBody(new CharSequenceSource(body));

		return bodyPart;
	}

	/**
	 * Composes a text/plain mime part from the body contained in
	 * the composer model. This could be for a pure text message or
	 * for the text part of a multipart/alternative.
	 * <br>
	 * If the model contains a html message, tags are stripped to 
	 * get plain text.
	 * <br>
	 * If a signature is defined, it is added to the body.
	 * 
	 * @return	The composed text/plain mime part
	 */
	private StreamableMimePart composeTextMimePart() {
		LocalMimePart bodyPart =
			new LocalMimePart(new MimeHeader("text", "plain"));
		// Init Mime-Header with Default-Values (text/plain)	

		// Set Default Charset or selected		
		String charsetName = model.getCharsetName();
		bodyPart.getHeader().putContentParameter("charset", charsetName);

		String body = model.getBodyText();

		/*
		 * *20030918, karlpeder* Tags are stripped if the model
		 * contains a html message (since we are composing
		 * a plain text message here.
		 */
		if (model.isHtml()) {
			body = HtmlParser.htmlToText(body);
		}

		AccountItem item = model.getAccountItem();
		IdentityItem identity = item.getIdentityItem();
		boolean appendSignature = identity.getBoolean("attach_signature");

		if (appendSignature == true) {
			String signature = getSignature(identity);

			if (signature != null) {
				body = body + "\r\n\r\n" + signature;

			}
		}

		if (needQPEncoding(body))
			bodyPart.getHeader().setContentTransferEncoding("quoted-printable");

		// to allow empty messages
		if (body.length() == 0) {
			body = " ";
		}

		bodyPart.setBody(new CharSequenceSource(body));

		return bodyPart;
	}

	public SendableMessage compose(WorkerStatusController workerStatusController)
		throws Exception {
		this.accountUid = model.getAccountItem().getUid();

		workerStatusController.setDisplayText("Composing Message...");

		MimeTreeRenderer renderer = MimeTreeRenderer.getInstance();
		SendableMessage message = new SendableMessage();
		StringBuffer composedMessage = new StringBuffer();

		SendableHeader header = initHeader();
		MimePart root = null;

		/*
		 * *20030921, karlpeder* The old code was (accidentially!?) modifying
		 * the attachment list of the model. This affects the composing
		 * when called a second time for saving the message after sending!
		 */
		//List mimeParts = model.getAttachments();

		List attachments = model.getAttachments();
		List mimeParts = new ArrayList();
		Iterator ite = attachments.iterator();
		while (ite.hasNext()) {
			mimeParts.add(ite.next());
		}

		// *20030919, karlpeder* Added handling of html messages
		StreamableMimePart body;
		if (model.isHtml()) {
			// compose message body as multipart/alternative

			XmlElement composerOptions =
				MailConfig.getComposerOptionsConfig().getRoot().getElement(
					"/options");
			XmlElement html = composerOptions.getElement("html");
			if (html == null) {
				html = composerOptions.addSubElement("html");
			}
			String multipart = html.getAttribute("send_as_multipart", "true");

			if (multipart.equals("true")) {
				// send as multipart/alternative
				body = composeMultipartAlternativeMimePart();
			} else {
				// send as text/html
				body = composeHtmlMimePart();
			}

		} else {
			// compose message body as text/plain
			body = composeTextMimePart();
		}

		if (body != null)
			mimeParts.add(0, body);

		// Create Multipart/Mixed if necessary
		if (mimeParts.size() > 1) {
			root = new MimePart(new MimeHeader("multipart", "mixed"));

			for (int i = 0; i < mimeParts.size(); i++) {
				root.addChild((StreamableMimePart) mimeParts.get(i));
			}
		} else {
			root = (MimePart) mimeParts.get(0);
		}

		if (model.isSignMessage()) {
			PGPItem item = model.getAccountItem().getPGPItem();
			// Set id on from address
			item.set(
				"id",
				model.getAccountItem().getIdentityItem().get("address"));
			PGPMimePart signPart =
				new PGPMimePart(new MimeHeader("multipart", "signed"), item);

			signPart.addChild(root);
			root = signPart;
		}

		if (model.isEncryptMessage()) {
			PGPItem item = model.getAccountItem().getPGPItem();
			// Set id on recipient
			item.set("id", model.getRCPTVector().get(0).toString());
			PGPMimePart signPart =
				new PGPMimePart(new MimeHeader("multipart", "encrypted"), item);

			signPart.addChild(root);
			root = signPart;
		}

		header.setRecipients(model.getRCPTVector());

		String composedBody;

		header.set("columba.attachment", new Boolean(true));

		root.getHeader().getHeader().merge(header.getHeader());

		InputStream in = renderer.renderMimePart(root);
		/*
		int next = in.read();
		while (next != -1) {
			composedMessage.append((char) next);
			next = in.read();
		}
		message.setStringSource(composedMessage.toString());
		ColumbaLogger.log.debug("Message:\n" + composedMessage.toString());
		*/
		
		message.setSourceStream(in);
		//StreamUtils.streamCopy(message.getSourceStream(), System.out);
		
		// size
		int size = in.available() / 1024;
		header.set("columba.size", new Integer(size));

		message.setHeader(header);

		message.setAccountUid(accountUid);

		return message;
	}

	/*
		private String createBoundary() {
			StringBuffer bound = new StringBuffer();
	
			bound.append("-----");
			bound.append(System.currentTimeMillis());
			bound.append(model.getHeaderField("From"));
	
			return bound.toString();
		}
	
		private String createMimeMultipart(Vector input) {
			StringBuffer output = new StringBuffer();
			bound = createBoundary();
			MimeHeader multiHeader = new MimeHeader("multipart", "mixed");
			multiHeader.contentParameter.put(
				"boundary",
				new String("\"" + bound + "\""));
	
			output.append(multiHeader.getHeader());
			output.append(
				"\n\tThis is a Mime Multipart Message sent with Columba\n");
	
			int count = input.size();
	
			for (int i = 0; i < count; i++) {
				output.append("\n--" + bound + "\n");
				//output.append(((MimePart)input.get(i)).composeToString());
			}
	
			output.append("\n--" + bound + "--");
	
			return output.toString();
		}
	
		private String createEncryptedMimePart(MimePartTree input) {
			if (input.count() > 1)
				return createEncryptedMimeMultipart(input);
	
			StringBuffer output = new StringBuffer();
			MimePart actPart = input.get(0);
	
			//return actPart.composeToString();
			return null;
		}
	
		private String createEncryptedMimeMultipart(MimePartTree input) {
	
			StringBuffer output = new StringBuffer();
			MimeHeader multiHeader = new MimeHeader("multipart", "encrypted");
			multiHeader.contentParameter.put(
				"protocol",
				"\"application/pgp-encrypted\"");
			bound = bound.substring(2, bound.length());
			multiHeader.contentParameter.put(
				"boundary",
				new String("\"" + bound + "\""));
	
			output.append(multiHeader.getHeader());
			output.append(
				"\n\tThis is a Mime Multipart Message sent with Columba\n");
	
			int count = input.count();
	
			for (int i = 0; i < count; i++) {
				output.append("\n--" + bound + "\n");
				//output.append(input.get(i).composeToString());
			}
	
			output.append("\n--" + bound + "--");
	
			return output.toString();
		}
	*/
}