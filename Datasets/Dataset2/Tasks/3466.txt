ColumbaLogger.log.info("reference=" +

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
package org.columba.mail.gui.tree.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.logging.ColumbaLogger;

import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.main.MailInterface;


/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class FetchSubFolderListCommand extends FolderCommand {
    FolderTreeNode treeNode;

    /**
     * Constructor for FetchSubFolderListCommand.
     * @param references
     */
    public FetchSubFolderListCommand(DefaultCommandReference[] references) {
        super(references);
    }

    /**
     * @see org.columba.core.command.Command#updateGUI()
     */
    public void updateGUI() throws Exception {
        MailInterface.treeModel.nodeStructureChanged(treeNode);
    }

    /**
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(Worker worker) throws Exception {
        ColumbaLogger.log.debug("reference=" +
            getReferences(Command.UNDOABLE_OPERATION));

        FolderCommandReference[] r = (FolderCommandReference[]) getReferences(Command.FIRST_EXECUTION);

        if (r == null) {
            return;
        }

        treeNode = (FolderTreeNode) r[0].getFolder();

        if (treeNode instanceof IMAPRootFolder) {
            ((IMAPRootFolder) treeNode).syncSubscribedFolders();
        }
    }

    /**
     * @see org.columba.core.command.Command#undo(Worker)
     */
    public void undo(Worker worker) throws Exception {
    }

    /**
     * @see org.columba.core.command.Command#redo(Worker)
     */
    public void redo(Worker worker) throws Exception {
    }
}