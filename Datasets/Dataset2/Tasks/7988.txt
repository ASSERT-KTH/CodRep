model.setHtml(Boolean.valueOf(enableHtml).booleanValue());

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

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.nio.charset.UnsupportedCharsetException;
import java.util.Iterator;
import java.util.List;

import org.columba.addressbook.folder.ContactCard;
import org.columba.addressbook.parser.AddressParser;
import org.columba.addressbook.parser.ListParser;
import org.columba.core.io.StreamUtils;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.parser.text.BodyTextParser;
import org.columba.mail.parser.text.HtmlParser;
import org.columba.ristretto.coder.Base64DecoderInputStream;
import org.columba.ristretto.coder.CharsetDecoderInputStream;
import org.columba.ristretto.coder.QuotedPrintableDecoderInputStream;
import org.columba.ristretto.message.BasicHeader;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.Message;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeType;
import org.columba.ristretto.message.StreamableMimePart;
import org.columba.ristretto.message.io.Source;
import org.columba.ristretto.parser.MessageParser;
import org.columba.ristretto.parser.ParserException;

/**
 * 
 * The <code>MessageBuilder</code> class is responsible for creating the
 * information for the <code>ComposerModel</class>class.
 * 
 * It generates appropriate header-information, mimeparts and
 * quoted bodytext 
 *
 * 
 */
public class MessageBuilder {

	public final static int REPLY = 0;
	public final static int REPLY_ALL = 1;
	public final static int REPLY_MAILINGLIST = 2;
	public final static int REPLY_AS_ATTACHMENT = 3;

	public final static int FORWARD = 4;
	public final static int FORWARD_INLINE = 5;

	public final static int OPEN = 6;

	private static MessageBuilder instance;

	public MessageBuilder() {

	}

	public static MessageBuilder getInstance() {
		if (instance == null)
			instance = new MessageBuilder();

		return instance;
	}

	/**
	 * 
	 * Check if the subject headerfield already starts with a pattern
	 * like "Re:" or "Fwd:"
	 * 
	 * @param subject  A <code>String</code> containing the subject
	 * @param pattern A <code>String</code> specifying the pattern
	 *                to search for.
	 **/
	public static boolean isAlreadyReply(String subject, String pattern) {

		if (subject == null)
			return false;

		if (subject.length() == 0)
			return false;

		String str = subject.toLowerCase();

		// for example: "Re: this is a subject"
		if (str.startsWith(pattern) == true)
			return true;

		// for example: "[columba-users]Re: this is a subject"
		int index = str.indexOf(pattern);
		if (index != -1)
			return true;

		return false;
	}

	/**
	 * 
	 * create subject headerfield in using the senders message
	 * subject and prepending "Re:" if not already there
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *               the headerfields of the message we want
	 * 	             reply/forward.
	 * 
	 * FIXME: we need to i18n this!
	 **/
	private static String createReplySubject(ColumbaHeader header) {
		String subject = (String) header.get("columba.subject");

		// if subject doesn't start already with "Re:" prepend it
		if (!isAlreadyReply(subject, "re:"))
			subject = "Re: " + subject;

		return subject;
	}

	/**
	 * 
	 * create Subject headerfield in using the senders message
	 * subject and prepending "Fwd:" if not already there
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *        the headerfields of the message we want
	 * 	      reply/forward.
	 * 
	 * FIXME: we need to i18n this!
	 * 
	 **/
	private static String createForwardSubject(ColumbaHeader header) {
		String subject = (String) header.get("Subject");

		// if subject doesn't start already with "Fwd:" prepend it
		if (!isAlreadyReply(subject, "fwd:"))
			subject = "Fwd: " + subject;

		return subject;
	}

