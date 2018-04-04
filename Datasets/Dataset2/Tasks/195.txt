import org.columba.core.gui.frame.FrameController;

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

import java.awt.Rectangle;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.SelectiveGuiUpdateCommand;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.HeaderTableSelectionHandler;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.message.HeaderList;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class ViewHeaderListCommand extends SelectiveGuiUpdateCommand {

	private HeaderList headerList;
	private Folder folder;

	public ViewHeaderListCommand(
		FrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NO_UNDO_OPERATION;
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {

		
		((HeaderTableSelectionHandler)frameController.getSelectionManager().getHandler("mail.table")).setFolder(folder);
		((MailFrameController) frameController)
			.tableController
			.getHeaderTableModel()
			.setHeaderList(headerList);
		
		TableChangedEvent ev =
			new TableChangedEvent(TableChangedEvent.UPDATE, folder);		
		
		MainInterface.frameModel.tableChanged(ev);
		
		((MailFrameController) frameController)
					.tableController.getView().scrollRectToVisible(new Rectangle(0,0,0,0));
					
		
		boolean enableThreadedView =
			folder.getFolderItem().getBoolean(
				"property",
				"enable_threaded_view",
				false);

		/*
		((MailFrameController) frameController)
			.tableController.getHeaderTableModel().getTableModelThreadedView().toggleView( enableThreadedView );
			
			
		((MailFrameController) frameController)
			.tableController
			.getView()
			.enableThreadedView(enableThreadedView);
		*/

		((MailFrameController) frameController)
			.tableController
			.getView()
			.clearSelection();
		
		/*
		((MailFrameController) frameController)
			.tableController
			.getActionListener()
			.changeMessageActions();
*/

		MainInterface.treeModel.nodeChanged(folder);

		//((MailFrameController)frameController).treeController.getView().makeVisible(folder.getSelectionTreePath());

	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		folder = (Folder) r[0].getFolder();
		headerList = (folder).getHeaderList(worker);
	}
}