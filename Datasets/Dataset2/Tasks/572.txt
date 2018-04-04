controller.updateComponents(true);

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
package org.columba.mail.gui.composer.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.MessageBuilder;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
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
public class OpenMessageWithComposerCommand extends FolderCommand {

	ComposerController controller;

	/**
	 * Constructor for OpenMessageInComposerCommand.
	 * @param frameController
	 * @param references
	 */
	public OpenMessageWithComposerCommand(DefaultCommandReference[] references) {
		super(references);
	}

	/**
	 * @see org.columba.core.command.Command#updateGUI()
	 */
	public void updateGUI() throws Exception {
		//controller.showComposerWindow();
	}

	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		Folder folder =
			(Folder) ((FolderCommandReference) getReferences()[0]).getFolder();
		Object[] uids = ((FolderCommandReference) getReferences()[0]).getUids();

		Message message = new Message();

		ColumbaHeader header =
			(ColumbaHeader) folder.getMessageHeader(uids[0], worker);
		message.setHeader(header);
		MimePartTree mimePartTree = folder.getMimePartTree(uids[0], worker);
		message.setMimePartTree(mimePartTree);

		String source = folder.getMessageSource(uids[0], worker);
		message.setSource(source);

		ComposerModel model = new ComposerModel();
		
		controller = (ComposerController) model.openView();

		MessageBuilder.openMessage(message, model);
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