	/**
	 * 
	 * create a To headerfield in using the senders message
	 * Reply-To or From headerfield
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *               the headerfields of the message we want
	 * 	             reply/forward.
	 * 
	 * */
	private static String createTo(ColumbaHeader header) {
		String replyTo = (String) header.get("Reply-To");
		String from = (String) header.get("From");

		if (replyTo == null) {
			// Reply-To headerfield isn't specified, try to use From instead
			if (from != null)
				return from;
			else
				return "";
		} else
			return replyTo;
	}

	/**
	 * 
	 * This is for creating the "Reply To All recipients" 
	 * To headerfield.
	 * 
	 * It is different from the <code>createTo</code> method
	 * in that it also appends the recipients specified in the
	 * To headerfield
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *               the headerfields of the message we want
	 * 	             reply/forward.
	 * 
	 **/
	private static String createToAll(ColumbaHeader header) {
		String sender = "";
		String replyTo = (String) header.get("Reply-To");
		String from = (String) header.get("From");
		String to = (String) header.get("To");
		String cc = (String) header.get("Cc");

		// if Reply-To headerfield isn't specified, try to use from
		if (replyTo == null) {
			sender = from;
		} else
			sender = replyTo;

		// create To headerfield
		StringBuffer buf = new StringBuffer();
		buf.append(sender);
		if (to != null) {

			buf.append(",");
			buf.append(to);
		}
		if (cc != null) {

			buf.append(",");
			buf.append(cc);
		}

		return buf.toString();
	}

	/**
	 * 
	 * This method creates a To headerfield for the
	 * "Reply To MailingList" action. 
	 * It uses the List-Post headerfield and falls back
	 * to Reply-To or From if needed
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *               the headerfields of the message we want
	 * 	             reply/forward.
	 * */
	private static String createToMailinglist(ColumbaHeader header) {

		// example: X-BeenThere: columba-devel@lists.sourceforge.net
		String sender = (String) header.get("X-BeenThere");

		if (sender == null)
			sender = (String) header.get("Reply-To");

		if (sender == null)
			sender = (String) header.get("From");

		return sender;
	}

	/**
	 * 
	 * Creates In-Reply-To and References headerfields. 
	 * These are useful for mailing-list threading.
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *               the headerfields of the message we want
	 * 	             reply/forward.
	 * 
	 * @param model  The <code>ComposerModel</code> we want to 
	 *               pass the information to.
	 * 
	 * FIXME: if the References headerfield contains to many 
	 *        characters, we have to remove some of the first
	 *        References, before appending another one.
	 *        (RFC822 headerfields are not allowed to become  
	 *        that long)
	 * 
	 * */
	private static void createMailingListHeaderItems(
		ColumbaHeader header,
		ComposerModel model) {
		String messageId = (String) header.get("Message-ID");
		if (messageId == null)
			messageId = (String) header.get("Message-Id");

		if (messageId != null) {
			model.setHeaderField("In-Reply-To", messageId);

			String references = (String) header.get("References");
			if (references != null) {
				references = references + " " + messageId;
				model.setHeaderField("References", references);

			}
		}
	}

	/**
	 * 
	 * Search the correct Identity for replying to someone
	 * 
	 * @param header A <code>ColumbaHeader</code> which contains
	 *               the headerfields of the message we want
	 * 	             reply/forward.
	 */
	private static AccountItem getAccountItem(Header header) {
		String host = (String) header.get("columba.host");
		String address = (String) header.get("To");

		// if the Account/Identity is already defined in the columba.host headerfield
		// use it. Otherwise search through every account for the To/email-address
		AccountItem item =
			MailConfig.getAccountList().hostGetAccount(host, address);

		return item;
	}

