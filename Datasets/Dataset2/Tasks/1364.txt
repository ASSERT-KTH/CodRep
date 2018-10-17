public class GetMimePartSourceStreamTest extends AbstractFolderTst {

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
import java.io.InputStream;

/**
 * @author fdietz
 *  
 */
public class GetMimePartSourceStreamTest extends AbstractFolderTest {

    public GetMimePartSourceStreamTest(String arg0) {
        super(arg0);
    }
    
    /**
     * @param factory
     * @param test
     */
    public GetMimePartSourceStreamTest(MailboxTstFactory factory, String test) {
        super(factory, test);

    }

   
    /**
     * Fetch source of mimepart 1.
     * 
     * @throws Exception
     */
    public void test() throws Exception {
        // add message "1.eml" as inputstream to folder
        String input = FolderTstHelper.getString(1);
        System.out.println("input=" + input);

        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);

        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);

        // get inputstream of mimepart 0 from folder
        InputStream outputStream = sourceFolder.getMimePartSourceStream(uid,
                new Integer[] { new Integer(1)});

        // create string from inputstream
        String output = FolderTstHelper.getStringFromInputStream(outputStream);
        System.out.println("output=" + output);

        input = FolderTstHelper.getString("1_1_mimepart.eml");
        
        // compare both messages
        assertEquals("message source should be equal", input, output);
    }
}