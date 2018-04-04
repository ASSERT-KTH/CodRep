import org.columba.core.main.MainInterface;

package org.columba.mail.folder.command;

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
public class MarkMessageCommand extends FolderCommand {

	public final static int MARK_AS_READ = 0;
	public final static int MARK_AS_FLAGGED = 1;
	public final static int MARK_AS_EXPUNGED = 2;
	public final static int MARK_AS_ANSWERED = 3;
	
	protected Object[] uids;
	protected Folder folder;
	protected int markVariant;

	/**
	 * Constructor for MarkMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public MarkMessageCommand(
		DefaultCommandReference[] references) {
		super( references);
	}

	public void updateGUI() throws Exception {
		
		TableChangedEvent ev = new TableChangedEvent( TableChangedEvent.MARK, folder, uids, markVariant );
		 
		MainInterface.frameModel.tableChanged(ev);
		
		MainInterface.treeModel.nodeChanged(folder);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		uids = r[0].getUids();
		folder = (Folder) r[0].getFolder();
		markVariant = r[0].getMarkVariant();
		ColumbaLogger.log.debug("src=" + folder);

		folder.markMessage(r[0].getUids(), markVariant , worker);
		
		
	}

}