	/**
	 * 
	 * create bodytext
	 * 
	 * @param message A <code>Message</code> which contains
	 *                the bodytext of the message we want
	 * 	              reply/forward.
	 */
	private static String createBodyText(MimePart mimePart)
		throws IOException {
		CharSequence bodyText = "";

		StreamableMimePart bodyPart = 
			(StreamableMimePart) mimePart;
		String charsetName =
			bodyPart.getHeader().getContentParameter("charset");
		String encoding = bodyPart.getHeader().getContentTransferEncoding();

		InputStream body = bodyPart.getInputStream();
		if (encoding != null) {
			if (encoding.equals("quoted-printable")) {
				body = new QuotedPrintableDecoderInputStream(body);
			} else if (encoding.equals("base64")) {
				body = new Base64DecoderInputStream(body);
			}
		}

		if (charsetName != null) {
			Charset charset;
			try {
				charset = Charset.forName(charsetName);
			} catch (UnsupportedCharsetException e) {
				charset = Charset.forName(System.getProperty("file.encoding"));
			}
			body = new CharsetDecoderInputStream(body, charset);
		}

		return StreamUtils.readInString(body).toString();
	}

	/**
	 * 
	 * prepend "> " characters to the bodytext to specify 
	 * we are quoting
	 * 
	 * @param message A <code>Message</code> which contains
	 *                the bodytext of the message we want
	 * 	              reply/forward.
	 * @param html    True for html messages (a different quoting is necessary)
	 * 
	 * FIXME: we should make this configureable
	 * 
	 */
	private static String createQuotedBodyText(
		MimePart mimePart,
		boolean html)
		throws IOException {
		String bodyText = createBodyText(mimePart);

		// Quote according model type (text/html)
		String quotedBodyText;
		if (html) {
			// html - quoting is done by inserting a div around the 
			// message formattet with a blue line at left edge

			// TODO: Implement quoting (font color, stylesheet, blockquote???)

			/*
			String lcase = bodyText.toLowerCase();
			StringBuffer buf = new StringBuffer();
			String quoteStart = "<blockquote>";
			String quoteEnd   = "</blockquote>";
			
			int pos = lcase.indexOf("<body");
			pos = lcase.indexOf(">", pos) + 1;
			buf.append(bodyText.substring(0, pos));
			buf.append(quoteStart);
			int end = lcase.indexOf("</body");
			buf.append(bodyText.substring(pos, end));
			buf.append(quoteEnd);
			buf.append(bodyText.substring(end));
			
			ColumbaLogger.log.debug("Source:\n" + bodyText);
			ColumbaLogger.log.debug("Result:\n" + buf.toString());
			
			quotedBodyText = buf.toString();
			*/
			quotedBodyText = bodyText;

		} else {
			// plain text
			quotedBodyText = BodyTextParser.quote(bodyText);
		}

		return quotedBodyText;

	}

