hashTable = new Hashtable(20);

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

package org.columba.mail.message;

import java.util.Enumeration;
import java.util.Hashtable;

/**
 * represents a Rfc822-compliant header
 * every headeritem is saved in a hashtable-structure
 * generally every headeritem is a string,
 * but for optimization reasons some items
 * are going to change to for example a Date class
 *
 * we added these items:
 *  - a date object
 *  - shortfrom, a parsed from
 *  - alreadyfetched, Boolean
 *  - pop3uid, String
 *  - uid, String
 *  - size, Integer
 *  - attachment, Boolean
 *  - priority, Integer
 */

public class Rfc822Header implements HeaderInterface {

	public static final int ALL = 0;
	public static final int NORMAL = 1;
	public static final int BRIEF = 2;
	public static final int USER_DEF = 3;

	// this hashtable stores all headeritems
	protected Hashtable hashTable;

	// do we need this variables anymore ??
	private String mimeVer = new String();

	// standard constructor
	public Rfc822Header() {
		hashTable = new Hashtable();

	}

	public Flags getFlags() {
		return new Flags(this);
	}
	
	public int count()
	{
		return hashTable.size();
		
	}

	// returns the header as given from mailserver
	// the items are split by \n
	public String getHeader() {
		Enumeration keys;
		StringBuffer output = new StringBuffer();
		String aktKey;

		keys = hashTable.keys();

		while (keys.hasMoreElements()) {
			aktKey = (String) keys.nextElement();

			if (aktKey.indexOf("columba") == -1) {
				output.append(aktKey);
				output.append(": ");

				output.append(hashTable.get(aktKey));

				output.append("\n");
			}
		}

		return output.toString();
	}

	public void setHashtable(Hashtable h) {
		hashTable = h;
	}

	public Hashtable getHashtable() {
		return hashTable;
	}

	// return headeritem
	public Object get(String s) {
		
		
		Object result = null;

		//  BUGFIX #660269 
		//   -> email-headers should start with upper-case letters
		//   -> it is wrong to use the lower-case string 

		String lowerCaseKey = s.toLowerCase();
		
		// does this item exist?
		if (hashTable.containsKey(s) == true) {
			result = hashTable.get(s);
		}
		else if ( hashTable.containsKey(lowerCaseKey) == true )
		{
			result = hashTable.get(lowerCaseKey);
			//ColumbaLogger.log.debug("using lowerCase key:"+lowerCaseKey);
		}
		
		/*
		else
			ColumbaLogger.log.debug("key not found:"+s);
		*/
		return result;
	}

	// set headeritem
	public void set(String s, Object o) {

		
		
		// BUGFIX #660269 
		//   -> email-headers should start with upper-case letters
		//   -> it is wrong to use the lower-case string 

		//s = s.toLowerCase();

		if ((s != null) && (o != null))
			hashTable.put(s, o);
	}

	public void setMimeVer(String par) {
		mimeVer = par;
	}

	public String getMimeVer() {
		return mimeVer;
	}

	public String getHeaderEntry(String type) {
		StringBuffer output = new StringBuffer(type);

		if (type.equals("from")) {
			output.append(" : ");
			output.append(get("From"));
			output.append('\n');
			return output.toString();
		}
		if (type.equals("to")) {
			output.append(" : ");
			output.append(get("To"));
			output.append('\n');
			return output.toString();
		}
		if (type.equals("cc")) {
			output.append(" : ");
			output.append(get("Cc"));
			output.append('\n');
			return output.toString();
		}
		if (type.equals("bcc")) {
			output.append(" : ");
			output.append(get("Bcc"));
			output.append('\n');
			return output.toString();
		}
		if (type.equals("date")) {
			output.append(" : ");
			output.append(get("Date"));
			output.append('\n');
			return output.toString();
		}
		if (type.equals("subject")) {
			output.append(" : ");
			output.append(get("Subject"));
			output.append('\n');
			return output.toString();
		}

		return null;
	}

	public String getHeaderInfo(int mode) {
		return null;
	}

	public Object clone() {
		Rfc822Header header = new Rfc822Header();
		header.setHashtable((Hashtable) hashTable.clone());

		return header;
	}

	public void printDebug() {
		for (Enumeration keys = hashTable.keys(); keys.hasMoreElements();) {
			String key = (String) keys.nextElement();

			Object value = hashTable.get(key);

			System.out.println("key=" + key + " value=" + value.toString());
		}

	}

}