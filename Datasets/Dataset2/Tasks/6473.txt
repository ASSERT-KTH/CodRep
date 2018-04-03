//listInfo.parse(r);

/*
 * Created on Jul 3, 2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.imap.parser;

import junit.framework.TestCase;

import org.columba.mail.imap.IMAPResponse;

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ListInfoTest extends TestCase {

	/**
	 * Constructor for ListInfoTest.
	 * @param arg0
	 */
	public ListInfoTest(String arg0) {
		super(arg0);
	}

	public void testParse() {

		IMAPResponse r = new IMAPResponse("testdata");

		ListInfo listInfo = new ListInfo();
		listInfo.parse(r);
	}

}