	/** 
	 * 
	 * Fill the <code>ComposerModel</code> with headerfields,
	 * bodytext and mimeparts
	 * 
	 * @param message   A <code>Message</code> which contains
	 *                  the headerfield/bodytext/mimeparts of 
	 *                  of the message we want to reply/forward.
	 * 
	 * @param model     The <code>ComposerModel</code> we want to 
	 *                  pass the information to.
	 * 
	 * @param operation an int value specifying the operation-type
	 *                  (for example: MessageBuilder.REPLY, .REPLY_TO_ALL)
	 * 
	 */
	public void createMessage(
		ColumbaMessage message,
		ComposerModel model,
		int operation)
		throws IOException {

		ColumbaHeader header = (ColumbaHeader) message.getHeaderInterface();

		MimePart bodyPart = message.getBodyPart();

		if (bodyPart != null) {
			String charset =
				bodyPart.getHeader().getContentParameter("charset");
			if (charset != null) {
				model.setCharsetName(charset);
			}
		}

		if ((operation == FORWARD) || (operation == FORWARD_INLINE)) {
			model.setSubject(createForwardSubject(header));
		} else {
			model.setSubject(createReplySubject(header));
		}

		String to = null;
		if (operation == REPLY)
			to = createTo(header);
		else if (operation == REPLY_ALL)
			to = createToAll(header);
		else if (operation == REPLY_MAILINGLIST)
			to = createToMailinglist(header);

		if (to != null) {
			model.setTo(to);
			addSenderToAddressbook(to);
		}

		if (operation != FORWARD)
			createMailingListHeaderItems(header, model);

		if ((operation != FORWARD) && (operation != FORWARD_INLINE)) {
			AccountItem accountItem = getAccountItem(header.getHeader());
			model.setAccountItem(accountItem);
		}

		// Initialisation of model to html or text
		if ((operation == REPLY_AS_ATTACHMENT) || (operation == FORWARD)) {
			/* original message is sent as attachment - model is setup
			 * according to the stored option for html / text
			 */
			XmlElement optionsElement =
				MailConfig.get("composer_options").getElement("/options");
			XmlElement htmlElement = optionsElement.getElement("html");
			if (htmlElement == null)
				htmlElement = optionsElement.addSubElement("html");
			String enableHtml = htmlElement.getAttribute("enable", "false");
			model.setHtml((new Boolean(enableHtml)).booleanValue());
		} else {
			/* 
			 * original message is sent "inline" - model is setup according
			 * to the type of the original message.
			 * NB: If the original message was plain text, the message type
			 *     seen here is always text. If the original message
			 *     contained html, the message type seen here will depend
			 *     on the "prefer html" option.
			 */
			MimeHeader bodyHeader = message.getBodyPart().getHeader();
			if (bodyHeader.getMimeType().getSubtype().equals("html")) {
				model.setHtml(true);
			} else {
				model.setHtml(false);
			}
		}

		if ((operation == REPLY_AS_ATTACHMENT) || (operation == FORWARD)) {
			// append message as mimepart
			if (message.getSource() != null) {
				// initialize MimeHeader as RFC822-compliant-message
				MimeHeader mimeHeader = new MimeHeader();
				mimeHeader.setMimeType(new MimeType("message", "rfc822"));

				model.addMimePart(
					new LocalMimePart(mimeHeader, message.getSource()));
			}
		} else {
			// prepend "> " to every line of the bodytext
			String bodyText = createQuotedBodyText(message.getBodyPart(), model.isHtml());
			if (bodyText == null) {
				bodyText = "[Error parsing bodytext]";
			}
			model.setBodyText(bodyText);
		}

	}

	/** 
		 * 
		 * Fill the <code>ComposerModel</code> with headerfields,
		 * bodytext and mimeparts
		 * 
		 * @param message   A <code>Message</code> which contains
		 *                  the headerfield/bodytext/mimeparts of 
		 *                  of the message we want to reply/forward.
		 * 
		 * @param model     The <code>ComposerModel</code> we want to 
		 *                  pass the information to.
		 * 
		 * @param templateBody bodytext of template message
		 * 
		 * @param htmlTemplate true if the templateBody shall be interpreted
		 * 					   as html
		 */
	public void createMessageFromTemplate(
		ColumbaMessage message,
		ComposerModel model,
		StreamableMimePart templateBodypart,
		boolean htmlTemplate)
		throws IOException {

		ColumbaHeader header = (ColumbaHeader) message.getHeaderInterface();

		MimePart bodyPart = message.getBodyPart();
		String templateBody = createBodyText(templateBodypart);
		
		if (bodyPart != null) {
			String charset =
				bodyPart.getHeader().getContentParameter("charset");
			if (charset != null) {
				model.setCharsetName(charset);
			}
		}

		model.setSubject(createReplySubject(header));

		String to = createTo(header);

		if (to != null) {
			model.setTo(to);
			addSenderToAddressbook(to);
		}

		createMailingListHeaderItems(header, model);

		AccountItem accountItem = getAccountItem(header.getHeader());
		model.setAccountItem(accountItem);

		// Initialisation of model to html or text
		MimeHeader bodyHeader = message.getBodyPart().getHeader();
		if (bodyHeader.getMimeType().getSubtype().equals("html")) {
			model.setHtml(true);
		} else {
			model.setHtml(false);
		}

		// prepend "> " to every line of the bodytext
		String bodyText = createQuotedBodyText(message.getBodyPart(), model.isHtml());
		if (bodyText == null) {
			bodyText = "[Error parsing bodytext]";
		}

		if (!htmlTemplate && model.isHtml()) {
			// conversion to html necessary
			templateBody = HtmlParser.textToHtml(templateBody, null, null);
		} else if (htmlTemplate && !model.isHtml()) {
			// conversion to text necessary
			templateBody = HtmlParser.htmlToText(templateBody);
		}

		StringBuffer buf;
		if (model.isHtml()) {
			// insert template just before ending body tag
			String lcase = bodyText.toLowerCase();
			int pos = lcase.indexOf("</body>");
			if (pos < 0) {
				pos = bodyText.length();
			}
			buf = new StringBuffer(bodyText.substring(0, pos));
			buf.append(HtmlParser.getHtmlBody(templateBody));
			buf.append("</body></html>");
		} else {
			// just insert template at end (text mode)
			buf = new StringBuffer(bodyText);
			buf.append(templateBody);
		}

		model.setBodyText(buf.toString());

	}

