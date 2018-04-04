public class ModifyContactTest extends AbstractFolderTstCase {

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.addressbook.folder;

import org.columba.addressbook.model.Contact;
import org.columba.addressbook.model.VCARD;

/**
 * @author fdietz
 *
 */
public class ModifyContactTest extends AbstractFolderTestCase {

	/**
	 * @param arg0
	 */
	public ModifyContactTest(String arg0) {
		super(arg0);
		
	}
	

	public void testModify() throws Exception{
		Contact c = new Contact();

		c.set(VCARD.NICKNAME, "old");

		Object uid = getSourceFolder().add(c);

		c.set(VCARD.NICKNAME, "new");
		getSourceFolder().modify(uid, c);
		
		Contact c2 = getSourceFolder().get(uid);

		assertEquals("nichname", "new", c2.get(VCARD.NICKNAME));
	}

}