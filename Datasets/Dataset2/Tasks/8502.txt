ColumbaLogger.log.info("src=" + srcFolder + " dest=" + destFolder);

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
package org.columba.mail.folder.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;
import org.columba.core.logging.ColumbaLogger;

import org.columba.mail.command.FolderCommandAdapter;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.TableUpdater;
import org.columba.mail.gui.table.model.TableModelChangedEvent;
import org.columba.mail.main.MailInterface;


/**
 * Move selected messages from source to destination folder.
 * <p>
 * A dialog asks the user the destination folder to use.
 *
 * @author fdietz
 */
public class MoveMessageCommand extends CopyMessageCommand {
    /**
     * Constructor for MoveMessageCommand.
     *
     * @param frameMediator
     * @param references
     */
    public MoveMessageCommand(DefaultCommandReference[] references) {
        super(references);
    }

    public void updateGUI() throws Exception {
        // calling CopyMessageCommand.updateGUI() here!
        super.updateGUI();

        // get source references
        FolderCommandReference[] r = adapter.getSourceFolderReferences();

        // for each source reference
        TableModelChangedEvent ev;

        for (int i = 0; i < r.length; i++) {
            // update message list
            ev = new TableModelChangedEvent(TableModelChangedEvent.REMOVE,
                    r[i].getFolder(), r[i].getUids());

            TableUpdater.tableChanged(ev);

            // update treemodel
            MailInterface.treeModel.nodeChanged(r[i].getFolder());
        }

        // get update reference
        // -> only available if virtual folder is involved in operation
        FolderCommandReference u = adapter.getUpdateReferences();

        if (u != null) {
            ev = new TableModelChangedEvent(TableModelChangedEvent.REMOVE,
                    u.getFolder(), u.getUids());

            TableUpdater.tableChanged(ev);

            MailInterface.treeModel.nodeChanged(u.getFolder());
        }
    }

    /**
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(Worker worker) throws Exception {
        // calling CopyMessageCommand.execute() here!
        super.execute(worker);

        // get source reference array
        FolderCommandReference[] r = adapter.getSourceFolderReferences();

        // for every source reference
        for (int i = 0; i < r.length; i++) {
            // get messgae UIDs
            Object[] uids = r[i].getUids();

            // get source folder
            Folder srcFolder = (Folder) r[i].getFolder();

            // register for status events
            ((StatusObservableImpl) srcFolder.getObservable()).setWorker(worker);

            // setting lastSelection to null
            srcFolder.setLastSelection(null);

            uids = r[i].getUids();

            ColumbaLogger.log.debug("src=" + srcFolder + " dest=" + destFolder);

            // update status message
            worker.setDisplayText("Moving messages to " + destFolder.getName() +
                "...");
            worker.setProgressBarMaximum(uids.length);

            // mark all messages as expunged
            srcFolder.markMessage(uids, MarkMessageCommand.MARK_AS_EXPUNGED);

            // expunge folder
            srcFolder.expungeFolder();

            // We are done - clear the status message after a delay
            worker.clearDisplayTextWithDelay();
        }
    }
}