	/** 
	 * 
	 * Fill the <code>ComposerModel</code> with headerfields,
	 * bodytext and mimeparts.
	 * 
	 * This is a special method for the "Open Message in Composer"
	 * action.
	 * 
	 * @param message   The <code>Message</code> we want to edit
	 *                  as new message.
	 * 
	 * @param model     The <code>ComposerModel</code> we want to 
	 *                  pass the information to.
	 * 
	 */
	public static void openMessage(Source messagesource, ComposerModel model)
		throws ParserException, IOException {
		Message message = MessageParser.parse(messagesource);
		Header header = message.getHeader();
		BasicHeader basicHeader = new BasicHeader(header);

		// copy every headerfield the original message contains
		model.setHeader(header);

		model.setTo(header.get("To"));

		AccountItem accountItem = getAccountItem(header);
		model.setAccountItem(accountItem);

		model.setSubject(basicHeader.getSubject());

		LocalMimePart bodyPart =
			(LocalMimePart) message.getMimePartTree().getFirstTextPart("html");

		// No conversion needed - the composer now supports both html and text
		//
		//if (bodyPart.getHeader().getMimeType().getSubtype().equals("html")) {
		//	model.setBodyText(
		//		HtmlParser.htmlToText(bodyPart.getBody().toString()));
		//} else {
		//	model.setBodyText(bodyPart.getBody().toString());
		//}
		if (bodyPart.getHeader().getMimeType().getSubtype().equals("html")) {
			// html
			model.setHtml(true);
		} else {
			model.setHtml(false);
		}

		//model.setBodyText(bodyPart.getBody().toString());
		model.setBodyText( createBodyText( bodyPart) );
		
	}

	/********************** addressbook stuff ***********************/

	/**
	 *
	 * add automatically every person we'll send a message to
	 * the "Collected Addresses" Addressbook
	 * 
	 * FIXME: this should be moved outside independent
	 *        -> should be in core, or even better addressbook
	 *
	 */
	public void addSenderToAddressbook(String sender) {

		if (sender != null) {
			if (sender.length() > 0) {

				org.columba.addressbook.folder.Folder selectedFolder =
					org
						.columba
						.addressbook
						.facade
						.FolderFacade
						.getCollectedAddresses();

				// this can be a list of recipients
				List list = ListParser.parseString(sender);
				Iterator it = list.iterator();
				while (it.hasNext()) {
					String address =
						AddressParser.getAddress((String) it.next());
					System.out.println("address:" + address);

					if (!selectedFolder.exists(address)) {
						ContactCard card = new ContactCard();

						String fn = AddressParser.getDisplayname(sender);
						System.out.println("fn=" + fn);

						card.set("fn", fn);
						card.set("displayname", fn);
						card.set("email", "internet", address);

						selectedFolder.add(card);
					}

				}

			}
		}

	}

}