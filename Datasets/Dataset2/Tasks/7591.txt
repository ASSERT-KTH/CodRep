import org.columba.core.main.MainInterface;

package org.columba.mail.folder.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class CopyMessageCommand extends FolderCommand {

	protected Folder destFolder;
	protected Object[] destUids;

	/**
	 * Constructor for CopyMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public CopyMessageCommand(
		
		DefaultCommandReference[] references) {
		super( references);

		commandType = Command.UNDOABLE_OPERATION;
	}

	public void updateGUI() throws Exception {
		

		TableChangedEvent ev =
			new TableChangedEvent(TableChangedEvent.UPDATE, destFolder);

		MainInterface.frameModel.tableChanged(ev);

		MainInterface.treeModel.nodeChanged(destFolder);
	}

	protected void innerCopy(
		Folder srcFolder,
		Folder destFolder,
		Object[] uids,
		Worker worker)
		throws Exception {
		
		srcFolder.innerCopy( destFolder, uids, worker );

	}

	protected void defaultCopy(
		Folder srcFolder,
		Folder destFolder,
		Object[] uids,
		Worker worker)
		throws Exception {
		for (int i = 0; i < uids.length; i++) {

			Object uid = uids[i];
			//ColumbaLogger.log.debug("copying UID=" + uid);

			if (srcFolder.exists(uid, worker)) {
				String source = srcFolder.getMessageSource(uid, worker);

				destUids[i] = destFolder.addMessage(source, worker);
			}

			worker.setProgressBarValue(i);
		}

	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		

		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Object[] uids = r[0].getUids();

		Folder srcFolder = (Folder) r[0].getFolder();
		destFolder = (Folder) r[1].getFolder();
		destUids = new Object[uids.length];

		ColumbaLogger.log.debug("src=" + srcFolder + " dest=" + destFolder);

		worker.setDisplayText(
			"Copying messages to " + destFolder.getName() + "...");
		worker.setProgressBarMaximum(uids.length);

		// compare source- and dest-folder		
		if (srcFolder.getRootFolder().equals(destFolder.getRootFolder())) {
			// source- and dest-folder match
			//  -> user optimized copy operation

			innerCopy(srcFolder, destFolder, uids, worker);
		} else {
			// no match
			//  -> for example: copying from imap-server to local-folder
			defaultCopy(srcFolder, destFolder, uids, worker);
		}

	}

	/**
	 * @see org.columba.core.command.Command#undo(Worker)
	 */
	public void undo(Worker worker) throws Exception {
		/*
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		
		Object[] uids = r[1].getUids();
		
		Folder srcFolder = (Folder) r[1].getFolder();
		
		for (int i = 0; i < uids.length; i++) {
			Object uid = uids[i];
			ColumbaLogger.log.debug("undo_copying UID=" + uid);
		
			srcFolder.removeMessage(uid, worker);
		}
		*/
	}

	/**
	 * @see org.columba.core.command.Command#redo(Worker)
	 */
	public void redo(Worker worker) throws Exception {
		execute(worker);
	}

}