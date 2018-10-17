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

import java.util.Vector;

import javax.swing.JOptionPane;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.gui.FrameController;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.SendableMessage;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.MoveMessageCommand;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.folder.outbox.SendListManager;
import org.columba.core.main.MainInterface;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class SendAllMessagesCommand extends FolderCommand {

	protected SendListManager sendListManager = new SendListManager();
	protected OutboxFolder outboxFolder;

	/**
	 * Constructor for SendAllMessagesCommand.
	 * @param frameController
	 * @param references
	 */
	public SendAllMessagesCommand(
		FrameController frameController,
		DefaultCommandReference[] references) {
		super(frameController, references);
	}


	/**
	 * @see org.columba.core.command.Command#execute(Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		outboxFolder = (OutboxFolder) r[0].getFolder();

		Object[] uids = outboxFolder.getUids(worker);

		for (int i = 0; i < uids.length; i++) {
			if (outboxFolder.exists(uids[i], worker) == true) {
				SendableMessage message =
					(SendableMessage) outboxFolder.getMessage(uids[i], worker);
				sendListManager.add(message);

			}
		}

		int actAccountUid = -1;
		Vector sentList = new Vector();
		boolean open = false;
		SMTPServer smtpServer = null;
		Folder sentFolder = null;
		while (sendListManager.hasMoreMessages()) {
			SendableMessage message = sendListManager.getNextMessage();

			if (message.getAccountUid() != actAccountUid) {

				// doesn't make any sense here
				/*
				if (sentList.size() != 0) {

					sentList.clear();
				}
				*/

				actAccountUid = message.getAccountUid();

				AccountItem accountItem =
					MailConfig
						.getAccountList()
						.uidGet(actAccountUid);

				sentFolder =
					(Folder) MainInterface.treeModel.getFolder(
						Integer.parseInt(
							accountItem.getSpecialFoldersItem().get("sent")));
				smtpServer = new SMTPServer(accountItem);

				open = smtpServer.openConnection();

			}

			if (open) {
				try {
					smtpServer.sendMessage(message, worker);

					sentList.add(message.getHeader().get("columba.uid") );
				}
				catch( SMTPException e ) {
					JOptionPane.showMessageDialog(null, e.getMessage(), "Error while sending", JOptionPane.ERROR_MESSAGE);					
				}
			}
		}

		if (sentList.size() > 0) {
			moveToSentFolder(sentList, sentFolder);
			sentList.clear();
		}
	}

	protected void moveToSentFolder(Vector v, Folder sentFolder) {
		FolderCommandReference[] r = new FolderCommandReference[2];
			r[0] = new FolderCommandReference(outboxFolder, v.toArray() );
			r[1] = new FolderCommandReference(sentFolder);

			MoveMessageCommand c = new MoveMessageCommand( r);

			MainInterface.processor.addOp(c);
		
	}

}