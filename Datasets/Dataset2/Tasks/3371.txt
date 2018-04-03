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

import org.columba.core.util.NullWorkerStatusController;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.AbstractFolderTest;
import org.columba.mail.folder.MailboxTstFactory;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.imap.IMAPFolder;
import org.columba.mail.folder.temp.TempFolder;

/**
 * Test cases for the MoveFolder command.
 *
 * @author redsolo
 */
public class MoveFolderCommandTest extends AbstractFolderTest {

    public MoveFolderCommandTest(String arg0) {
        super(arg0);
    }
    
    public MoveFolderCommandTest(MailboxTstFactory factory, String arg0) {
        super(factory, arg0);
    }
    /**
     * Tests the execute() method.
     * @throws Exception thrown for any bad reason if the command goes wrong.
     */
    public void testMoveFolder() throws Exception {
        MessageFolder rootFolder = createFolder();
        
        // Is not supported by IMAP and TempFolder
        if( rootFolder instanceof IMAPFolder || rootFolder instanceof TempFolder ) {
        	return;
        }

        MessageFolder folderToBeMoved = createFolder();
        rootFolder.append(folderToBeMoved);

        MessageFolder destinationFolder = createFolder();
        rootFolder.append(destinationFolder);

        FolderCommandReference[] references = new FolderCommandReference[2];
        references[0] = new FolderCommandReference(folderToBeMoved);
        references[1] = new FolderCommandReference(destinationFolder);
        MoveFolderCommand command = new MoveFolderCommand(references);
        command.execute(NullWorkerStatusController.getInstance());

        assertEquals("The destination folders child size is incorrect.", 1, destinationFolder.getChildCount());
        assertEquals("The root folder has more than one child", 1, destinationFolder.getChildCount());
        assertEquals("The moved folders parent is not the destination folder", destinationFolder, folderToBeMoved.getParent());
    }
}