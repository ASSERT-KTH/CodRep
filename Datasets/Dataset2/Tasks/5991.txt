public void updateGUI() throws Exception {

package org.columba.mail.gui.message.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class ViewMessageSourceCommand extends FolderCommand {

	String source;

	/**
	 * Constructor for ViewMessageSourceCommand.
	 * @param frameController
	 * @param references
	 */
	public ViewMessageSourceCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateSelectedGUI() throws Exception {
		(
			(
				MailFrameController) frameController)
					.messageController
					.showMessageSource(
			source);

		((MailFrameController) frameController)
			.getView()
			.hideAttachmentViewer();

	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		MailFrameController mailFrameController =
			(MailFrameController) frameController;

		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Object[] uids = r[0].getUids();

		Folder folder = (Folder) r[0].getFolder();

		Object[] destUids = new Object[uids.length];
		Object uid = uids[0];
		source = folder.getMessageSource(uid, worker);

	}
}