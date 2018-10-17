import org.columba.core.command.NullWorkerStatusController;

//The contents of this file are subject to the Mozilla Public License Version
//1.1
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
//Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.mail.folder.command;

import java.io.ByteArrayInputStream;

import org.columba.core.util.NullWorkerStatusController;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.AbstractFolderTest;
import org.columba.mail.folder.FolderTstHelper;
import org.columba.mail.folder.MailboxTstFactory;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.MailboxInfo;

/**
 * @author fdietz
 */
public class MarkMessageTest extends AbstractFolderTest {

    private Object uid;

    private ByteArrayInputStream inputStream;

    
    public MarkMessageTest(String arg0) {
        super(arg0);
    }
    
    /**
     * @param arg0
     */
    public MarkMessageTest(MailboxTstFactory factory, String arg0) {
        super(factory, arg0);
    }

    public void testMarkAsReadMessage() throws Exception {

        // create Command reference
        FolderCommandReference[] ref = new FolderCommandReference[1];
        ref[0] = new FolderCommandReference(getSourceFolder(),
                new Object[] {uid});
        ref[0].setMarkVariant(MarkMessageCommand.MARK_AS_READ);

        // create copy command
        MarkMessageCommand command = new MarkMessageCommand(ref);

        // execute command -> use mock object class as worker which does
        // nothing
        command.execute(NullWorkerStatusController.getInstance());

        Flags flags = getSourceFolder().getFlags(uid);

        assertEquals("message should be marked as read", true, flags.getSeen());

        MailboxInfo info = getSourceFolder().getMessageFolderInfo();
        assertEquals("one mark as read message should be in folder", 1, info
                .getExists()
                - info.getUnseen());

    }

    public void testMarkAsFlaggedMessage() throws Exception {

        // create Command reference
        FolderCommandReference[] ref = new FolderCommandReference[2];
        ref[0] = new FolderCommandReference(getSourceFolder(),
                new Object[] { uid});
        ref[0].setMarkVariant(MarkMessageCommand.MARK_AS_FLAGGED);

        // create copy command
        MarkMessageCommand command = new MarkMessageCommand(ref);

        // execute command -> use mock object class as worker which does
        // nothing
        command.execute(NullWorkerStatusController.getInstance());

        Flags flags = getSourceFolder().getFlags(uid);

        assertEquals("message should be marked as flagged", true, flags
                .getFlagged());

    }

    public void testMarkAsExpungedMessage() throws Exception {

        // create Command reference
        FolderCommandReference[] ref = new FolderCommandReference[2];
        ref[0] = new FolderCommandReference(getSourceFolder(),
                new Object[] { uid});
        ref[0].setMarkVariant(MarkMessageCommand.MARK_AS_EXPUNGED);

        // create copy command
        MarkMessageCommand command = new MarkMessageCommand(ref);

        // execute command -> use mock object class as worker which does
        // nothing
        command.execute(NullWorkerStatusController.getInstance());

        Flags flags = getSourceFolder().getFlags(uid);

        assertEquals("message should be marked as expunged", true, flags
                .getExpunged());

    }

    /**
     * @see junit.framework.TestCase#setUp()
     */
    protected void setUp() throws Exception {
        // create folders, etc.
        super.setUp();

        // add message "0.eml" as inputstream to folder
        String input = FolderTstHelper.getString(0);
        System.out.println("input=" + input);
        // create stream from string
        inputStream = FolderTstHelper.getByteArrayInputStream(input);
        // add stream to folder
        uid = getSourceFolder().addMessage(inputStream);

    }

    /**
     * @see junit.framework.TestCase#tearDown()
     */
    protected void tearDown() throws Exception {
        // close streams
        inputStream.close();

        // delete folders
        super.tearDown();

    }
}