import org.columba.core.io.TempFileStore;

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
package org.columba.mail.gui.message.command;

import java.io.File;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.io.DiskIO;
import org.columba.core.util.TempFileStore;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.mimetype.MimeTypeViewer;
import org.columba.mail.message.MimeHeader;

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
	File tempFile;

	/**
	 * Constructor for ViewMessageSourceCommand.
	 * @param frameController
	 * @param references
	 */
	public ViewMessageSourceCommand(
		AbstractFrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		MimeTypeViewer viewer = new MimeTypeViewer();
		MimeHeader header = new MimeHeader();
		viewer.open(header, tempFile);

	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		AbstractMailFrameController mailFrameController =
			(AbstractMailFrameController) frameController;

		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Object[] uids = r[0].getUids();

		Folder folder = (Folder) r[0].getFolder();
//		register for status events
		((StatusObservableImpl)folder.getObservable()).setWorker(worker);

		Object[] destUids = new Object[uids.length];
		Object uid = uids[0];
		source = folder.getMessageSource(uid);

		try {

			tempFile = TempFileStore.createTempFile();
			DiskIO.saveStringInFile(tempFile, source);
		} catch (Exception ex) {
			ex.printStackTrace();

		}
	}
}