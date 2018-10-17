Object uid = inboxFolder.addMessage(messageStream, message.getHeader().getAttributes(),message.getHeader().getFlags());

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
package org.columba.mail.pop3.command;

import org.columba.core.command.CompoundCommand;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.AccountItem;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterList;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.folder.AbstractFolder;
import org.columba.mail.folder.RootFolder;
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.gui.frame.TableUpdater;
import org.columba.mail.gui.table.model.TableModelChangedEvent;
import org.columba.mail.main.MailInterface;
import org.columba.mail.message.ColumbaMessage;
import org.columba.mail.spam.command.CommandHelper;
import org.columba.mail.spam.command.ScoreMessageCommand;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.io.SourceInputStream;

/**
 * After downloading the message from the POP3 server, its added to the Inbox
 * folder.
 * <p>
 * The spam filter is executed on this message.
 * <p>
 * The Inbox filters are applied to the message.
 *
 * @author fdietz
 */
public class AddPOP3MessageCommand extends FolderCommand {

    private MessageFolder inboxFolder;

    /**
     * @param references command arguments
     */
    public AddPOP3MessageCommand(DefaultCommandReference[] references) {
        super(references);
    }

    /** {@inheritDoc} */
    public void execute(WorkerStatusController worker) throws Exception {
        FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

        inboxFolder = (MessageFolder) r[0].getFolder();

        ColumbaMessage message = (ColumbaMessage) r[0].getMessage();

        // add message to folder
        SourceInputStream messageStream = new SourceInputStream(message.getSource());
        Object uid = inboxFolder.addMessage(messageStream, message.getHeader().getAttributes(),message.getFlags());
        messageStream.close();
        inboxFolder.getFlags(uid).set(Flags.RECENT);

        inboxFolder.getMessageFolderInfo().incRecent();

        // apply spam filter
        applySpamFilter(uid, worker);

        // apply filter on message
        applyFilters(uid);
    }

    /**
     * Apply spam filter engine on message.
     * <p>
     * Message is marked as ham or spam.
     *
     * @param uid
     *            message uid.
     * @throws Exception
     */
    private void applySpamFilter(Object uid, WorkerStatusController worker)
            throws Exception {
        // message belongs to which account?
        AccountItem item = CommandHelper.retrieveAccountItem(inboxFolder, uid);

        // if spam filter is not enabled -> return
        if (!item.getSpamItem().isEnabled()) {
            return;
        }

        // create reference
        FolderCommandReference[] r = new FolderCommandReference[1];
        r[0] = new FolderCommandReference(inboxFolder, new Object[] {uid});

        // pass command to command scheduler
        new ScoreMessageCommand(r).execute(worker);

        if (item.getSpamItem().isMoveIncomingJunkMessagesEnabled()) {
            if (item.getSpamItem().isIncomingTrashSelected()) {
                // move message to trash
                MessageFolder trash = (MessageFolder) ((RootFolder) inboxFolder
                        .getRootFolder()).getTrashFolder();

                // create reference
                FolderCommandReference[] ref2 = new FolderCommandReference[2];
                ref2[0] = new FolderCommandReference(inboxFolder,
                        new Object[] {uid});
                ref2[1] = new FolderCommandReference(trash);

                MainInterface.processor.addOp(new MoveMessageCommand(ref2));
            } else {
                // move message to user-configured folder (generally "Junk"
                // folder)
                AbstractFolder destFolder = MailInterface.treeModel
                        .getFolder(item.getSpamItem().getMoveCustomFolder());

                // create reference
                FolderCommandReference[] ref2 = new FolderCommandReference[2];
                ref2[0] = new FolderCommandReference(inboxFolder,
                        new Object[] {uid});
                ref2[1] = new FolderCommandReference(destFolder);
                MainInterface.processor.addOp(new MoveMessageCommand(ref2));
            }
        }
    }

    /**
     * Apply filters on new message.
     *
     * @param uid
     *            message uid
     */
    private void applyFilters(Object uid) throws Exception {
        FilterList list = inboxFolder.getFilterList();

        for (int j = 0; j < list.count(); j++) {
            Filter filter = list.get(j);

            Object[] result = inboxFolder.searchMessages(filter,
                    new Object[] {uid});

            if (result.length != 0) {
                CompoundCommand command = filter
                        .getCommand(inboxFolder, result);

                MainInterface.processor.addOp(command);
            }
        }
    }

    /** {@inheritDoc} */
    public void updateGUI() throws Exception {
        // update table viewer
        TableModelChangedEvent ev = new TableModelChangedEvent(
                TableModelChangedEvent.UPDATE, inboxFolder);

        TableUpdater.tableChanged(ev);

        // update tree viewer
        MailInterface.treeModel.nodeChanged(inboxFolder);
    }
}