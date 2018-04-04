public void updateSelectedGUI() throws Exception {

package org.columba.mail.gui.attachment.command;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.util.TempFileStore;
import org.columba.main.MainInterface;
import org.columba.mail.coder.CoderRouter;
import org.columba.mail.coder.Decoder;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.MimeHeader;
import org.columba.mail.message.MimePart;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class OpenAttachmentCommand extends FolderCommand {

	MimePart part;
	File tempFile;

	/**
	 * Constructor for OpenAttachmentCommand.
	 * @param references
	 */
	public OpenAttachmentCommand(FrameController frame, DefaultCommandReference[] references) {
		super(frame, references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NORMAL_OPERATION;

	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		MainInterface.frameController.attachmentController.open(part, tempFile);
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		Folder folder = (Folder) r[0].getFolder();
		Object[] uids = r[0].getUids();

		Integer[] address = r[0].getAddress();

		part = folder.getMimePart(uids[0], address, worker);

		Decoder decoder;
		MimeHeader header;
		tempFile = null;

		header = part.getHeader();

		// If part is Message/Rfc822 we do not need to download anything because
		// we have already parsed the subMessage and can directly access the mime-parts

		if (!part.getHeader().getContentType().equals("message")) {

			try {
				String filename = part.getHeader().getFileName();
				if (filename != null) {
					tempFile = TempFileStore.createTempFile(filename);
				} else
					tempFile = TempFileStore.createTempFile();

				decoder =
					CoderRouter.getDecoder(header.contentTransferEncoding);

				decoder.decode(
					new ByteArrayInputStream(
						part.getBody().getBytes("US-ASCII")),
					new FileOutputStream(tempFile));

				//decoder.run();

			} catch (Exception ex) {
				ex.printStackTrace();

			}

		}
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