private static final String fileRegexp = "[0-9]+";

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
package org.columba.mail.folder.mh;

import java.io.File;
import java.io.FileFilter;

import org.apache.oro.text.regex.MalformedPatternException;
import org.apache.oro.text.regex.Pattern;
import org.apache.oro.text.regex.PatternMatcher;
import org.apache.oro.text.regex.Perl5Compiler;
import org.apache.oro.text.regex.Perl5Matcher;

/**
 * @author timo
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class MHMessageFileFilter implements FileFilter {
	
	private static final String fileRegexp = "[0-9]+~*"; 
	
	protected static MHMessageFileFilter myInstance;
	
	Pattern filePattern;
	PatternMatcher matcher;
	
	public static MHMessageFileFilter getInstance() {
		if( myInstance == null)
			myInstance = new MHMessageFileFilter();
			
		return myInstance;
	}
	
	protected MHMessageFileFilter() {
		try {
			filePattern = new Perl5Compiler().compile(fileRegexp);
		} catch (MalformedPatternException e) {
			e.printStackTrace();
		}
		matcher = new Perl5Matcher();
	}
	
	/**
	 * @see java.io.FileFilter#accept(java.io.File)
	 */
	public boolean accept(File arg0) {
		return (arg0.isFile()) && matcher.matches(arg0.getName(), filePattern);
	}

}