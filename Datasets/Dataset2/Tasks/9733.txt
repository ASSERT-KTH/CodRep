start - 1 - lastEnd));

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

package org.columba.mail.folder.mbox;

import java.io.IOException;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;

import org.columba.ristretto.io.Source;
import org.columba.ristretto.parser.CharSequenceSearcher;

public class MboxParser {	
	
	public static MboxMessage[] parseMbox(Source mailboxSource) throws IOException {
		List messages = new LinkedList();

		CharSequenceSearcher searcher = new CharSequenceSearcher("From ");
		List boundaries = searcher.match(mailboxSource);

		Iterator it = boundaries.iterator();
		int start = ((Integer) it.next()).intValue();

		int lastEnd = findNext(mailboxSource, start + 5, '\n') + 1;

		int newUid = 0;

		while (it.hasNext()) {
			start = ((Integer) it.next()).intValue();
			messages.add(new MboxMessage(new Integer(newUid++), lastEnd,
					start - 1));
			lastEnd = findNext(mailboxSource, start + 5, '\n') + 1;
		}

		return (MboxMessage[]) messages.toArray(new MboxMessage[0]);
	}

	private static int findNext(Source source, int pos, char ch) {
		int result = -1;

		pos++;
		while (!source.isEOF()) {
			if (source.charAt(pos) == ch) {
				return pos;
			} else {
				pos++;
			}
		}

		return -1;
	}

}