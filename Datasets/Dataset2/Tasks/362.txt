String header = EncodedWord.decode(

/*
 * EudoraMailImportFilter.java Created 2003-05-14 by Karl Peder Olesen
 * 
 * 
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with the
 * License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
 * 
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
 * the specific language governing rights and limitations under the License.
 * 
 * The Original Code is Eudora Mail Import Filter plugin for Columba.
 * 
 * The Initial Developer of the Original Code is Karl Peder Olesen. Portions
 * created by Karl Peder Olesen are Copyright (C) 2003
 * 
 * All Rights Reserved.
 *  
 */

package org.columba.mail;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.StringReader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.StringTokenizer;
import java.util.logging.Logger;

import org.columba.api.command.IWorkerStatusController;
import org.columba.mail.folder.IMailbox;
import org.columba.mail.folder.mailboximport.AbstractMailboxImporter;
import org.columba.ristretto.coder.EncodedWord;

/**
 * Class used to import Eudora mail boxes. Plugin to Columba
 * 
 * @author Karl Peder Olesen
 * @version 1.0
 */
public class EudoraMailImportFilter extends AbstractMailboxImporter {

	/** JDK 1.4+ logging framework logger, used for logging. */
	private static final Logger LOG = Logger.getLogger("org.columba.mail");

	/** Time zone, e.g. "+0100", used for new Date headers (= host default) */
	private static final String TIME_ZONE = (new SimpleDateFormat("Z"))
			.format(new Date());

	/**
	 * Charset, e.g. "iso-8859-1", when nothing else is specified (= host
	 * default)
	 */
	private static final String DEFAULT_CHARSET = System
			.getProperty("file.encoding");

	public EudoraMailImportFilter() {
		super();
	}

	/**
	 * Creates a new EudoraMailImportFilter object
	 * 
	 * @param destinationFolder
	 *            Where to import mails to (folder inside Columba)
	 * @param sourceFiles
	 *            Mailboxes to import
	 */
	public EudoraMailImportFilter(IMailbox destinationFolder, File[] sourceFiles) {
		super(destinationFolder, sourceFiles);
	}

	/**
	 * Returns which type of import is supported
	 * 
	 * @return type of import supported - here TYPE_FILE (=0)
	 */
	public int getType() {
		return TYPE_FILE;
	}

	public String getDescription() {
		return "Eudora Mail Pro 4.0\n";
	}

	/**
	 * Imports a single mailbox file. This one is called from importMailbox
	 * (defined in DefaultMailboxImporter), which iterates over the source files
	 * to be imported - and calls this method for each file.
	 * 
	 * @param file
	 *            Mailbox file to import
	 * @param worker
	 *            Used for handling user interuption
	 * @param destFolder
	 *            Which mail folder inside Columba to import into
	 */
	public void importMailboxFile(File file, IWorkerStatusController worker,
			IMailbox destFolder) throws Exception {
		LOG.fine("Starting to import Eudora mbox file: "
				+ file.getAbsolutePath());

		StringBuffer strbuf = new StringBuffer();
		BufferedReader in = new BufferedReader(new FileReader(file));
		String str;
		int msgCounter = 0; // counts how many messages has been
		// processed
		String replacementDate = null; // date fetched from "From ???@??? ..."

		// parse line by line
		while ((str = in.readLine()) != null) {
			// if user cancelled task exit immediately
			if (worker.cancelled()) {
				return;
			}

			// Lines not starting with "From ???@???" is part of the message
			// (headers or body)
			if (!str.startsWith("From ???@???") || (str.length() == 0)) {
				strbuf.append(str + "\n");
			} else // we reached "From ..." (start of new message)
			{
				// If a msg has been read, import it into Columba
				if (strbuf.length() != 0) {
					if (convertAndSaveMessage(strbuf.toString(),
							replacementDate, worker, destFolder)) {
						msgCounter++;
					}
				}
				// reset for new message
				if (str.length() >= 13)
					replacementDate = str.substring(13); // fetch date from
				// "From ???@???
				// ..."
				else
					replacementDate = "";
				strbuf = new StringBuffer();
			}

		}

		// save last message (while loop terminated before last msg was saved)
		if (strbuf.length() > 0) {
			if (convertAndSaveMessage(strbuf.toString(), replacementDate,
					worker, destFolder)) {
				msgCounter++;
			}
		}

		LOG.fine("Import of Eudora mbox file completed. " + msgCounter
				+ " messages imported");
		in.close();

	} // ** End of method importMailboxFile

	/**
	 * Returns a new date header from a date string like "Tue Apr 01 23:17:33
	 * 2003". The date header returned will be on a format like: "Date: Tue, 01
	 * Apr 2003 23:17:33 +0100", where +0100 is the time zone
	 * 
	 * @param dateStr
	 *            date string
	 * @param timeZone
	 *            time zone, e.g. +0100
	 * @return date header without "\n"
	 */
	private String getNewDateHeader(String dateStr, String timeZone) {
		StringTokenizer tok = new StringTokenizer(dateStr);
		try {
			String dow = tok.nextToken(); // day of week
			String mon = tok.nextToken(); // month
			String day = tok.nextToken(); // day of month
			String time = tok.nextToken(); // time
			String year = tok.nextToken(); // year

			StringBuffer dateHeader = new StringBuffer();
			dateHeader.append("Date: ");
			dateHeader.append(dow + ",");
			dateHeader.append(" " + day + " " + mon + " " + year);
			dateHeader.append(" " + time);
			if ((!(timeZone == null)) && (!timeZone.equals(""))) {
				dateHeader.append(" " + timeZone);
			}

			return dateHeader.toString();
		} catch (java.util.NoSuchElementException e) {
			// invalid date format - not enough tokens in it!!

			// Logging.log.severe(
			// "Not enough tokens in \""
			// + dateStr
			// + "\" to create Date: header. Returning null",
			// e);
			LOG.severe("Not enough tokens in \"" + dateStr
					+ "\" to create Date: header. Returning null");
			return null;
		}
	} // ** End of method getDateHeader

	/**
	 * Handles a single message, i.e.: 1) Creates a new date header if necessary
	 * (from replacement date) 2) Modifies the Content-Type: header if necessary
	 * 3) Create attachment lists as a "multipart" in the msg, either from lines
	 * stating "Attachment Converted:" or from "X-Attachments" header ... and
	 * then saves the msg to the specified folder
	 * 
	 * @param msg
	 *            Message incl. both headers and body
	 * @param replDate
	 *            Replacement date in a string like "Tue Apr 01 23:17:33 2003"
	 * @param worker
	 *            Used for handling user interuption
	 * @param destFolder
	 *            Which mail folder inside Columba to import into
	 * @return True on success, false on error
	 */
	private boolean convertAndSaveMessage(String msg, String replacementDate,
			IWorkerStatusController worker, IMailbox destFolder) {
		// divide message into headers and body
		String[] divided = divideMessage(msg);
		if (divided == null) {
			LOG.severe("Error splitting message into headers and body");
			return false;
		}
		String headers = divided[0];
		String body = divided[1];

		// loop over headers and modify them as needed
		HeaderTokenizer tokenizer = new HeaderTokenizer(headers);
		EncodedWord decoder = new EncodedWord();
		StringBuffer headerBuf = new StringBuffer();
		boolean dateFound = false;
		boolean contentTypeFound = false;
		String line = tokenizer.nextLine();
		while (line != null) {
			if (line.indexOf(':') != -1) {
				// a header
				String key = line.substring(0, line.indexOf(':'));
				String header = decoder.decode(
						(CharSequence) line.substring(line.indexOf(':') + 1)
								.trim()).toString();

				// handle header
				if (key.equalsIgnoreCase("Date")) {
					// Date header
					dateFound = true; // we got a date header (store this
					// fact for later use
				} else if (key.equalsIgnoreCase("Content-Type")) {
					contentTypeFound = true;

					/*
					 * For multipart Content-Types we need to take action (if
					 * boundary is nonexistent): Eudora stores content type =
					 * multipart even though the message is not really multipart -
					 * e.g. because an attachment already has has been decoded
					 * by Eudora)
					 */
					ContentType conType = new ContentType(header); // parse
					// Content-Type
					if ((conType.getType().equalsIgnoreCase("multipart"))
							&& (body.indexOf("--" + conType.getBoundary()) == -1)) {
						// boundary not found - Content-Type must be changed
						if (conType.getSubType()
								.equalsIgnoreCase("alternative")) {
							// just convert it to text/plain or text/html
							header = guessBodyContentType(body);
							LOG
									.fine("Content-Type: multipart/alternative replaced with "
											+ header);
						} else {
							/*
							 * mixed or unknown multipart type (to be treated as
							 * mixed). This is typically a message with
							 * attachments. Eudora just stores links to them -
							 * therefore we create a new multipart/mixed message
							 * with 2nd part = html page with links to
							 * attachments
							 */
							String[] split = createAttachmentListFromAttachmentConverted(body);
							if ((split == null) || (split.length == 1)) {
								// no attachments found - just convert it to
								// text/plain or text/html
								header = guessBodyContentType(body);
								LOG.fine("Content-Type: multipart/"
										+ conType.getSubType()
										+ " replaced by " + header);
							} else {
								header = "multipart/mixed;\n\tboundary="
										+ conType.getBoundary();
								body = createBodyFromParts(split, conType
										.getBoundary());
								LOG
										.fine("Content-Type: multipart/mixed. Boundaries added to msg body");
							}
						}
					}
				} else if (key.equalsIgnoreCase("X-Attachments")) {
					/*
					 * Such a header is used by Eudora to indicate attachments
					 * for outgoing messages. Outgoing messages have no
					 * Content-Type specified. Therefore the Content-Type header
					 * can be safely set here without risk of conflicts with the
					 * modifications made above
					 */
					if (header.length() > 0) {
						// attachments found
						String[] split = createAttachmentListFromHeader(body,
								header);

						if ((split == null) || (split.length == 1)) {
							// no attachments found - just insert a
							// Content-Type header
							headerBuf.append("MIME-Version: 1.0\n"); // extra
							// header
							// necessary
							key = "Content-Type"; // X-Attachments header is
							// replaced
							header = guessBodyContentType(body);
							contentTypeFound = true;
							LOG
									.fine("X-Attachments header replaced by Content-Type: "
											+ header);
						} else {
							// get unique boundary (not checked against att.
							// list part - but guess its ok)
							String unique = getUniqueBoundary(body);
							headerBuf.append("MIME-Version: 1.0\n"); // extra
							// header
							// necessary
							key = "Content-Type"; // X-Attachments header is
							// replaced
							header = "multipart/mixed;\n\tboundary=" + unique;
							contentTypeFound = true; // we have now added
							// such a header
							body = createBodyFromParts(split, unique);
							LOG
									.fine("X-Attachments header replaced by Content-Type: multipart/mixed");
						}
					}
				}

				// store header after processing
				headerBuf.append(key + ": " + header + "\n");

			}
			line = tokenizer.nextLine();
		} // ** End of while loop over headers

		/*
		 * If no Date header was found, it is necessary to contruct a new one
		 * (this is the case for outgoing messages from Eudora)
		 */
		if (!dateFound) {
			LOG.fine("Date header missing - constructing new one");
			String dateHeader = getNewDateHeader(replacementDate, TIME_ZONE);
			if (dateHeader != null)
				headerBuf.append(dateHeader + "\n"); // append the new Date
			// header
		}

		/*
		 * If no Content-Type header was found, it is necessary to construct a
		 * new one (for outgoing msg Eudora never includes a Content-Type =>
		 * html msg is not shown correctly).
		 */
		if (!contentTypeFound) {
			LOG.fine("Content-Type header missing - constructing new one");
			String contHeader = "Content-Type: " + guessBodyContentType(body);
			headerBuf.append("MIME-Version: 1.0\n");
			headerBuf.append(contHeader + "\n");
		}

		// save message to destination folder
		return saveMessage(headerBuf.toString(), body, worker, destFolder);

	} // ** End of method convertAndSavemessage

	/**
	 * Used to save messages to destination folder. Called from
	 * convertAndSaveMessage.
	 * 
	 * @param headers
	 *            Header part of message, without the last "\n" separator (it is
	 *            added here)
	 * @param body
	 *            Body part of message
	 * @param worker
	 * @param destFolder
	 *            Folder in Columba to save message in
	 * @return True on success, false on error
	 */
	private boolean saveMessage(String headers, String body,
			IWorkerStatusController worker, IMailbox destFolder) {
		StringBuffer buf = new StringBuffer();
		// create full msg from headers and body
		buf.append(headers);
		buf.append("\n");
		buf.append(body);

		// ... and save it
		try {
			// NB: This is the saveMessage method def. in
			// DefaultMessageImporter
			saveMessage(buf.toString(), worker, destFolder);
			return true;
		} catch (Exception e) {
			// Logging.log.severe("Error saving converted message", e);
			LOG.severe("Error saving converted message: " + e.getMessage());
			return false;
		}
	} // ** End of method saveMessage

	/**
	 * Creates a multipart body from different body parts separated by the given
	 * boundary. The different part must have Content-Type etc. specified, since
	 * this is not done here.
	 * 
	 * @param parts
	 *            The different body parts (MUST have at least one element
	 * @param boundary
	 *            Boundary for separating elements (without beginning "--")
	 * @return The new body
	 */
	private String createBodyFromParts(String[] parts, String boundary) {
		// build new message body
		StringBuffer newBody = new StringBuffer();
		for (int i = 0; i < parts.length; i++) {
			newBody.append("--" + boundary + "\n");
			newBody.append(parts[i]);
		}
		newBody.append("--" + boundary + "--\n");
		return newBody.toString();
	}

	/**
	 * Generates a boundary, which is unique in relation to the message body. It
	 * is guaranteed that the string ("--" + boundary) is not found in the msg
	 * body
	 * 
	 * @param body
	 *            The message body
	 * @return A unique boundary
	 */
	private String getUniqueBoundary(String body) {
		String boundary = "BOUNDARY"; // initial guess
		int i = 0;
		boolean found = true;
		while (found) {
			if (body.indexOf("--" + boundary) == -1)
				found = false;
			else {
				boundary = boundary + String.valueOf(i);
				i++;
			}
		}
		// unique boundary found
		return boundary;
	}

	/**
	 * Used to divide a message (RFC822 compliant headers) into headers and
	 * body. Method found in and copied from
	 * org.columba.mail.parser.AbstractParser
	 * 
	 * @param input
	 *            message to divide
	 * @return Array with [0] = headers and [1] = body (null on error)
	 */
	private String[] divideMessage(String input) {
		String[] output = new String[2];
		int emptyLinePos;

		if (input.length() == 0)
			return null;

		if (input.charAt(0) == '\n') {
			output[0] = new String();
			output[1] = input;
			return output;
		}

		emptyLinePos = input.indexOf("\n\n");

		if (input.indexOf("\n\n") != -1) {
			output[0] = input.substring(0, emptyLinePos + 1);
			output[1] = input.substring(emptyLinePos + 2);
		} else {
			output[0] = input;
			output[1] = new String();
		}

		return output;
	} // ** End of method divideMessage

	/**
	 * Simple method for guessing whether a message body is text/plain or
	 * text/html.
	 * 
	 * @param body
	 *            The message body
	 * @return The Content-type as "text/html" (possibly with a charset if
	 *         found) or "text/plain" (default)
	 */
	private String guessBodyContentType(String body) {
		// is it HTML or plain text
		boolean isHTML = false;
		if (((body.indexOf("<x-html>") != -1) || (body.indexOf("<X-HTML>") != -1))
				&& ((body.indexOf("</x-html>") != -1) || (body
						.indexOf("</X-HTML>") != -1)))
			isHTML = true;
		else if (((body.indexOf("<HTML>") != -1) || (body.indexOf("<html>") != -1))
				&& ((body.indexOf("</HTML>") != -1) || (body.indexOf("</html>") != -1)))
			isHTML = true;

		if (!isHTML) {
			if ((DEFAULT_CHARSET != null) && (DEFAULT_CHARSET.length() > 0))
				return "text/plain; charset=" + DEFAULT_CHARSET;
			else
				return "text/plain";
		} else {
			/*
			 * It is HTML, try to find out which charset from meta tag: NB: The
			 * seach for charset below is very simple. It assumes that the meta
			 * tag to find is on ITS OWN LINE, i.e. " <meta" can be found at the
			 * beginning of the line, and all the content of the tag is found on
			 * the same line! Could be better, but this is first shot...
			 */
			BufferedReader reader = new BufferedReader(new StringReader(body));
			String line = null;
			try {
				line = reader.readLine();
			} catch (IOException e) {
				// Logging.log.severe("Error while looking for charset", e);
				LOG
						.severe("Error while looking for charset: "
								+ e.getMessage());
			}
			String charset = null;
			while (line != null) {
				line = line.trim();
				if ((line.length() > 5)
						&& (line.substring(0, 5).equalsIgnoreCase("<meta"))) {
					String lcLine = line.toLowerCase(); // for easier search /
					// matching
					if ((lcLine.indexOf("http-equiv=content-type") != -1)
							|| (lcLine.indexOf("http-equiv=\"content-type\"") != -1)) {
						// meta tag with content definition found
						int pos = lcLine.indexOf("charset");
						if (pos != -1) {
							// charset is specified - find it
							pos = lcLine.indexOf('=', pos);
							pos++;
							while (lcLine.charAt(pos) == ' ') {
								pos++;
							} // step
							// past
							// spaces
							// find position of '>', '"'. or ' ' which is = end
							// of charset name
							int end = lcLine.length();
							int tmp = lcLine.indexOf('>', pos);
							if (tmp != -1)
								end = tmp;
							tmp = lcLine.indexOf('"', pos);
							if ((tmp != -1) && (tmp < end))
								end = tmp;
							tmp = lcLine.indexOf(' ', pos);
							if ((tmp != -1) && (tmp < end))
								end = tmp;
							// charset is found from line, not lcLine => not
							// forced lower case
							charset = line.substring(pos, end);
							break; // we found what we were looking for
						}
					}
				}
				try {
					line = reader.readLine();
				} catch (IOException e) {
					// Logging.log.severe(
					// "Error while looking for charset",
					// e);
					LOG.severe("Error while looking for charset: "
							+ e.getMessage());
					line = null; // this will terminate the loop
				}
			} // end of while loop

			if ((charset != null) && (charset.length() > 0))
				return "text/html; charset=" + charset;
			else {
				if ((DEFAULT_CHARSET != null) && (DEFAULT_CHARSET.length() > 0))
					return "text/html; charset=" + DEFAULT_CHARSET;
				else
					return "text/html";
			}
		}

	} // ** End of method guessBodyContentType

	/**
	 * Divides a message body into two parts with content types defined: The
	 * message it self and a list of attachments (as html). The attachments are
	 * found as a list of files in a header, separated by ; and not enclosed by ".
	 * If no attachments are found, the body will be left untouched.
	 * 
	 * @param body
	 *            The message body
	 * @param xAttachments
	 *            Header with attachment file names (X-Attachments header)
	 * @return Body in first array entry, attachment list (if present) in second
	 *         array entry (null on error)
	 */
	private String[] createAttachmentListFromHeader(String body,
			String xAttachments) {
		StringTokenizer tok = new StringTokenizer(xAttachments, ";");
		StringBuffer attachBuf = new StringBuffer();
		while (tok.hasMoreTokens()) {
			// handle attachment (by creating a link)
			String name = tok.nextToken().trim();
			attachBuf.append("<a href=\"file://" + name + "\">" + name
					+ "</a><br>\n");
		}

		if (attachBuf.length() == 0) {
			// no attachments found - should in fact have been checked by the
			// caller
			String[] retVal = new String[1];
			retVal[0] = body; // body untouched
			return retVal;
		} else {
			// attachments found...
			// insert start and end for html
			attachBuf
					.insert(0,
							"<html><head><title>Attachment list</title></head><body><p>\n");
			attachBuf.append("</p></body></html>\n");
			// insert header for attachment list
			String charset;
			if ((DEFAULT_CHARSET != null) && (DEFAULT_CHARSET.length() > 0))
				charset = "; charset=" + DEFAULT_CHARSET;
			else
				charset = "";
			attachBuf.insert(0, "Content-Type: text/html" + charset
					+ "; name=\"attachmentlist.html\"\n\n");
			// build new body part
			StringBuffer bodyBuf = new StringBuffer();
			String header = "Content-Type: "
					+ guessBodyContentType(bodyBuf.toString());
			bodyBuf.append(header + "\n\n");
			bodyBuf.append(body);
			// return parts
			String[] retVal = new String[2];
			retVal[0] = bodyBuf.toString();
			retVal[1] = attachBuf.toString();
			return retVal;
		}
	} // ** End of method createAttachmentListFromHeader

	/**
	 * Divides a message body into two parts with content types defined: The
	 * message it self and a list of attachments (as html). If no attachments
	 * are found, the body will be left untouched.
	 * 
	 * @param body
	 *            The message body
	 * @return Body in first array entry, attachment list (if present) in second
	 *         array entry (null on error)
	 */
	private String[] createAttachmentListFromAttachmentConverted(String body) {
		StringBuffer bodyBuf = new StringBuffer();
		StringBuffer attachBuf = new StringBuffer();
		BufferedReader reader = new BufferedReader(new StringReader(body));
		try {
			String line = reader.readLine();
			while (line != null) {
				if (line.startsWith("Attachment Converted:")) {
					// handle attachment (by creating a link)
					String name = line.substring(line.indexOf(':') + 1).trim();
					if (name.startsWith("\""))
						name = name.substring(1, name.length() - 1);
					attachBuf.append("<a href=\"file://" + name + "\">" + name
							+ "</a><br>\n");
				} else {
					// part of body
					bodyBuf.append(line + "\n");
				}
				line = reader.readLine();
			}

			if (attachBuf.length() > 0) {
				// attachments found

				// insert start and end for html
				attachBuf
						.insert(0,
								"<html><head><title>Attachment list</title></head><body><p>\n");
				attachBuf.append("</p></body></html>\n");
				// insert header for attachment list
				String charset;
				if ((DEFAULT_CHARSET != null) && (DEFAULT_CHARSET.length() > 0))
					charset = "; charset=" + DEFAULT_CHARSET;
				else
					charset = "";
				attachBuf.insert(0, "Content-Type: text/html" + charset
						+ "; name=\"attachmentlist.html\"\n\n");

				// build new body part
				String header = "Content-Type: "
						+ guessBodyContentType(bodyBuf.toString());
				bodyBuf.insert(0, header + "\n\n");

				String[] retVal = new String[2];
				retVal[0] = bodyBuf.toString();
				retVal[1] = attachBuf.toString();
				return retVal;
			} else {
				// no attachments found
				String[] retVal = new String[1];
				retVal[0] = body; // body untouched
				return retVal;
			}
		} catch (IOException e) {
			// Logging.log.severe("Error parsing body for attachments", e);
			LOG.severe("Error parsing body for attachments: " + e.getMessage());
			return null;
		}
	} // ** End of method createAttachmentListFromAttachmentConverted

} // ** End of class EudoraMailImportFilter