public void updateSelectedGUI() throws Exception {

package org.columba.mail.smtp;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.main.MainInterface;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.AddMessageCommand;
import org.columba.mail.gui.composer.ComposerController;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SendMessageCommand extends FolderCommand {

	/**
	 * Constructor for SendMessageCommand.
	 * @param frameController
	 * @param references
	 */
	public SendMessageCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
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
		ComposerCommandReference[] r =
			(ComposerCommandReference[]) getReferences();

		ComposerController composerController = r[0].getComposerController();

		AccountItem item = composerController.getModel().getAccountItem();
		Folder sentFolder =
			(Folder) MainInterface.treeModel.getFolder(
				Integer.parseInt(item.getSpecialFoldersItem().getSent()));
		SendableMessage message =
			composerController.composerInterface.messageComposer.compose();

		SMTPServer server = new SMTPServer(item);
		boolean open = server.openConnection();

		if (open) {
			server.sendMessage(message);

			server.closeConnection();
			
			composerController.hideComposerWindow();

			FolderCommandReference[] ref = new FolderCommandReference[1];
			ref[0] = new FolderCommandReference(sentFolder);
			ref[0].setMessage(message);

			AddMessageCommand c = new AddMessageCommand(frameController, ref);

			MainInterface.processor.addOp(c);

		}

	}

}