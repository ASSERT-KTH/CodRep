import org.columba.core.main.MainInterface;

package org.columba.mail.folder.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class RemoveFolderCommand extends Command {

	private FolderTreeNode parentFolder;
	private boolean success;

	/**
	 * Constructor for RemoveFolder.
	 * @param frameController
	 * @param references
	 */
	public RemoveFolderCommand(DefaultCommandReference[] references) {
		super(references);

		success = false;
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		MainInterface.treeModel.nodeStructureChanged(parentFolder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		Folder childFolder =
			(Folder) ((FolderCommandReference) getReferences()[0]).getFolder();

		parentFolder = (FolderTreeNode) childFolder.getParent();

		childFolder.removeFolder();

	}

}