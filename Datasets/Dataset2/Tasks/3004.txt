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

package org.columba.mail.pop3.protocol;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import org.columba.core.command.CommandCancelledException;
import org.columba.core.command.WorkerStatusController;
import org.columba.main.MainInterface;

public class POP3Protocol {
	private Socket socket;
	private BufferedReader in;
	private PrintWriter out;

	private boolean statuschecked;
	//public boolean connected;
	private String security;
	public String answer;
	private int logMethod;
	//private int totalMessages;
	//private int totalSize;

	private String selectedMessageSizeString;
	private int lineCount;
	private int selectedMessageSize;
	private String user;
	private String password;
	private String server;

	public static final int DEFAULT_PORT = 110;

	public static final int USER = 1;
	public static final int APOP = 2;

	public POP3Protocol(String user, String password, String server) {
		this.user = user;
		this.password = password;
		this.server = server;

		logMethod = USER;
	}

	public POP3Protocol() {
		logMethod = USER;
	}

	public void setLoginMethod(String str) {
		if (str.equalsIgnoreCase("USER"))
			logMethod = USER;
		else if (str.equalsIgnoreCase("APOP"))
			logMethod = APOP;
		else
			logMethod = USER;
	}

	public void sendString(String s) throws IOException {
		if (MainInterface.DEBUG.equals(Boolean.TRUE))
			System.out.println("CLIENT:" + s);

		out.print(s + "\r\n");
		out.flush();
	}

	public String getServerResponse() throws IOException {
		return answer;
	}

	public boolean getAnswer() throws IOException {

		answer = in.readLine();

		if (MainInterface.DEBUG.equals(Boolean.TRUE))
			System.out.println("SERVER:" + answer);

		return (answer.startsWith("+OK"));
	}

	public void getNextLine() throws IOException {
		answer = in.readLine();

		if (MainInterface.DEBUG.equals(Boolean.TRUE))
			System.out.println("SERVER:" + answer);
	}

	/*
	public boolean openPort(String host) throws IOException {
		return openPort(host, DEFAULT_PORT);
	}
	
	public boolean openPort() throws IOException {
		return openPort(server, DEFAULT_PORT);
	}
	*/

	public boolean openPort(String host, int port) throws IOException {
		socket = new Socket(host, port);

		// All Readers shall use ISO8859_1 Encoding in order to ensure
		// 1) ASCII Chars represented right to ensure working parsers
		// 2) No mangling of the received bytes to be able to convert
		//    the received bytes to another charset

		in =
			new BufferedReader(
				new InputStreamReader(socket.getInputStream(), "ISO8859_1"));
		out =
			new PrintWriter(
				new OutputStreamWriter(socket.getOutputStream(), "ISO8859_1"));

		//connected = true;
		security = null;

		if (getAnswer()) {
			int i = answer.indexOf("<");
			if (i != -1) {
				security = answer.substring(i, answer.indexOf(">") + 1);

			}

			return true;
		} else
			return false;
	}

	public int getSize() {
		return selectedMessageSize;
	}

	public String getSizeString() {
		return selectedMessageSizeString;
	}

	public boolean login(String u, String pass) throws IOException {

		switch (logMethod) {

			case USER :
				return userPass(u, pass);

			case APOP :
				return apop(u, pass);
		}

		return false;
	}

	/*
	public boolean login() throws IOException {
		switch (logMethod) {
			case USER :
				{
	
					return userPass(user, password);
				}
	
			case APOP :
				{
	
					return apop(user, password);
				}
		}
	
		return false;
	}
	*/
	private boolean userPass(String usr, String pass) throws IOException {
		sendString("USER " + usr);
		if (getAnswer()) {
			sendString("PASS " + pass);
			return getAnswer();
		}
		return false;
	}

	private boolean apop(String user, String pass) throws IOException {
		if (security != null) {
			try {
				MessageDigest md = MessageDigest.getInstance("MD5");
				md.update(security.getBytes());
				if (pass == null)
					pass = "";
				byte[] digest = md.digest(pass.getBytes());
				sendString("APOP " + user + " " + digestToString(digest));
				return getAnswer();
			} catch (NoSuchAlgorithmException e) {
			}
		}
		return false;
	}

	public boolean logout() throws IOException {

		sendString("QUIT");

		//in.close();
		//out.close();
		//socket.close();
		return getAnswer();

	}

	public void close() throws IOException {
		in.close();
		out.close();
		socket.close();
	}

	/*
	public int getTotalMessages() throws IOException {
		
	
		if (!checkStat()) {
			return -1;
		}
	
		return totalMessages;
	}
	
	public int getTotalSize() throws IOException {
		if (!statuschecked) {
			if (!checkStat()) {
				return -1;
			}
		}
		return totalSize;
	}
	*/

	public int getLineCount() {
		return lineCount;
	}

