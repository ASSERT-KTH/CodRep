public void updateSelectedGUI() throws Exception {

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.table.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.message.HeaderList;
import org.columba.main.MainInterface;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class ViewHeaderListCommand extends Command {

	private HeaderList headerList;
	private Folder folder;

	public ViewHeaderListCommand( FrameController frame, DefaultCommandReference[] references ) {
		super( frame, references );
		
		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NO_UNDO_OPERATION;				
	}
		
	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		((MailFrameController)frameController).tableController.getHeaderTableModel().setHeaderList(headerList);
		
		((MailFrameController)frameController).tableController.getView().clearSelection();
		((MailFrameController)frameController).tableController.getActionListener().changeMessageActions();
		
		MainInterface.treeModel.nodeChanged(folder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		
		folder = (Folder)r[0].getFolder();
		headerList = (folder).getHeaderList(worker);
	}
}