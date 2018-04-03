assertEquals("Number of unseen messages in folder", 0, info.getUnseen());

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
package org.columba.mail.folder;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.MailboxInfo;

/**
 * Add message to folder testcase.
 *
 * @author fdietz
 */
public class AddMessageFolderTest extends AbstractFolderTst {

  
    public AddMessageFolderTest(String arg0) {
        super(arg0);
    }
    /**
     * Constructor for CachedMHFolderTest.
     *
     * @param arg0
     */
    public AddMessageFolderTest(MailboxTstFactory factory, String arg0) {
        super(factory, arg0);
    }

    /**
     * Add a message as InputStream to MHCachedFolder.
     * <p>
     * Check if message in folder is identical.
     * <p>
     * Check if total message count of folder was incremented correctly.
     *
     * @throws Exception
     */
    public void testAddMessage() throws Exception {

        Object[] uids1 = getSourceFolder().getUids();
        assertEquals("starting with empty folder", 0, uids1.length);

        MailboxInfo info1 = getSourceFolder().getMessageFolderInfo();
        assertEquals("starting with empty folder", 0, info1.getExists());

        // add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);

        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);

        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);

        // get inputstream of this message from folder
        InputStream outputStream = sourceFolder.getMessageSourceStream(uid);

        // create string from inputstream
        String output = FolderTstHelper.getStringFromInputStream(outputStream);

        // compare both messages
        assertEquals("message source should be equal", input, output);

        Object[] uids = getSourceFolder().getUids();
        assertEquals("one message should be in this folder", 1, uids.length);

        MailboxInfo info = getSourceFolder().getMessageFolderInfo();
        assertEquals("message-folderinfo exists", 1, info.getExists());

        // close streams
        inputStream.close();
        outputStream.close();
    }

    /**
     * Check if MailFolderInfo is properly set based on message attributes.
     * <p>
     */
    public void testAddAttributesTest() throws Exception {

        Object[] uids1 = getSourceFolder().getUids();
        assertEquals("starting with empty folder", 0, uids1.length);

        MailboxInfo info1 = getSourceFolder().getMessageFolderInfo();
        assertEquals("starting with empty folder", 0, info1.getExists());

        //		 add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);

        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);

        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);
        Flags flags = getSourceFolder().getFlags(uid);
        flags.setSeen(true);

        MailboxInfo info = getSourceFolder().getMessageFolderInfo();

        assertEquals("message-folderinfo exists", 1, info.getExists());
        assertEquals("Number of unseen messages in folder", 1, info.getUnseen());
        assertEquals("Number of seen messages in folder", 0, info.getExists()
                - info.getUnseen());

        // close streams
        inputStream.close();
    }
}