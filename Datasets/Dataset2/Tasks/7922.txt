public class CopyMessageFolderTest extends AbstractFolderTst {

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

import org.columba.ristretto.message.Attributes;
import org.columba.ristretto.message.Flags;

/**
 * @author fdietz
 */
public class CopyMessageFolderTest extends AbstractFolderTest {
    
    public CopyMessageFolderTest(String arg0) {
        super(arg0);
    }
    
    /**
     * @param arg0
     */
    public CopyMessageFolderTest(MailboxTstFactory factory, String arg0) {
        super(factory, arg0);
    }

   

    /**
     * Copy message and check if attributes are copied correctly.
     * <p>
     * Use Folder.addMessage(InputStream, Attributes), instead of
     * CopyMessageCommand.
     * 
     * @throws Exception
     */
    public void testCopyMessageAttribute2() throws Exception {
        //		 add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);
        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);

        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);
        // close streams
        inputStream.close();
        // get flags of message
        Flags oldFlags = getSourceFolder().getFlags(uid);
        // set flags
        oldFlags.setSeen(false);
        oldFlags.setRecent(false);
        oldFlags.setFlagged(true);        
        oldFlags.setDeleted(false);

        // get message source stream
        InputStream is = getSourceFolder().getMessageSourceStream(uid);
        // get message attributes
        Attributes attributes = getSourceFolder().getAttributes(uid);
        
        uid = getDestFolder().addMessage(is, attributes, oldFlags);

        // close inpustream
        is.close();

        Flags flags = getDestFolder().getFlags(uid);

        assertEquals("copied message should be marked as not seen", false,
                flags.getSeen());
        assertEquals("copied message should be marked as flagged", true, flags
                .getFlagged());
        assertEquals("copied message should be marked as not expunged", false,
                flags.getDeleted());
        // close streams
        inputStream.close();

    }
}