srcFolder.expungeFolder(worker);

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

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandAdapter;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.TableChangedEvent;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class MoveMessageCommand extends CopyMessageCommand {

	protected Folder destFolder;
	

	protected FolderCommandAdapter adapter;

	/**
	 * Constructor for MoveMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public MoveMessageCommand(DefaultCommandReference[] references) {
		super(references);
	}

	public void updateGUI() throws Exception {
		super.updateGUI();
		

		FolderCommandReference[] r = adapter.getSourceFolderReferences();

		TableChangedEvent ev;
		for (int i = 0; i < r.length; i++) {

			ev =
				new TableChangedEvent(
					TableChangedEvent.REMOVE,
					r[i].getFolder(),
					r[i].getUids());

			MailFrameController.tableChanged(ev);

			MainInterface.treeModel.nodeChanged(r[i].getFolder());
		}

		FolderCommandReference u = adapter.getUpdateReferences();
		if (u != null) {

			ev = new TableChangedEvent(TableChangedEvent.REMOVE, u.getFolder(), u.getUids());

			MailFrameController.tableChanged(ev);

			MainInterface.treeModel.nodeChanged(u.getFolder());
		}

	
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		super.execute(worker);

		adapter =
			new FolderCommandAdapter(
				(FolderCommandReference[]) getReferences());

		FolderCommandReference[] r = adapter.getSourceFolderReferences();
		destFolder = (Folder) adapter.getDestinationFolder();

		for (int i = 0; i < r.length; i++) {

			Object[] uids = r[i].getUids();

			Folder srcFolder = (Folder) r[i].getFolder();
			uids = r[i].getUids();

			ColumbaLogger.log.debug("src=" + srcFolder + " dest=" + destFolder);

			worker.setDisplayText(
				"Moving messages to " + destFolder.getName() + "...");
			worker.setProgressBarMaximum(uids.length);

			srcFolder.markMessage(
				uids,
				MarkMessageCommand.MARK_AS_EXPUNGED,
				worker);

			srcFolder.expungeFolder(uids, worker);

		}

	}
}