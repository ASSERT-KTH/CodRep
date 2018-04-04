IMAPResponse[] responses = sendCommand("UID COPY", args);

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

package org.columba.mail.imap.protocol;

import java.io.BufferedOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.lang.reflect.Array;
import java.net.Socket;
import java.util.Vector;

import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.folder.MessageFolderInfo;
import org.columba.mail.imap.IMAPResponse;

public class IMAPProtocol {
	public static final int DEFAULT_PORT = 143;

	private static final byte[] CRLF = {(byte) '\r', (byte) '\n' };

	private Socket socket;
	private IMAPInputStream in;
	private DataOutputStream out;

	private ArgumentWriter argumentWriter;

	public String answer;

	private String userId = new String("A");
	private int id = 0;
	private String idString;

	private String result;

	public IMAPProtocol() {

	}

	public boolean openPort(String host) throws IOException {
		return openPort(host, DEFAULT_PORT);
	}

	public boolean openPort(String host, int port) throws IOException {

		socket = new Socket(host, port);

		in = new IMAPInputStream(socket.getInputStream());
		out =
			new DataOutputStream(
				new BufferedOutputStream(socket.getOutputStream()));

		argumentWriter = new ArgumentWriter(this);

		answer = in.readResponse();
		ColumbaLogger.log.debug("SERVER:" + answer);

		if (answer.startsWith("*"))
			return true;
		else
			return false;
	}

	protected String generateIdentifier() {
		id++;
		idString = new String(userId + new Integer(id).toString());
		return idString;
	}

	public DataOutputStream getOutputStream() {
		return out;
	}

	public String sendString(String s, Arguments args) throws Exception {
		StringBuffer buf = new StringBuffer();

		String id = generateIdentifier();

		out.writeBytes(id + " " + s);

		if (args != null) {

			argumentWriter.write(args);
		}

		out.write(CRLF);
		out.flush();

		//ColumbaLogger.log.debug("CLIENT:" + buf.toString());

		return id;
	}

	public IMAPResponse getResponse() throws Exception {
		String answer = in.readResponse();

		ColumbaLogger.log.debug("SERVER:" + answer);

		return new IMAPResponse(answer);
	}

	protected synchronized IMAPResponse[] sendCommand(
		String command,
		Arguments args)
		throws Exception {
		Vector v = new Vector();
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
				imapResponse = getResponse();
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
		v.copyInto(r);

		return r;

	}

	protected synchronized void sendSimpleCommand(
		String command,
		Arguments args)
		throws Exception {

		IMAPResponse[] r = sendCommand(command, args);

		notifyResponseHandler(r);

		handleResult(r[r.length - 1]);
	}

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

	/**************** any state commands ***********************/

	public void login(String user, String password) throws Exception {

		Arguments args = new Arguments();
		args.add(user);
		args.add(password);

		sendSimpleCommand("LOGIN", args);

	}

	/************************ authenticate state commands **************************/

	public MessageFolderInfo select(String mailbox) throws Exception {
		Arguments args = new Arguments();
		args.add(mailbox);

		IMAPResponse[] responses = sendCommand("SELECT", args);

		notifyResponseHandler(responses);

		// mailfolderinfo parsing
		MessageFolderInfo info = null;

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return info;
	}

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

	public IMAPResponse[] lsub(String reference, String pattern)
		throws Exception {
		return fetchList("LSUB", reference, pattern);
	}

	public IMAPResponse[] list(String reference, String pattern)
		throws Exception {
		return fetchList("LIST", reference, pattern);
	}

	public void create(String mailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(mailbox);

		sendSimpleCommand("CREATE", args);
	}

	public void delete(String mailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(mailbox);

		sendSimpleCommand("DELETE", args);
	}

	public void rename(String oldMailbox, String newMailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(oldMailbox);
		args.add(newMailbox);

		sendSimpleCommand("RENAME", args);
	}

	public void subscribe(String oldMailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(oldMailbox);

		sendSimpleCommand("SUBSCRIBE", args);
	}

	public void unsubscribe(String oldMailbox) throws Exception {

		Arguments args = new Arguments();
		args.add(oldMailbox);

		sendSimpleCommand("UNSUBSCRIBE", args);
	}

	public void append(String mailBox, String messageSource) throws Exception {

		Arguments args = new Arguments();
		args.add(mailBox);
		args.add(messageSource);

		sendSimpleCommand("APPEND", args);

	}

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

	public IMAPResponse[] fetchUIDList(String messageSet) throws Exception {

		IMAPResponse[] responses = fetch("UID", messageSet, false);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] fetchFlagsList(String messageSet) throws Exception {

		IMAPResponse[] responses = fetch("FLAGS", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] fetchHeaderList(String messageSet, String headerFields) throws Exception {

		IMAPResponse[] responses = fetch("BODY[HEADER.FIELDS ("+headerFields+")]", messageSet, true);
		//IMAPResponse[] responses = fetch("ENVELOPE", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] fetchMimePartTree(String messageSet)
		throws Exception {

		IMAPResponse[] responses = fetch("BODYSTRUCTURE", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] fetchMimePart(String messageSet, Integer[] address)
		throws Exception {

		StringBuffer addressString =
			new StringBuffer(Integer.toString(address[0].intValue() + 1));
		for (int i = 1; i < Array.getLength(address); i++) {
			addressString.append('.');
			addressString.append(Integer.toString(address[i].intValue() + 1));
		}

		IMAPResponse[] responses =
			fetch("BODY[" + addressString + "]", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] fetchMessageSource(String messageSet)
		throws Exception {

		IMAPResponse[] responses = fetch("BODY[]", messageSet, true);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

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

	public IMAPResponse[] expunge() throws Exception {

		IMAPResponse[] responses = sendCommand("EXPUNGE", null);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

	public IMAPResponse[] search(String searchString) throws Exception {

		IMAPResponse[] responses =
			sendCommand("UID SEARCH " + searchString, null);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}
	
	public IMAPResponse[] copy( String messageSet, String mailbox) throws Exception {
		
		Arguments args = new Arguments();
		args.add(messageSet);
		args.add(mailbox);
		
		IMAPResponse[] responses = sendCommand("COPY", args);

		notifyResponseHandler(responses);

		IMAPResponse r = responses[responses.length - 1];

		handleResult(r);

		return responses;
	}

}