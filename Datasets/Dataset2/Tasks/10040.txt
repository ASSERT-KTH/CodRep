"--no-secmem-warning --batch --no-tty --digest-algo %digest-algo% --verify %sigfile% -" };

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
package org.columba.mail.pgp;

import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;


/**
 * The special class witch handles the commandline parameters to sign, verify,
 * encrypt and decrypt messages with the gnu pgp tool named gpg.
 * @author waffel
 *
 */

public class GnuPGUtil extends DefaultUtil {
	// For signing we use the SHA1 algo as digest
    //	--textmode (textmode signature - not binary!!), --armor, --digest-algo SHA (we use SHA1 as default)
	static String[] cmd =
		{
			"--batch --no-tty --passphrase-fd 0 -d",
			"--no-secmem-warning --no-greeting --batch --no-tty --armor --output - --encrypt --group recipientgroup=%recipients%  -r recipientgroup",		
			"--no-secmem-warning --no-greeting --batch --digest-algo SHA1 --yes --no-tty --armor --textmode --passphrase-fd 0 --output - --detach-sign -u %user% ",
			"--no-secmem-warning --batch --no-tty --digest-algo SHA1 --verify %sigfile% -" };

	/* (non-Javadoc)
	 * @see org.columba.mail.pgp.DefaultUtil#getRawCommandString(int)
	 */
	protected String[] getRawCommandString(int type) {
		List ret = new ArrayList();
		StringTokenizer strToken = new StringTokenizer(cmd[type], " ");
		while (strToken.hasMoreTokens()) {
			ret.add(strToken.nextToken());
		}
		return (String[]) ret.toArray(new String[0]);
	}

	/**
	 * every line of the error stream starts with "gpg"; remove these characters
	 */
	protected String parse(String s) {
		StringBuffer str = new StringBuffer(s);
		// remove on the start position of the string the "gpg:" string

		int pos = 0;
		if (pos + 3 < str.length()) {
			if ((str.charAt(pos) == 'g')
				&& (str.charAt(pos + 1) == 'p')
				&& (str.charAt(pos + 2) == 'g')
				&& (str.charAt(pos + 3) == ':')) {
				str.delete(pos, pos + 4);
			}
		}

		pos++;
		// remove on each beginning of an new line the start string "gpg:" from this line
		while (pos < str.length()) {
			if (str.charAt(pos) == '\n') {
				pos++;
				if (pos + 3 < str.length()) {
					if ((str.charAt(pos) == 'g')
						&& (str.charAt(pos + 1) == 'p')
						&& (str.charAt(pos + 2) == 'g')
						&& (str.charAt(pos + 3) == ':')) {
						str.delete(pos, pos + 4);
					}
				}
			}

			pos++;
		}

		return str.toString();
	}

}