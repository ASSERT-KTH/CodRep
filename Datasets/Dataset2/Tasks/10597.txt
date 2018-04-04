part = folder.getMimePart(uids[0], address);

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.
package org.columba.mail.gui.attachment.command;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;

import javax.swing.JFileChooser;
import javax.swing.JOptionPane;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
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
		DefaultCommandReference[] references) {
		super(references);
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
                
                while (true) {
                        if (fileChooser.showSaveDialog(null) != JFileChooser.APPROVE_OPTION) {
                                return;
                        }
                        tempFile = fileChooser.getSelectedFile();
                        lastDir = tempFile.getParentFile();
                        if (tempFile.exists()) {
                                if (JOptionPane.showConfirmDialog(
                                null, "Overwrite File?", "Warning",
				JOptionPane.YES_NO_OPTION,
				JOptionPane.WARNING_MESSAGE) == JOptionPane.YES_OPTION) {
                                        break;
                                }
                        } else {
                                break;
                        }
		}

		Decoder decoder;
		MimeHeader header;

		header = part.getHeader();
		try {
			decoder = CoderRouter.getDecoder(header.contentTransferEncoding);

			decoder.decode(
				new ByteArrayInputStream(part.getBody().getBytes("ISO_8859_1")),
				new FileOutputStream(tempFile));

		} catch (Exception ex) {
			ex.printStackTrace();

			//setCancel(true);
		}
	}
}