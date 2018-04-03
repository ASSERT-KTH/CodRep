import org.columba.core.gui.frame.FrameController;

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

package org.columba.mail.smtp;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.util.MailResourceLoader;

public class SendAllMessagesAction extends FrameAction {

	public SendAllMessagesAction(FrameController controller) {
		super(
			controller,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_sendunsentmessages"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_sendunsentmessages_toolbar"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_sendunsentmessages_tooltip"),
			"SENDALL",
			null,
			ImageLoader.getImageIcon("send-24.png"),
			'0',
			KeyStroke.getKeyStroke(KeyEvent.VK_F10, 0));
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		FolderCommandReference[] r = new FolderCommandReference[1];
		OutboxFolder folder =
			(OutboxFolder) MainInterface.treeModel.getFolder(103);

		r[0] = new FolderCommandReference(folder);

		SendAllMessagesCommand c =
			new SendAllMessagesCommand(frameController, r);

		MainInterface.processor.addOp(c);		
	}

}