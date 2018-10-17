import org.columba.ristretto.message.HeaderInterface;

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
package org.columba.mail.folder.command;

import org.columba.addressbook.folder.ContactCard;
import org.columba.addressbook.gui.tree.util.SelectAddressbookFolderDialog;
import org.columba.addressbook.parser.AddressParser;
import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.message.HeaderInterface;

/**
 * Add sender of the selected messages to addressbook.
 * <p>
 * A dialog asks the user the destination addressbook.
 * 
 * @author fdietz
 */
public class AddSenderToAddressbookCommand extends FolderCommand {

	org.columba.addressbook.folder.Folder selectedFolder;

	/**
	 * Constructor for AddSenderToAddressbookCommand.
	 * @param references
	 */
	public AddSenderToAddressbookCommand(DefaultCommandReference[] references) {
		super(references);
	}

	/**
	 * Constructor for AddSenderToAddressbookCommand.
	 * @param frame
	 * @param references
	 */
	public AddSenderToAddressbookCommand(
		AbstractFrameController frame,
		DefaultCommandReference[] references) {
		super(frame, references);
	}

	/**
	 * @see org.columba.core.command.Command#execute(org.columba.core.command.Worker)
	 */
	public void execute(Worker worker) throws Exception {
		FolderCommandReference[] r = (FolderCommandReference[]) getReferences();

		Object[] uids = r[0].getUids();
		Folder folder = (Folder) r[0].getFolder();
		
//		register for status events
		((StatusObservableImpl)folder.getObservable()).setWorker(worker);
		
		SelectAddressbookFolderDialog dialog =
			MainInterface
				.addressbookTreeModel
				.getSelectAddressbookFolderDialog();

		selectedFolder = dialog.getSelectedFolder();

		if (selectedFolder == null)
			return;

		for (int i = 0; i < uids.length; i++) {

			HeaderInterface header = folder.getMessageHeader(uids[i]);
			String sender = (String) header.get("From");

			addSender(sender);

		}

	}

	public void addSender(String sender) {
		if (sender == null)
			return;

		if (sender.length() > 0) {

			String address = AddressParser.getAddress(sender);
			System.out.println("address:" + address);

			if (!selectedFolder.exists(address)) {
				ContactCard card = new ContactCard();

				String fn = AddressParser.getDisplayname(sender);
				System.out.println("fn=" + fn);

				card.set("fn", fn);
				card.set("displayname", fn);
				card.set("email", "internet", address);

				selectedFolder.add(card);
			}
		}
	}

}