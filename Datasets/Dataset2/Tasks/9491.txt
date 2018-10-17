new TableChangedEvent(TableChangedEvent.UPDATE, folder);

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

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.TableUpdater;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.HeaderInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AddMessageCommand extends Command {

	protected HeaderInterface[] headerList = new HeaderInterface[1];
	protected Folder folder;

	/**
	 * Constructor for AddMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public AddMessageCommand(DefaultCommandReference[] references) {
		super(references);
	}

	public void updateGUI() throws Exception {
		//MailFrameController frame = (MailFrameController) frameController;

		TableChangedEvent ev =
			new TableChangedEvent(TableChangedEvent.ADD, folder, headerList);

		//frame.tableController.tableChanged(ev);
		
		MainInterface.treeModel.nodeChanged(folder);
		
		TableUpdater.tableChanged(ev);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		folder = (Folder) r[0].getFolder();
		AbstractMessage message = (AbstractMessage) r[0].getMessage();

		Object uid = folder.addMessage(message, worker);

		// we need this to reflect changes in table-widget
		// -> this is cached in folder anyway, so actually
		// -> we just get the HeaderInterface from a Hashtable
		headerList[0] = folder.getMessageHeader(uid, worker);
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