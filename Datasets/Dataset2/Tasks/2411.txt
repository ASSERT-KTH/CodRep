folder.markMessage(r[0].getUids(), markVariant , worker);

package org.columba.mail.folder.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.gui.table.util.MessageNode;
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
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
	}

	public void updateGUI() throws Exception {
		MailFrameController frame = (MailFrameController) frameController;
		TableChangedEvent ev = new TableChangedEvent( TableChangedEvent.MARK, folder, uids, markVariant );
		 
		frame.tableController.tableChanged(ev);
		
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

		folder.markMessage(MessageNode.toUidArray( (MessageNode[]) uids ), markVariant , worker);
		
		
	}

}