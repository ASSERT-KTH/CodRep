public void updateSelectedGUI() throws Exception {

package org.columba.mail.gui.message.command;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.message.AbstractMessage;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class ViewMessageCommand extends FolderCommand {

	MimePart bodyPart;
	MimePartTree mimePartTree;
	HeaderInterface header;
	Folder folder;
	Object uid;
	

	/**
	 * Constructor for ViewMessageCommand.
	 * @param references
	 */
	public ViewMessageCommand(
		FrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NORMAL_OPERATION;
	}

	private void getData(
		Folder srcFolder,
		Object uid,
		WorkerStatusController wsc)
		throws Exception {
		
		this.folder = srcFolder;
		this.uid = uid;
		

		bodyPart = null;

		AbstractMessage message = srcFolder.getMessage(uid, wsc);
		header = message.getHeader();
		mimePartTree = srcFolder.getMimePartTree(uid, wsc);

		boolean viewhtml =
			MailConfig
				.getMainFrameOptionsConfig()
				.getWindowItem()
				.getHtmlViewer();

		// Which Bodypart shall be shown? (html/plain)

		if (viewhtml)
			bodyPart = mimePartTree.getFirstTextPart("html");
		else
			bodyPart = mimePartTree.getFirstTextPart("plain");

		if (bodyPart == null) {
			bodyPart = new MimePart();
			bodyPart.setBody(new String("<No Message-Text>"));
		} else
			bodyPart = srcFolder.getMimePart(uid, bodyPart.getAddress(), wsc);

	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		((MailFrameController) frameController).messageController.showMessage(
			bodyPart);

		if ((mimePartTree.count() > 1)
			|| (!mimePartTree.get(0).getHeader().contentType.equals("text"))) {
			(
				(
					MailFrameController) frameController)
						.attachmentController
						.setMimePartTree(
				mimePartTree);
			((MailFrameController) frameController)
				.getView()
				.showAttachmentViewer();
		} else
			((MailFrameController) frameController)
				.getView()
				.hideAttachmentViewer();

		((MailFrameController) frameController)
			.headerController
			.getView()
			.setHeader(
			header);

		((MailFrameController) frameController)
			.tableController
			.getMarkAsReadTimer()
			.restart( folder, uid);

	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		getData((Folder) r[0].getFolder(), r[0].getUids()[0], worker);
	}

}