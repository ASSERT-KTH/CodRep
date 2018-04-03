public void updateGUI() throws Exception {

package org.columba.mail.gui.composer.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.MessageBuilder;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.Message;
import org.columba.mail.message.MimePartTree;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class ForwardCommand extends FolderCommand {

	ComposerController controller;
	/**
	 * Constructor for ForwardCommand.
	 * @param frameController
	 * @param references
	 */
	public ForwardCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateSelectedGUI() throws Exception {
		controller.showComposerWindow();
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {

		Folder folder =
			(Folder) ((FolderCommandReference) getReferences()[0]).getFolder();
		Object[] uids = ((FolderCommandReference) getReferences()[0]).getUids();

		Message message = (Message) folder.getMessage(uids[0], worker);

		ColumbaHeader header = (ColumbaHeader) message.getHeader();
		MimePartTree mimePartTree = folder.getMimePartTree(uids[0], worker);

		String source = folder.getMessageSource(uids[0], worker);
		message.setSource(source);

		controller = new ComposerController(frameController);

		MessageBuilder.getInstance().createMessage(
			message,
			controller.getModel(),
			MessageBuilder.FORWARD);

	}

	/**
	 * @see org.columba.core.command.Command#undo(Worker)
	 */
	public void undo(Worker worker) throws Exception {
	}

	/**
	 * @see org.columba.core.command.Command#redo(Worker)
	 */
	public void redo(Worker worker) throws Exception {
	}

}