IMAPResponse r = protocol.getResponse();

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
package org.columba.mail.imap.protocol;

import java.io.OutputStream;

import org.columba.mail.imap.IMAPResponse;

/**
 * @author freddy
 *
 * Helper class which writes <class>Arguments</class> to
 * a <class>DataOutputStream</class>
 * 
 * 
 * 
 *   Following a short paragraph of RFC2060 IMAP:
 * 
 *
 *   A string is in one of two forms: literal and quoted string.  The
 *   literal form is the general form of string.  The quoted string form
 *   is an alternative that avoids the overhead of processing a literal at
 *   the cost of limitations of characters that can be used in a quoted
 *   string.
 *
 *   A literal is a sequence of zero or more octets (including CR and LF),
 *   prefix-quoted with an octet count in the form of an open brace ("{"),
 *   the number of octets, close brace ("}"), and CRLF.  In the case of
 *   literals transmitted from server to client, the CRLF is immediately
 *   followed by the octet data.  In the case of literals transmitted from
 *   client to server, the client MUST wait to receive a command
 *   continuation request (described later in this document) before
 *   sending the octet data (and the remainder of the command).
 *
 *   A quoted string is a sequence of zero or more 7-bit characters,
 *   excluding CR and LF, with double quote (<">) characters at each end.
 *
 *   The empty string is represented as either "" (a quoted string with
 *   zero characters between double quotes) or as {0} followed by CRLF (a
 *   literal with an octet count of 0).
 *
 *      Note: Even if the octet count is 0, a client transmitting a
 *      literal MUST wait to receive a command continuation request.
 * 
 */
public class ArgumentWriter {

	protected final byte[] openingCurlyBracket = { '{' };//new String("{").getBytes("US-ASCII");
	protected final byte[] closingCurlyBracket = { '}' };
	
	protected final byte[] newline = { '\r', '\n' };
	
	protected OutputStream output;
	protected IMAPProtocol protocol;
	
	static boolean nested = false; 
	/**
	 * Constructor for ArgumentWriter.
	 */
	public ArgumentWriter(IMAPProtocol protocol) {

		this.protocol = protocol;

		this.output = protocol.getOutputStream();
		
		nested = false;

	}
	
	/*
	 * 
	 * this is only used by testcases
	 * 
	 */
	public ArgumentWriter( OutputStream output )
	{
		this.output = output;
		
		nested = false;
	}

	public void write(Arguments args) throws Exception {
		/*
		if (args.count() == 0)
			return;
		*/
		
		for (int i = 0; i < args.count(); i++) {
			Object value = args.get(i);
			
			if (args.count() > 0)
			{ 
				if ( nested == false)
					output.write(' ');
				else
				{
					if ( i>0 )
					output.write(' ');
				}
			}

			if (value instanceof ByteString) {

				writeString(((ByteString) value).getBytes());
			} else if (value instanceof byte[]) {
				writeBytes((byte[]) value);
			} else if (value instanceof Atom) {
				writeAtom((Atom) value);
			} else if (value instanceof Arguments) {
				// support for nested arguments
				// -> this is a must have for more complex SEARCH requests
				output.write('('); // open parans
				nested = true;
				write((Arguments) value);
				output.write(')'); // close params
				nested = false;
				output.flush();
				
			}

		}
		
		output.flush();

	}

	/**
	 * send String (converted to byte[]) and decide:
	 *  - do we have to send it as literal
	 *  - do we have to quote this string, because of 
	 *    special escape characters
	 * 
	 * @param data
	 * @throws Exception
	 */
	protected void writeString(byte[] data) throws Exception {
		int length = data.length;
		boolean needsQuoting = false;
		boolean hasEscapeCharacters = false;

		// If lengthgth is greater than 1024 bytes, send as literal
		if (length > 1024) {
			writeBytes(data);
			return;
		}

		// if length==0, send as quoted string
		if (length == 0)
			needsQuoting = true;

		byte b;

		// (1) 
		// we have to take a look at every byte to see
		// if its an escape character
		// 
		// if it has escape characters, we have to quote the string
		//
		//   args#            1    2        3
		// example: CLIENT: LOGIN user my%{passwo\rd
		//
		// the client-request #3 contains escape characters,
		// which are already used by the IMAP protocol
		//
		// we have to quote "my%$passwo/rd"
		//
		// (2) 
		// we have to search for NUL, CR or LF characters, meaning
		// that this is a complete string we want to send
		// to the SERVER.
		// If we don't send this as literal, SERVER thinks, when
		// seeing CR/LF, that the CLIENT request is finished

		for (int i = 0; i < length; i++) {
			b = data[i];

			// search for problem (2)
			if (b == '\0' || b == '\r' || b == '\n' || ((b & 0xff) > 0177)) {
				// NUL, CR or LF characters found
				//  -> send as literal
				writeBytes(data);
				return;
			}

			// search for problem (1)
			if (b == '*'
				|| b == '%'
				|| b == '('
				|| b == ')'
				|| b == '{'
				|| b == '"'
				|| b == '\\'
				|| ((b & 0xff) <= ' ')) {
				needsQuoting = true;
				if (b == '"' || b == '\\')
					hasEscapeCharacters = true;
			}
		}

		// begin quoted string
		if (needsQuoting)
			output.write('"');

		if (hasEscapeCharacters) {

			for (int i = 0; i < length; i++) {
				b = data[i];
				if (b == '"' || b == '\\')
					output.write('\\');
				output.write(b);
			}
		} else
			output.write(data);

		// end quoted string
		if (needsQuoting)
			output.write('"');
	}

	/**
	 * send byte[] as literal
	 * 
	 * 
	 * @param data
	 * @throws Exception
	 */
	protected void writeBytes(byte[] data) throws Exception {
		output.write(openingCurlyBracket);
		output.write(Integer.toString(data.length).getBytes("ISO-8859-1"));
		output.write(closingCurlyBracket);
		output.write(newline);
		
		output.flush();

		for (;;) {
			IMAPResponse r = protocol.getResponse(null);
			if (r.isCONTINUATION())
				break;
		}

		output.write(data);
	}

	/**
	 * 
	 * send US-ASCII string
	 * 
	 * @param s
	 * @throws Exception
	 */
	protected void writeAtom(Atom atom) throws Exception {
		output.write(atom.getString().getBytes("ISO-8859-1"));
	}

}