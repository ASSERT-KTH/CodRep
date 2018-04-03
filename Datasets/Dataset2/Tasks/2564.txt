suite.addTest(new TestSuite(UIDParserTest.class));

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

import junit.framework.Test;
import junit.framework.TestSuite;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AllTests {

	public static Test suite() {
		TestSuite suite =
			new TestSuite("Test for org.columba.modules.mail.parser");
		//$JUnit-BEGIN$
		suite.addTest(new TestSuite(Imap4ParserTest.class));
		//$JUnit-END$
		return suite;
	}
}