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

package org.columba.mail.smtp;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.io.StringWriter;
import java.net.Socket;
import java.util.Hashtable;
import java.util.Vector;

import org.columba.core.command.WorkerStatusController;
import org.columba.mail.coder.Base64Decoder;
import org.columba.mail.coder.Base64Encoder;
import org.columba.main.MainInterface;

public class SMTPProtocol {
	public final static int SMTP = 0;
	public final static int ESMTP = 1;

	private String host;
	private String localHost;
	private int port;

	private Socket socket;
	private DataOutputStream out;
	private BufferedReader in;

	private Hashtable capabilities;

	private Base64Decoder decoder;
	private Base64Encoder encoder;

	private boolean isEsmtp;

	public SMTPProtocol(String hostName, int portNr) throws Exception {
		capabilities = new Hashtable();

		decoder = new Base64Decoder();
		encoder = new Base64Encoder();

		host = hostName;
		port = portNr;

	}

	public SMTPProtocol(String hostName) {
		capabilities = new Hashtable();

		decoder = new Base64Decoder();
		encoder = new Base64Encoder();

		host = hostName;
		port = 25;

	}

	private void checkAnswer(String answer, String start)
		throws SMTPException {
		if (MainInterface.DEBUG.equals(Boolean.TRUE))
			System.out.println("SERVER:" + answer);

		if (!answer.startsWith(start)) {
			throw (new SMTPException(answer));
		}
	}

	private void sendString(String str) throws Exception {
		if (MainInterface.DEBUG.equals(Boolean.TRUE))
			System.out.println("CLIENT:" + str);

		out.writeBytes(str + "\r\n");
		out.flush();
	}

	public void authenticate(
		String username,
		String password,
		String loginMethod)
		throws Exception {
		String answer;
		StringWriter decoded = new StringWriter();
		String methods = (String) capabilities.get("AUTH");

		System.out.println("esmtp login-method=" + loginMethod);

		// Try LOGIN
		if (loginMethod.equalsIgnoreCase("LOGIN") == true) {

			sendString("AUTH LOGIN");
			answer = in.readLine();

			checkAnswer(answer, "3");

			answer = answer.substring(4);

			sendString(encoder.encode(username, null));

			answer = in.readLine();
			checkAnswer(answer, "3");

			answer = answer.substring(4);

			sendString(encoder.encode(password, null));

			checkAnswer(in.readLine(), "2");
		} else if (loginMethod.equalsIgnoreCase("PLAIN") == true) {

			sendString("AUTH PLAIN");

			answer = in.readLine();

			checkAnswer(answer, "3");

			String authenticateID = new String("");

			StringBuffer buf = new StringBuffer();
			buf.append(authenticateID);
			buf.append('\0');
			buf.append(username);
			buf.append('\0');
			buf.append(password);

			sendString(encoder.encode(buf.toString(), null));

			checkAnswer(in.readLine(), "2");

		} else {
			throw (new SMTPException("Unsupported authentication type!"));
		}

	}

	public int openPort() throws Exception {
		String answer;

		socket = new Socket(host, port);
		out = new DataOutputStream(socket.getOutputStream());
		in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

		checkAnswer(in.readLine(), "2");

		// we send a FQDN EHLO/HELO that works
		// sending the actual hostname could be considered spyware
		// and it doesn't work with machines without a FQDN name,
		// or using NAT or a TCP tunnel to another host
		sendString("EHLO localhost.localdomain");

		answer = in.readLine();

		if (answer.startsWith("2")) {

			isEsmtp = true;
			getCapabilities();

			return ESMTP;
		}

		isEsmtp = false;

		sendString("HELO localhost.localdomain");

		checkAnswer(in.readLine(), "2");

		return SMTP;
	}

	private void getCapabilities() throws Exception {
		String answer;
		String key;
		String value;
		int separator;

		answer = in.readLine();

		while (answer != null) {
			if (answer.startsWith("2")) {

				separator = answer.indexOf(' ');
				if (separator > 4) {
					key = answer.substring(4, separator);
					value = answer.substring(separator + 1);
					capabilities.put(key, value);
				} else
					capabilities.put(answer.substring(4), new String());

				if (answer.charAt(3) != '-')
					break;
			} else {
				throw (new SMTPException(answer));
			}

			answer = in.readLine();
			checkAnswer(answer, "2");
		}
	}

	public void setupMessage(String from, Vector to) throws Exception {
		int anzAdresses;

		anzAdresses = to.size();

		sendString("MAIL FROM: " + from);

		checkAnswer(in.readLine(), "2");

		for (int i = 0; i < anzAdresses; i++) {
			sendString("RCPT TO: " + to.get(i));

			checkAnswer(in.readLine(), "2");
		}
	}

	public void sendMessage(String message, WorkerStatusController workerStatusController) throws Exception {
		BufferedReader messageReader =
			new BufferedReader(new StringReader(message));
		String line;

		int progressCounter = 0;

		workerStatusController.setDisplayText("Sending Message...");
		workerStatusController.setProgressBarMaximum(message.length()/1024);
		
		out.writeBytes("DATA\r\n");
		out.flush();

		checkAnswer(in.readLine(), "3");

		line = messageReader.readLine();

		while (line != null) {
			progressCounter += line.length();
			if( progressCounter > 1024 ) { 
				workerStatusController.incProgressBarValue();
				progressCounter %= 1024;
			}

			if (line.equals("."))
				line = new String(" .");

			out.writeBytes(line + "\r\n");
			line = messageReader.readLine();
		}
		out.writeBytes("\r\n.\r\n");
		out.flush();

		checkAnswer(in.readLine(), "2");
	}

	public void closePort() throws Exception {
		out.writeBytes("QUIT\r\n");
		out.flush();

		checkAnswer(in.readLine(), "2");
	}
}