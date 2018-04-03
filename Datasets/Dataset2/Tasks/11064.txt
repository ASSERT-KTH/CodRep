message.getHeader().getAttributes(), message.getFlags());

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
package org.columba.mail.gui.composer.command;

import java.io.InputStream;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.WorkerStatusController;

import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.composer.MessageComposer;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.MessageFolder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.gui.frame.TableUpdater;
import org.columba.mail.gui.table.model.TableModelChangedEvent;
import org.columba.mail.main.MailInterface;


/**
 * @author freddy
 */
public class SaveMessageCommand extends FolderCommand {
    private MessageFolder folder;

    /**
     * Constructor for SaveMessageCommand.
     *
     * @param frameMediator
     * @param references
     */
    public SaveMessageCommand(DefaultCommandReference[] references) {
        super(references);
    }

    public void updateGUI() throws Exception {
        // update the table
        TableModelChangedEvent ev = new TableModelChangedEvent(TableModelChangedEvent.UPDATE,
                folder);

        TableUpdater.tableChanged(ev);

        MailInterface.treeModel.nodeChanged(folder);
    }

    /**
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(WorkerStatusController worker)
        throws Exception {
        ComposerCommandReference[] r = (ComposerCommandReference[]) getReferences();

        ComposerController composerController = r[0].getComposerController();

        AccountItem item = ((ComposerModel) composerController.getModel()).getAccountItem();

        SendableMessage message = (SendableMessage) r[0].getMessage();

        if (message == null) {
            message = new MessageComposer(((ComposerModel) composerController.getModel())).compose(worker);
        }

        folder = (MessageFolder) r[0].getFolder();

        InputStream sourceStream = message.getSourceStream();
        folder.addMessage(sourceStream,
            message.getHeader().getAttributes());
        sourceStream.close();
    }
}