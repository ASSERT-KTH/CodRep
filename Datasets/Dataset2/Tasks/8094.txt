Object[] uids = srcFolder.getUids();

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandAdapter;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;

/**
 * @author fdietz
 *
 * let spamassassin go through all messages:
 * - analyze message
 * - tag as spam/ham in adding two more headerfields
 * 
 * added headerfields are:
 *  X-Spam-Level: digit number
 *  X-Spam-Flag: YES/NO (create a filter on this headerfield)
 * 
 */
public class AnalyzeFolderCommand extends FolderCommand {

	Folder srcFolder;

	/**
	
		 * @param references
		 */
	public AnalyzeFolderCommand(DefaultCommandReference[] references) {
		super(references);

	}
	/**
	 * @param frame
	 * @param references
	 */
	public AnalyzeFolderCommand(
		AbstractFrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);

	}

	/* (non-Javadoc)
	 * @see org.columba.core.command.Command#execute(org.columba.core.command.Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		FolderCommandAdapter adapter = new FolderCommandAdapter(r);

		// there can be only one reference for this command
		srcFolder = (Folder) adapter.getSourceFolderReferences()[0].getFolder();

		worker.setDisplayText(
			"Applying analyzer to" + srcFolder.getName() + "...");

		Object[] uids = srcFolder.getUids(worker);

		for (int i = 0; i < uids.length; i++) {
			AnalyzeMessageCommand.addHeader(srcFolder, uids[i], worker);
		}

	}

}