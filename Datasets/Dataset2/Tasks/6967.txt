FolderItem folderItem = folder.getConfiguration();

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
package org.columba.mail.gui.table.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.main.MainInterface;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.FolderItem;
import org.columba.mail.config.ImapItem;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.command.ApplyFilterCommand;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.gui.frame.TableViewOwner;
import org.columba.mail.gui.table.selection.TableSelectionHandler;
import org.columba.mail.main.MailInterface;
import org.columba.mail.message.HeaderList;


/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 *
 */
public class ViewHeaderListCommand extends Command {
    private HeaderList headerList;
    private MessageFolder folder;

    public ViewHeaderListCommand(FrameMediator frame,
        DefaultCommandReference[] references) {
        super(frame, references);

        priority = Command.REALTIME_PRIORITY;
        commandType = Command.NO_UNDO_OPERATION;
    }

    /**
 * @see org.columba.core.command.Command#updateGUI()
 */
    public void updateGUI() throws Exception {
        // notify table selection handler 
        ((TableSelectionHandler) frameMediator.getSelectionManager().getHandler("mail.table")).setFolder(folder);

        // this should be called from TableController instead
        ((TableViewOwner) frameMediator).getTableController().showHeaderList(folder,
            headerList);

        // update tree model
        MailInterface.treeModel.nodeChanged(folder);
    }

    /**
 * @see org.columba.core.command.Command#execute(Worker)
 */
    public void execute(WorkerStatusController worker)
        throws Exception {
        FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

        folder = (MessageFolder) r[0].getFolder();

        //		register for status events
        ((StatusObservableImpl) folder.getObservable()).setWorker(worker);

        // fetch the headerlist
        headerList = (folder).getHeaderList();

        // this is a little hack !!
        // check if this is an imap folder
        FolderItem folderItem = folder.getFolderItem();

        if (folderItem.get("type").equals("IMAPFolder")) {
            IMAPRootFolder rootFolder = (IMAPRootFolder) folder.getRootFolder();
            AccountItem accountItem = rootFolder.getAccountItem();
            ImapItem item = accountItem.getImapItem();

            boolean applyFilter = item.getBoolean("automatically_apply_filter",
                    false);

            // if "automatically apply filter" is selected 
            if (applyFilter == true) {
                MainInterface.processor.addOp(new ApplyFilterCommand(r));
            }
        }
    }
}