args.add(new Atom(messageSet));

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
//
//$Log: IMAPProtocol.java,v $
//
package org.columba.mail.imap.protocol;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.lang.reflect.Array;
import java.net.Socket;
import java.util.List;
import java.util.Vector;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.folder.MessageFolderInfo;
import org.columba.mail.imap.IMAPResponse;

/**
 *
 * @author frd
 *
 * This is the implementation of the IMAP protocol as defined in
 * RFC2060 (http://www.rfc-editor.org). Every IMAP command has
 * its corresponding function. So, you *really* need to read the
 * RFC to understand it.
 *
 * You should also take a look at the following classes:
 * - <code>IMAPInputStream</code> is a special inputstream which
 *   handles all IMAP related specialities
 * - <code>ArgumentWriter</code> takes all arguments you pass
 *   to          the server and makes sure they are escaped (etc.) correctly
 * - <code>Arguments</code> is a lightweight class to encapsulate the
 *   different  arguments
 * - exception classes:
 *    - <code>BadCommandException</code>
 *    - <code>CommandFailedException</code>
 *    - <code>DisconnectedException</code>
 *    - <code>IMAPProtocolException</code>
 *
 */
public class IMAPProtocol {
	/**
	 *	default IMAP port
	 */
	public static final int DEFAULT_PORT = 143;

	/**
	 * line endings
	 */
	private static final byte[] CRLF = {(byte) '\r', (byte) '\n' };

	/**
	 *
	 * client operation socket
	 */
	private Socket socket;

	/**
	 * inputstream
	 */
	private IMAPInputStream in;
	/**
	 * outputstream
	 */
	private DataOutputStream out;

	/**
	 * abstraction layer on top of outputstream
	 */
	private ArgumentWriter argumentWriter;

	/**
	 * IMAP server answer
	 */
	public String answer;

	/**
	 * starting character of our client TAG
	 */
	private String userId = new String("A");
	/**
	 * id complements the "userId" and
	 * is increased everytime we send a command
	 */
	private int id = 0;
	/**
	 * idString combines the userId and the id
	 */
	private String idString;

	/**
	 *
	 */
	private String result;

	/**
	 * default constructor
	 * @see java.lang.Object#Object()
	 */
	public IMAPProtocol() {

	}

	/**
	 * Method openPort with default port
	 *
	 *
	 * @param host
	 * @return boolean
	 * @throws IOException
	 */
	public boolean openPort(String host) throws IOException {
		return openPort(host, DEFAULT_PORT);
	}

	/**
	 * Method openPort
	 *
	 *
	 * @param host		name of IMAP server
	 * @param port	    port of IMAP server
	 * @return boolean  true if connection was established correctly
	 * @throws IOException
	 */
	public boolean openPort(String host, int port) throws IOException {

		socket = new Socket(host, port);

		DebugInputStream debugInputStream =
			new DebugInputStream(socket.getInputStream(), System.out);
		in = new IMAPInputStream(debugInputStream);

		DebugOutputStream debugOutputStream =
			new DebugOutputStream(socket.getOutputStream(), System.out);

		out = new DataOutputStream(new BufferedOutputStream(debugOutputStream));

		argumentWriter = new ArgumentWriter(this);

		answer = in.readResponse(null);

		if (answer.startsWith("*"))
			return true;
		else
			return false;
	}

	/**
	 * Method generateIdentifier.
	 *
	 * generate client request ID
	 *
	 *
	 * @return String
	 */
	protected String generateIdentifier() {
		id++;
		idString = new String(userId + new Integer(id).toString());
		return idString;
	}

	/**
	 * Method getOutputStream.
	 * @return DataOutputStream
	 */
	public DataOutputStream getOutputStream() {
		return out;
	}

	/**
	 * Method sendString.
	 * @param s
	 * @param args
	 * @return String
	 * @throws Exception
	 */
	public String sendString(String s, Arguments args) throws Exception {

		String id = generateIdentifier();

		out.writeBytes(id + " " + s);

		if (args != null) {

			argumentWriter.write(args);
		}

		out.write(CRLF);
		out.flush();

		return id;
	}

	/**
	 * Method getResponse.
	 * @param worker
	 * @return IMAPResponse
	 * @throws Exception
	 */
	public IMAPResponse getResponse(WorkerStatusController worker)
		throws Exception {
		String answer = in.readResponse(worker);

		return new IMAPResponse(answer);
	}

