Object uid = folder.addMessage(message.getSource());

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

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.composer.MessageComposer;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.gui.frame.TableUpdater;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.message.HeaderInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SaveMessageCommand extends FolderCommand {

	protected Folder folder;
	protected HeaderInterface[] headerList = new HeaderInterface[1];

	/**
	 * Constructor for SaveMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public SaveMessageCommand(DefaultCommandReference[] references) {
		super(references);
	}

	public void updateGUI() throws Exception {

		// update the table
		TableChangedEvent ev =
			new TableChangedEvent(TableChangedEvent.UPDATE, folder);

		TableUpdater.tableChanged(ev);

		MainInterface.treeModel.nodeChanged(folder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {

		ComposerCommandReference[] r =
			(ComposerCommandReference[]) getReferences();

		ComposerController composerController = r[0].getComposerController();

		AccountItem item = ((ComposerModel)composerController.getModel()).getAccountItem();

		SendableMessage message =
			new MessageComposer(((ComposerModel)composerController.getModel())).compose(worker);

		folder = (Folder) r[0].getFolder();

		// we can't use this addMessage-method here
		// -> IMAP only supports sending sources
		//Object uid = folder.addMessage(message, worker);
		
		Object uid = folder.addMessage(message.getSource(), worker);
		

		// IMAP can't give you this information
		/*
		// we need this to reflect changes in table-widget
		// -> this is cached in folder anyway, so actually
		// -> we just get the HeaderInterface from a Hashtable
		headerList[0] = folder.getMessageHeader(uid, worker);
		*/
	}

}