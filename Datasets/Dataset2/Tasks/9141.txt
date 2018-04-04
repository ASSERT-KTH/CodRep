rightIndex = source.lastIndexOf(")");

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
package org.columba.mail.imap.parser;

import org.columba.mail.imap.IMAPResponse;

/**
 * @author fdietz
 *
 * See <code>MimePartParserTest</code> for examples of sources
 * 
 */
public class MimePartParser {

	public static String parse(IMAPResponse[] responses) {
		String source = responses[0].getSource();

		int newLine = source.indexOf("\n");
		
		if  ( newLine == -1 )
		{
			// there's not newline
			// -> one line message
			// example:
			// * 133 FETCH (UID 133 BODY[1] \"da!\")
			// note: message is enclosed with " characters
			int leftIndex = source.indexOf("\"");
			int rightIndex = source.lastIndexOf("\"");
			
			return source.substring(leftIndex+1, rightIndex);
		}
		
		boolean uidAtBeginning = false;
		int uidIndex = source.indexOf("(UID");
		if (uidIndex != -1)
			uidAtBeginning = true;

		int leftIndex = source.indexOf('}');

		int rightIndex = -1;
		if (uidAtBeginning) {
			// message is ending with "\n)"
			rightIndex = source.length() - 2;
		} else {
			// message is ending with " UID 17)"
			// note the whitespace before "UID" !
			rightIndex = source.lastIndexOf("UID") - 1;
		}

		// skip "} \n"
		return source.substring(leftIndex + 3, rightIndex);
	}

}