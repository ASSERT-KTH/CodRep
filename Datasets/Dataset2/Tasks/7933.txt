ipcHelper.executeCommand(ExternalToolsHelper.getSALearn()+" --spam --dir" + path);

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandAdapter;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;

/**
 * @author fdietz
 *
 * command:
 * 
 *  sa-learn --spam
 * 
 * command description:
 * 
 * Learn the input message(s) as spam. If you have previously learnt any of 
 * the messages as ham, SpamAssassin will forget them first, then re-learn 
 * them as spam. Alternatively, if you have previously learnt them as spam, 
 * it'll skip them this time around.
 * 
 */
public class LearnSpamCommand extends FolderCommand {

	/**
	
		 * @param references
		 */
	public LearnSpamCommand(DefaultCommandReference[] references) {
		super(references);

	}
	/**
	 * @param frame
	 * @param references
	 */
	public LearnSpamCommand(
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
		Folder srcFolder =
			(Folder) adapter.getSourceFolderReferences()[0].getFolder();

		worker.setDisplayText(
			"Learning spam from " + srcFolder.getName() + "...");

		IPCHelper ipcHelper = new IPCHelper();

		String path = srcFolder.getDirectoryFile().getAbsolutePath();

		ColumbaLogger.log.debug("creating process..");
		ipcHelper.executeCommand("sa-learn --spam --dir" + path);
		
		int exitCode = ipcHelper.waitFor();
		ColumbaLogger.log.debug("exitcode=" + exitCode);
		
		String output = ipcHelper.getOutputString();
		ColumbaLogger.log.debug("retrieving output: "+output);
		
		worker.setDisplayText("SpamAssassin: "+output);

		ColumbaLogger.log.debug("wait for threads to join..");
		ipcHelper.waitForThreads();
	}

}