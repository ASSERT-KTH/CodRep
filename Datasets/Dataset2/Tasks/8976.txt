import org.columba.core.gui.frame.FrameController;

/*
 * Created on 24.03.2003
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.folder.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.ImportFolderCommandReference;
import org.columba.mail.folder.mailboximport.DefaultMailboxImporter;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ImportMessageCommand extends FolderCommand {

	/**
	 * @param references
	 */
	public ImportMessageCommand(DefaultCommandReference[] references) {
		super(references);
		
	}

	/**
	 * @param frame
	 * @param references
	 */
	public ImportMessageCommand(
		FrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);
		
	}

	/* (non-Javadoc)
	 * @see org.columba.core.command.Command#execute(org.columba.core.command.Worker)
	 */
	public void execute(Worker worker) throws Exception {
		ImportFolderCommandReference[] r = (ImportFolderCommandReference[]) getReferences();
		
		DefaultMailboxImporter importer = r[0].getImporter();
		
		importer.run(worker);
		

	}

}