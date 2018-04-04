import org.columba.core.main.MainInterface;

package org.columba.mail.folder.command;

import org.columba.core.command.Command;
import org.columba.core.command.CompoundCommand;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.filter.Filter;
import org.columba.mail.filter.FilterList;
import org.columba.mail.folder.Folder;
import org.columba.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class ApplyFilterCommand extends Command{

	/**
	 * Constructor for ApplyFilterCommand.
	 * @param frameController
	 * @param references
	 */
	public ApplyFilterCommand(
		
		DefaultCommandReference[] references) {
		super( references);
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Folder srcFolder = (Folder) r[0].getFolder();
		Object[] uids = r[0].getUids();

		FilterList list = srcFolder.getFilterList();
		
		worker.setDisplayText("Applying filter to "+srcFolder.getName()+"...");
		worker.setProgressBarMaximum(list.count());
		
		for (int i = 0; i < list.count(); i++) {
			worker.setProgressBarValue(i);
			Filter filter = list.get(i);

			Object[] result = srcFolder.searchMessages(filter, worker);
			if (result.length != 0) {
				CompoundCommand command =
					filter.getCommand(srcFolder, result);

				MainInterface.processor.addOp(command);
			}
			//processAction( srcFolder, filter, result, worker );
		}
	}

}