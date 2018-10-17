import org.columba.core.main.MainInterface;

package org.columba.mail.folder.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.logging.ColumbaLogger;
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
public class MoveMessageCommand extends CopyMessageCommand {

	protected Folder destFolder;
	protected Folder srcFolder;
	protected Object[] uids;

	/**
	 * Constructor for MoveMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public MoveMessageCommand(
		DefaultCommandReference[] references) {
		super(references);
	}

	public void updateGUI() throws Exception {

		TableChangedEvent ev =
			new TableChangedEvent(TableChangedEvent.UPDATE, destFolder);

		MainInterface.frameModel.tableChanged(ev);

		TableChangedEvent ev2 =
			new TableChangedEvent(TableChangedEvent.UPDATE, srcFolder);

		MainInterface.frameModel.tableChanged(ev2);

		MainInterface.treeModel.nodeChanged(destFolder);
		MainInterface.treeModel.nodeChanged(srcFolder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		super.execute(worker);
		
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Object[] uids = r[0].getUids();

		srcFolder = (Folder) r[0].getFolder();
		destFolder = (Folder) r[1].getFolder();

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