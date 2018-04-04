import org.columba.core.command.NullWorkerStatusController;

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
package org.columba.mail.folder.command;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import org.columba.core.util.NullWorkerStatusController;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.AbstractFolderTest;
import org.columba.mail.folder.FolderTstHelper;
import org.columba.mail.folder.MailboxTstFactory;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.MailboxInfo;


/**
 * @author fdietz
 *
 */
public class CopyMessageCommandTest extends AbstractFolderTest {

    public CopyMessageCommandTest(String arg0) {
        super(arg0);
    }
    
    /**
     * @param arg0
     */
    public CopyMessageCommandTest(MailboxTstFactory factory, String arg0) {
        super(factory, arg0);
    }

    /**
     * Copy message using a {@link CopyMessageCommand}.
     *
     * @throws Exception
     */
    public void testCopyMessage() throws Exception {
        // add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);
        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);
        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);

        // create Command reference
        FolderCommandReference[] ref = new FolderCommandReference[2];
        ref[0] = new FolderCommandReference(getSourceFolder(),
                new Object[] {uid});
        ref[1] = new FolderCommandReference(getDestFolder());

        // create copy command
        CopyMessageCommand command = new CopyMessageCommand(ref);

        // execute command -> use mock object class as worker which does
        // nothing
        command.execute(NullWorkerStatusController.getInstance());

        // get inputstream of this message from folder
        InputStream outputStream = destFolder.getMessageSourceStream(uid);
        // create string from inputstream
        String output = FolderTstHelper.getStringFromInputStream(outputStream);
        // compare both messages
        assertEquals(input, output);
        Object[] uids = getDestFolder().getUids();
        assertEquals("one message should be in destination folder", 1, uids.length);
        MailboxInfo info = getDestFolder().getMessageFolderInfo();
        assertEquals("one message should be in destination folder", 1, info
                .getExists());
        // close streams
        inputStream.close();
        outputStream.close();
    }

    /**
     * Copy message using a {@link CopyMessageCommand}and check if attributes
     * are copied correctly.
     *
     * @throws Exception
     */
    public void testCopyMessageAttribute() throws Exception {
        //  add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);
        // create stream from string
        ByteArrayInputStream inputStream = FolderTstHelper
                .getByteArrayInputStream(input);
        // add stream to folder
        Object uid = getSourceFolder().addMessage(inputStream);
        // get flags of message
        Flags oldFlags = getSourceFolder().getFlags(uid);
        // set flags
        oldFlags.setSeen(false);
        /*
        oldFlags.setRecent(true);
        oldFlags.setFlagged(true);
        oldFlags.setExpunged(false);
		*/
		
        // create Command reference
        FolderCommandReference[] ref = new FolderCommandReference[2];
        ref[0] = new FolderCommandReference(getSourceFolder(),
                new Object[] {uid});
        ref[1] = new FolderCommandReference(getDestFolder());

        // create copy command
        CopyMessageCommand command = new CopyMessageCommand(ref);

        // execute command -> use mock object class as worker which does
        // nothing
        command.execute(NullWorkerStatusController.getInstance());

        Flags flags = getDestFolder().getFlags(uid);

        assertEquals("copied message should be marked as not seen", false,
                flags.getSeen());
        /*
        assertEquals("copied message should be marked as recent", true, flags
                .getRecent());
        assertEquals("copied message should be marked as flagged", true, flags
                .getFlagged());
        assertEquals("copied message should be marked as not expunged", false,
                flags.getExpunged());
        */
        // close streams
        inputStream.close();

    }

}