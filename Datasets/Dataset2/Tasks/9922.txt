public class AttributeTest extends AbstractFolderTst {

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
package org.columba.mail.folder;

import java.io.ByteArrayInputStream;


/**
 * Tests for {@link Attribute} methods.
 * 
 * @author fdietz
 *
 */
public class AttributeTest extends AbstractFolderTest {

    public AttributeTest(String arg0) {
        super(arg0);
    }
    /**
     * @param factory
     * @param test
     */
    public AttributeTest(MailboxTstFactory factory, String test) {
        super(factory, test);
        
    }

    /**
     * Check set/get attributes
     * @throws Exception
     */
    public void test() throws Exception {
//      add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);

        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);

        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);
        
        getSourceFolder().setAttribute(uid, "columba.spam", Boolean.TRUE);
        
        Boolean result = (Boolean) getSourceFolder().getAttribute(uid, "columba.spam");
        
        assertEquals("attribute columba.spam", Boolean.TRUE, result);
    }
}