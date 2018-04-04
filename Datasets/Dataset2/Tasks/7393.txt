part.getBody().getBytes("ISO_8859_1")),

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

import org.columba.core.command.Command;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.FrameModel;
import org.columba.core.main.MainInterface;
import org.columba.core.util.TempFileStore;
import org.columba.mail.coder.CoderRouter;
import org.columba.mail.coder.Decoder;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.temp.TempFolder;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.messageframe.MessageFrameController;
import org.columba.mail.gui.mimetype.MimeTypeViewer;
import org.columba.mail.message.AbstractMessage;
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
	// true, if showing a message as attachment
	boolean inline = false;
	TempFolder tempFolder;
	Object tempMessageUid;

	/**
	 * Constructor for OpenAttachmentCommand.
	 * @param references
	 */
	public OpenAttachmentCommand(DefaultCommandReference[] references) {
		super(references);

		priority = Command.REALTIME_PRIORITY;
		commandType = Command.NORMAL_OPERATION;

	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		MimeHeader header = part.getHeader();

		if (header.getContentType().toLowerCase().indexOf("message") != -1) {
			
			MessageFrameController c = (MessageFrameController) FrameModel.openView("MessageFrame");
			
			FolderCommandReference[] r = new FolderCommandReference[1];
			Object[] uidList = new Object[1];
			uidList[0] = tempMessageUid;
			
			c.setTableSelection(r);
			
			r[0] = new FolderCommandReference(tempFolder, uidList);
			MainInterface.processor.addOp(
						new ViewMessageCommand(c,
						r));
						
			
			
			
			//inline = true;
			//openInlineMessage(part, tempFile);
		} else {
			//inline = false;
			MimeTypeViewer viewer = new MimeTypeViewer();
			viewer.open(header, tempFile);
		}
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

		if (part.getHeader().getContentType().equals("message")) {
			tempFolder = MainInterface.treeModel.getTempFolder();
			tempMessageUid = tempFolder.addMessage( (AbstractMessage) part.getContent(), worker );
			
			inline = true;
		}
		else
		{
		

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