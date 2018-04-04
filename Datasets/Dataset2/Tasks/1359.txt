((TableOwnerInterface) frameController).getTableController().showHeaderList(folder, headerList);

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
import org.columba.core.command.CompoundCommand;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.SelectiveGuiUpdateCommand;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.FolderItem;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterList;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.TableOwnerInterface;
import org.columba.mail.gui.table.selection.TableSelectionHandler;
import org.columba.mail.message.HeaderList;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class ViewHeaderListCommand extends SelectiveGuiUpdateCommand {

	private HeaderList headerList;
	private Folder folder;

	public ViewHeaderListCommand(
		AbstractFrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NO_UNDO_OPERATION;
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {

		(
			(TableSelectionHandler) frameController
				.getSelectionManager()
				.getHandler(
				"mail.table")).setFolder(
			folder);

		((TableOwnerInterface) frameController).showHeaderList(folder, headerList);

		MainInterface.treeModel.nodeChanged(folder);

	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		folder = (Folder) r[0].getFolder();

		FolderItem item = folder.getFolderItem();
		if (item.get("type").equals("IMAPFolder")) {
			boolean applyFilter =
				item.getBoolean(
					"property",
					"automatically_apply_filter",
					false);
			if (applyFilter == true) {
				FilterList list = folder.getFilterList();

				worker.setDisplayText(
					"Applying filter to " + folder.getName() + "...");
				worker.setProgressBarMaximum(list.count());

				for (int i = 0; i < list.count(); i++) {
					worker.setProgressBarValue(i);
					Filter filter = list.get(i);

					Object[] result = folder.searchMessages(filter, worker);
					if (result.length != 0) {
						CompoundCommand command =
							filter.getCommand(folder, result);

						MainInterface.processor.addOp(command);
					}
					//processAction( srcFolder, filter, result, worker );
				}
			}
		}

		headerList = (folder).getHeaderList(worker);
	}
}