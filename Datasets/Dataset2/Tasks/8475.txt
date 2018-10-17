import org.columba.core.main.MainInterface;

package org.columba.mail.gui.tree.command;

import java.util.Hashtable;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.main.MainInterface;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class CreateSubFolderCommand extends Command {

	private FolderTreeNode parentFolder;
	private boolean success;
	private Hashtable attributes;

	/**
	 * Constructor for CreateSubFolderCommand.
	 * @param references
	 */
	public CreateSubFolderCommand(DefaultCommandReference[] references) {
		super(references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.UNDOABLE_OPERATION;

		success = true;
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		// if creating of folder failed -> exit
		if (success == false)
			return;

		// else update TreeModel
		MainInterface.treeModel.nodeStructureChanged(parentFolder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {

		parentFolder =
			((FolderCommandReference) getReferences()[0]).getFolder();
		String name =
			((FolderCommandReference) getReferences()[0]).getFolderName();

		/*
		attributes = parentFolder.getAttributes();
		attributes.put("name", name);
		*/
		try {
			parentFolder.addFolder(name);
		} catch (Exception ex) {
			success = false;
			throw ex;
		}
	}

	/**
	 * @see org.columba.core.command.Command#undo(Worker)
	 */
	public void undo(Worker worker) throws Exception {
	}

	/**
	 * @see org.columba.core.command.Command#undo(Worker)
	 */
	public void redo(Worker worker) throws Exception {
	}

}