	public int fetchMessageCount() throws IOException {
		String dummy;

		sendString("STAT");
		if (getAnswer()) {
			try {
				dummy = answer.substring(answer.indexOf(' ') + 1);

				int totalMessages =
					Integer.parseInt(dummy.substring(0, dummy.indexOf(' ')));

				dummy = dummy.substring(dummy.indexOf(' ') + 1);

				//totalSize = Integer.parseInt(dummy);

				statuschecked = true;
				return totalMessages;

			} catch (NumberFormatException e) {
			}
		}

		return -1;
	}

	public String fetchMessageSizes() throws IOException {
		int size = -1;
		String dummy;
		StringBuffer buf = new StringBuffer();

		sendString("LIST");
		if (getAnswer()) {

			getNextLine();
			int i = 0;
			while (!answer.equals(".")) {
				buf.append(answer + "\n");
				/*
				try {
					size =
						Integer.parseInt(
							answer.substring(answer.indexOf(' ') + 1));
				} catch (NumberFormatException e) {
				}
				
				messageSizes.addElement(new Integer(size));
				
				i++;
				*/
				getNextLine();
			}

			return buf.toString();

		} else
			System.out.println("getAnswer == false");

		return null;
	}

	/*
	public String getMessage(int messageNumber) throws IOException
	{
	StringBuffer messageBuffer = new StringBuffer();
	    lineCount=0;
	
	    //System.out.println(lineCount);
	
	
	if( connected ) {
	    sendString("RETR "+messageNumber);
	    if ( getAnswer() ) {
		getNextLine();
		while( !answer.equals(".") ) {
		    messageBuffer.append(answer+"\n");
		    getNextLine();
	                lineCount++;
		}
	    }
	}
	
	return messageBuffer.toString();
	}
	*/

	public String fetchUIDList(
		int totalMessageCount,
		WorkerStatusController worker)
		throws Exception {
		StringBuffer buffer = new StringBuffer();
		Integer parser = new Integer(0);
		int progress = 0;

		sendString("UIDL");
		if (getAnswer()) {

			worker.setProgressBarMaximum(totalMessageCount);
			worker.setProgressBarValue(0);
			getNextLine();
			while (!answer.equals(".")) {
				//System.out.println("SERVER: "+ answer );
				if (worker.cancelled() == true)
					throw new CommandCancelledException();
				buffer.append(answer + "\n");
				progress++;

				worker.setProgressBarValue(progress);
				getNextLine();
			}
		}

		return buffer.toString();
	}

	public String fetchMessage(
		String messageNumber,
		WorkerStatusController worker)
		throws Exception {
		StringBuffer messageBuffer = new StringBuffer();
		Integer parser = new Integer(0);
		int progress = 0;
		String sizeline = new String();
		int test;
		boolean progressBar = true;

		sendString("RETR " + messageNumber);
		if (getAnswer()) {
			/*
			//selectedMessageSizeString = answer.substring(3, answer.indexOf(' ',4) );
			
			try
			{
			
			    selectedMessageSize = parser.parseInt( answer.substring(3, answer.indexOf(' ',4) ).trim());
			    //worker.setProgressBarMaximum( selectedMessageSize );
			}
			catch (NumberFormatException ex )
			{
			    System.out.println( ex.getMessage() );
			    //progressBar = false;
			}
			*/

			getNextLine();
			while (!answer.equals(".")) {

				if (worker.cancelled() == true)
					throw new CommandCancelledException();

				messageBuffer.append(answer + "\n");

				progress = answer.length() + 2;

				worker.incProgressBarValue(progress);

				getNextLine();
			}
			/*
			if ( progressBar == true )
			    worker.setProgressBarValue( selectedMessageSize );
			    */

		}

		return messageBuffer.toString();
	}

	public String getMessageHeader(int messageNumber) throws IOException {
		StringBuffer messageBuffer = new StringBuffer();
		Integer parser = new Integer(0);
		//int progress = 0;

		sendString("TOP " + messageNumber + " " + 0);
		if (getAnswer()) {
			getNextLine();
			while (!answer.equals(".")) {
				messageBuffer.append(answer + "\n");
				getNextLine();
			}
		}

		return messageBuffer.toString();
	}

	public boolean deleteMessage(int messageNumber) throws IOException {

		sendString("DELE " + messageNumber);
		if (getAnswer())
			return true;

		return false;
	}

	public boolean noop() throws IOException {

		sendString("NOOP");
		if (getAnswer())
			return true;

		return false;
	}

	public boolean reset() throws IOException {

		sendString("RSET");
		if (getAnswer())
			return true;

		return false;
	}

	private String digestToString(byte[] digest) {
		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < 16; ++i) {
			if ((digest[i] & 0xFF) < 0x10) {
				sb.append("0");
			}
			sb.append(Integer.toHexString(digest[i] & 0xFF));
		}
		return sb.toString();
	}
}