	/**
	 * Method sendCommand.
	 * @param command
	 * @param args
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	protected synchronized IMAPResponse[] sendCommand(
		String command,
		Arguments args)
		throws Exception {
		List v = new Vector();
		boolean finished = false;
		String clientTag = null;
		IMAPResponse imapResponse = null;

		try {
			clientTag = sendString(command, args);
		} catch (IOException ex) {
			// disconnect exception
			ex.printStackTrace();

			v.add(IMAPResponse.BYEResponse);
		}

		while (!finished) {
			try {
				// we are passing "null" here, because we don't want
				// any status information printed
				imapResponse = getResponse(null);
			} catch (IOException ex) {
				// disconnect exception
				ex.printStackTrace();

				imapResponse = IMAPResponse.BYEResponse;
			}

			v.add(imapResponse);

			if (imapResponse.getStatus() == IMAPResponse.STATUS_BYE)
				finished = true;

			if (imapResponse.isTagged()
				&& imapResponse.getTag().equals(clientTag))
				finished = true;
		}

		IMAPResponse[] r = new IMAPResponse[v.size()];
		((Vector) v).copyInto(r);

		return r;

	}

	/**
	 * Method sendCommand.
	 * @param command
	 * @param args
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	protected synchronized IMAPResponse[] sendCommand(
		String command,
		Arguments args,
		WorkerStatusController worker)
		throws Exception {
		List v = new Vector();
		boolean finished = false;
		String clientTag = null;
		IMAPResponse imapResponse = null;

		try {
			clientTag = sendString(command, args);
		} catch (IOException ex) {
			// disconnect exception
			ex.printStackTrace();

			v.add(IMAPResponse.BYEResponse);
		}

		while (!finished) {
			try {
				imapResponse = getResponse(worker);
			} catch (IOException ex) {
				// disconnect exception
				ex.printStackTrace();

				imapResponse = IMAPResponse.BYEResponse;
			}

			v.add(imapResponse);

			if (imapResponse.getStatus() == IMAPResponse.STATUS_BYE)
				finished = true;

			if (imapResponse.isTagged()
				&& imapResponse.getTag().equals(clientTag))
				finished = true;
		}

		IMAPResponse[] r = new IMAPResponse[v.size()];
		((Vector) v).copyInto(r);

		return r;

	}

	/**
	 * Method sendCommand.
	 * @param command
	 * @param args
	 * @param count
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	protected synchronized IMAPResponse[] sendCommand(
		String command,
		Arguments args,
		int count,
		WorkerStatusController worker)
		throws Exception {
		List v = new Vector();
		boolean finished = false;
		String clientTag = null;
		IMAPResponse imapResponse = null;

		try {
			clientTag = sendString(command, args);
		} catch (IOException ex) {
			// disconnect exception
			ex.printStackTrace();

			v.add(IMAPResponse.BYEResponse);
		}

		worker.setProgressBarMaximum(count);

		int counter = 0;
		worker.setProgressBarValue(counter);

		while (!finished) {
			try {
				imapResponse = getResponse(worker);

				worker.setProgressBarValue(++counter);
			} catch (IOException ex) {
				// disconnect exception
				ex.printStackTrace();

				imapResponse = IMAPResponse.BYEResponse;
			}

			v.add(imapResponse);

			if (imapResponse.getStatus() == IMAPResponse.STATUS_BYE)
				finished = true;

			if (imapResponse.isTagged()
				&& imapResponse.getTag().equals(clientTag))
				finished = true;
		}

		IMAPResponse[] r = new IMAPResponse[v.size()];
		((Vector) v).copyInto(r);

		return r;

	}

	/**
	 * Method sendSimpleCommand.
	 * @param command
	 * @param args
	 * @throws Exception
	 */
	protected synchronized void sendSimpleCommand(
		String command,
		Arguments args)
		throws Exception {

		IMAPResponse[] r = sendCommand(command, args);

		notifyResponseHandler(r);

		handleResult(r[r.length - 1]);
	}

	/**
	 * Method handleResult.
	 * @param response
	 * @throws Exception
	 */
	public void handleResult(IMAPResponse response) throws Exception {
		if (response.isOK())
			return;
		else if (response.isNO())
			throw new CommandFailedException(response);
		else if (response.isBAD())
			throw new BadCommandException(response);
		else if (response.isBYE()) {
			// disconnected
			throw new DisconnectedException(response);
		}
	}

	/**
	 * Method notifyResponseHandler.
	 * @param responses
	 */
	/******************* response handler **********************/

	protected void notifyResponseHandler(IMAPResponse[] responses) {
		for (int i = 0; i < responses.length; i++) {

			IMAPResponse r = responses[i];
			//System.out.println("r-source="+r.getSource());

			//if ( r==null ) System.out.println("response==null");

			if ((r == null) || (r.isTagged()))
				continue;

			//System.out.println("-> handle response");

			handleResponse(r);
		}
	}

