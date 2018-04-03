import org.columba.core.main.MainInterface;

package org.columba.mail.smtp;

import javax.swing.JOptionPane;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.AddMessageCommand;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.main.MainInterface;

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
	public SendMessageCommand(DefaultCommandReference[] references) {
		super(references);
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
				item.getSpecialFoldersItem().getInteger("sent"));
		SendableMessage message =
			composerController.composerInterface.messageComposer.compose(
				worker);

		SMTPServer server = new SMTPServer(item);
		boolean open = server.openConnection();

		if (open) {

			try {
				server.sendMessage(message, worker);

				composerController.hideComposerWindow();

				FolderCommandReference[] ref = new FolderCommandReference[1];
				ref[0] = new FolderCommandReference(sentFolder);
				ref[0].setMessage(message);

				AddMessageCommand c = new AddMessageCommand(ref);

				MainInterface.processor.addOp(c);

				server.closeConnection();
			} catch (SMTPException e) {
				JOptionPane.showMessageDialog(
					null,
					e.getMessage(),
					"Error while sending",
					JOptionPane.ERROR_MESSAGE);
			} catch (Exception e) {
				e.printStackTrace();
			}

		}

	}

}