public void updateSelectedGUI() throws Exception {

package org.columba.mail.gui.attachment.command;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;

import javax.swing.JFileChooser;
import javax.swing.JOptionPane;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.core.util.cFileChooser;
import org.columba.core.util.cFileFilter;
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
public class SaveAttachmentCommand extends FolderCommand {

	File tempFile = null;
	MimePart part;
	static File lastDir = null;

	/**
	 * Constructor for SaveAttachmentCommand.
	 * @param frameController
	 * @param references
	 */
	public SaveAttachmentCommand(
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
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();
		Folder folder = (Folder) r[0].getFolder();
		Object[] uids = r[0].getUids();

		Integer[] address = r[0].getAddress();

		part = folder.getMimePart(uids[0], address, worker);

		String fileName = part.getHeader().getContentParameter("name");
		if (fileName == null)
			fileName = part.getHeader().getDispositionParameter("filename");

		cFileChooser fileChooser;

		if (lastDir == null)
			fileChooser = new cFileChooser();
		else
			fileChooser = new cFileChooser(lastDir);

		cFileFilter fileFilter = new cFileFilter();
		fileFilter.acceptFilesWithProperty(cFileFilter.FILEPROPERTY_FILE);

		fileChooser.setDialogTitle("Save Attachment as ...");
		if (fileName != null)
			fileChooser.forceSelectedFile(new File(fileName));

		fileChooser.setSelectFilter(fileFilter);
		int returnVal = fileChooser.showSaveDialog(null);

		if (returnVal == JFileChooser.APPROVE_OPTION) {
			tempFile = fileChooser.getSelectedFile();
		}

		lastDir = tempFile.getParentFile();

		if (tempFile.exists()) {
			Object[] options = { "OK", "CANCEL" };
			JOptionPane.showOptionDialog(
				null,
				"Overwrite File?",
				"Warning",
				JOptionPane.DEFAULT_OPTION,
				JOptionPane.WARNING_MESSAGE,
				null,
				options,
				options[0]);
		}

		Decoder decoder;
		MimeHeader header;

		header = part.getHeader();
		try {
			decoder = CoderRouter.getDecoder(header.contentTransferEncoding);

			/*
			decoder.setupDecoder(
				new StringReader(part.getBody()),
				new FileWriter(tempFile));
			*/
			//setText("Running Decoder ... ");

			decoder.decode(
				new ByteArrayInputStream(part.getBody().getBytes("US-ASCII")),
				new FileOutputStream(tempFile));

			//decoder.run();

		} catch (Exception ex) {
			ex.printStackTrace();

			//setCancel(true);
		}
	}

}