	/**
	 * Method handleResponse.
	 * @param r
	 */
	protected void handleResponse(IMAPResponse r) {
		//System.out.println("handleResponse");

		if (r.isBYE()) {
			// cleanup

			r = null;
			return;
		} else if (r.isOK()) {

			//System.out.println("response-code=" + r.getResponseCode());
			r = null;
			return;
		}

	}

	/**
	 * Method login.
	 * @param user
	 * @param password
	 * @throws Exception
	 */
	/**************** any state commands ***********************/

	public void login(String user, String password) throws Exception {

		Arguments args = new Arguments();
		args.add(user);
		args.add(password);

		sendSimpleCommand("LOGIN", args);

	}

	/**
	 * Method select.
	 * @param mailbox
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	/************************ authenticate state commands **************************/

	public IMAPResponse[] select(String mailbox) throws Exception {
		Arguments args = new Arguments();
		args.add(mailbox);

		IMAPResponse[] responses = sendCommand("SELECT", args);

		notifyResponseHandler(responses);

		// mailfolderinfo parsing
		MessageFolderInfo info = null;

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method fetchList.
	 * @param cmd
	 * @param reference
	 * @param pattern
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchList(
		String cmd,
		String reference,
		String pattern)
		throws Exception {
		Arguments args = new Arguments();
		args.add(reference);
		args.add(pattern);

		IMAPResponse[] responses = sendCommand(cmd, args);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method lsub.
	 * @param reference
	 * @param pattern
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] lsub(String reference, String pattern)
		throws Exception {
		return fetchList("LSUB", reference, pattern);
	}

	/**
	 * Method list.
	 * @param reference
	 * @param pattern
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] list(String reference, String pattern)
		throws Exception {
		return fetchList("LIST", reference, pattern);
	}

	/**
	 * Method create.
	 * @param mailbox
	 * @throws Exception
	 */
	public void create(String mailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(mailbox);

		sendSimpleCommand("CREATE", args);
	}

	/**
	 * Method delete.
	 * @param mailbox
	 * @throws Exception
	 */
	public void delete(String mailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(mailbox);

		sendSimpleCommand("DELETE", args);
	}

	/**
	 * Method rename.
	 * @param oldMailbox
	 * @param newMailbox
	 * @throws Exception
	 */
	public void rename(String oldMailbox, String newMailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(oldMailbox);
		args.add(newMailbox);

		sendSimpleCommand("RENAME", args);
	}

	/**
	 * Method subscribe.
	 * @param oldMailbox
	 * @throws Exception
	 */
	public void subscribe(String oldMailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(oldMailbox);

		sendSimpleCommand("SUBSCRIBE", args);
	}

	/**
	 * Method unsubscribe.
	 * @param oldMailbox
	 * @throws Exception
	 */
	public void unsubscribe(String oldMailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(oldMailbox);

		sendSimpleCommand("UNSUBSCRIBE", args);
	}

	/**
	 * Method append.
	 * @param mailBox
	 * @param messageSource
	 * @throws Exception
	 */
	public void append(String mailBox, String messageSource) throws Exception {

		Arguments args = new Arguments();
		args.add(mailBox);
		args.add(messageSource);

		sendSimpleCommand("APPEND", args);

	}

	/**
	 * Method fetch.
	 * @param item
	 * @param messageSet
	 * @param uid
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	/******************************** selected state commands *************************/

	public IMAPResponse[] fetch(String item, String messageSet, boolean uid)
		throws Exception {
		if (uid)
			return sendCommand(
				"UID FETCH " + messageSet + " (" + item + ")",
				null);
		else
			return sendCommand("FETCH " + messageSet + " (" + item + ")", null);
	}

	/**
	 * Method fetch.
	 * @param item
	 * @param messageSet
	 * @param uid
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetch(
		String item,
		String messageSet,
		boolean uid,
		WorkerStatusController worker)
		throws Exception {
		if (uid)
			return sendCommand(
				"UID FETCH " + messageSet + " (" + item + ")",
				null,
				worker);
		else
			return sendCommand(
				"FETCH " + messageSet + " (" + item + ")",
				null,
				worker);
	}
	/**
	 * Method fetch.
	 * @param item
	 * @param messageSet
	 * @param uid
	 * @param count
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetch(
		String item,
		String messageSet,
		boolean uid,
		int count,
		WorkerStatusController worker)
		throws Exception {
		if (uid)
			return sendCommand(
				"UID FETCH " + messageSet + " (" + item + ")",
				null,
				count,
				worker);
		else
			return sendCommand(
				"FETCH " + messageSet + " (" + item + ")",
				null,
				count,
				worker);
	}

	/**
	 * Method fetchUIDList.
	 * @param messageSet
	 * @param count
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchUIDList(
		String messageSet,
		int count,
		WorkerStatusController worker)
		throws Exception {

		IMAPResponse[] responses =
			fetch("UID", messageSet, false, count, worker);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method fetchFlagsList.
	 * @param messageSet
	 * @param count
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchFlagsList(
		String messageSet,
		int count,
		WorkerStatusController worker)
		throws Exception {

		IMAPResponse[] responses =
			fetch("FLAGS", messageSet, true, count, worker);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method fetchHeaderList.
	 * @param messageSet
	 * @param headerFields
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchHeaderList(
		String messageSet,
		String headerFields)
		throws Exception {

		ColumbaLogger.log.debug("messageSet=" + messageSet);
		ColumbaLogger.log.debug("headerFields=" + headerFields);

		IMAPResponse[] responses =
			fetch(
				"BODY.PEEK[HEADER.FIELDS (" + headerFields + ")]",
				messageSet,
				true);
		//IMAPResponse[] responses = fetch("ENVELOPE", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method fetchMimePartTree.
	 * @param messageSet
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchMimePartTree(String messageSet)
		throws Exception {

		IMAPResponse[] responses = fetch("BODYSTRUCTURE", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method fetchMimePart.
	 * @param messageSet
	 * @param address
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchMimePart(
		String messageSet,
		Integer[] address,
		WorkerStatusController worker)
		throws Exception {

		StringBuffer addressString =
			new StringBuffer(Integer.toString(address[0].intValue() + 1));
		for (int i = 1; i < Array.getLength(address); i++) {
			addressString.append('.');
			addressString.append(Integer.toString(address[i].intValue() + 1));
		}

		// changed BODY to BODY.PEEK
		// this is an alternative approach that does not
		// implicitly set the \Seen flag
		IMAPResponse[] responses =
			fetch("BODY.PEEK[" + addressString + "]", messageSet, true, worker);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method fetchMessageSource.
	 * @param messageSet
	 * @param worker
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] fetchMessageSource(
		String messageSet,
		WorkerStatusController worker)
		throws Exception {

		// changed BODY to BODY.PEEK
		// this is an alternative approach that does not
		// implicitly set the \Seen flag
		IMAPResponse[] responses =
			fetch("BODY.PEEK[]", messageSet, true, worker);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method storeFlags.
	 * @param messageSet
	 * @param flags
	 * @param enable
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] storeFlags(
		String messageSet,
		String flags,
		boolean enable)
		throws Exception {

		IMAPResponse[] responses = null;
		if (enable)
			responses =
				sendCommand(
					"UID STORE " + messageSet + " +FLAGS " + flags,
					null);
		else
			responses =
				sendCommand(
					"UID STORE " + messageSet + " +FLAGS " + flags,
					null);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
		 * Method removeFlags.
		 * @param messageSet
		 * @param flags
		 * @param enable
		 * @return IMAPResponse[]
		 * @throws Exception
		 */
	public IMAPResponse[] removeFlags(
		String messageSet,
		String flags,
		boolean enable)
		throws Exception {

		IMAPResponse[] responses = null;
		if (enable)
			responses =
				sendCommand(
					"UID STORE " + messageSet + " -FLAGS " + flags,
					null);
		else
			responses =
				sendCommand(
					"UID STORE " + messageSet + " -FLAGS " + flags,
					null);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method expunge.
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] expunge() throws Exception {

		IMAPResponse[] responses = sendCommand("EXPUNGE", null);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method search.
	 * @param searchString
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] search(Arguments args) throws Exception {

		IMAPResponse[] responses = sendCommand("UID SEARCH ALL", args);
		//IMAPResponse[] responses = sendCommand("UID SEARCH ", args);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] searchWithCharsetSupport(String charset, Arguments args)
		throws Exception {

		IMAPResponse[] responses =
			sendCommand("UID SEARCH CHARSET " + charset + " ALL", args);
			//sendCommand("UID SEARCH CHARSET " + charset + " ", args);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] search(String messageSet, Arguments args)
		throws Exception {

		IMAPResponse[] responses =
			sendCommand("UID SEARCH " + messageSet, args);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	/**
	 * Method copy.
	 * @param messageSet
	 * @param mailbox
	 * @return IMAPResponse[]
	 * @throws Exception
	 */
	public IMAPResponse[] copy(String messageSet, String mailbox)
		throws Exception {

		Arguments args = new Arguments();
		args.add(messageSet);
		args.add(mailbox);

		IMAPResponse[] responses = sendCommand("UID COPY", args);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

}

///////////////////////////////////////////////////////////////////////////
// $Log:$
///////////////////////////////////////////////////////////////////////////