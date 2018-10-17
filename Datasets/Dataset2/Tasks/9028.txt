public class GetHeaderFieldsTest extends AbstractFolderTst {

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

import org.columba.ristretto.message.Header;

/**
 * @author fdietz
 *  
 */
public class GetHeaderFieldsTest extends AbstractFolderTest {

    public GetHeaderFieldsTest(String arg0) {
        super(arg0);
    }
    
    /**
     * @param factory
     * @param test
     */
    public GetHeaderFieldsTest(MailboxTstFactory factory, String test) {
        super(factory, test);

    }

    /**
     * Compare Subject, From, To headers.
     * 
     * @throws Exception
     */
    public void test() throws Exception {
        // add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);

        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);

        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);
        Header header = getSourceFolder().getHeaderFields(uid,
                new String[] { "Subject", "From", "To"});
        
        assertEquals("Subject", "test", header.get("Subject"));
        assertEquals("From", "alice@mail.org", header.get("From"));
        assertEquals("To", "bob@mail.org", header.get("To"));
    }

}