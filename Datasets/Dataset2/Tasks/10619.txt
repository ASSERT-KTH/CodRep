HeaderItem item = mediator.getTable().getSelectedItem();

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.addressbook.gui.action;

import java.awt.event.ActionEvent;

import org.columba.addressbook.folder.AddressbookFolder;
import org.columba.addressbook.folder.ContactCard;
import org.columba.addressbook.folder.GroupListCard;
import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;
import org.columba.addressbook.gui.EditGroupDialog;
import org.columba.addressbook.gui.dialog.contact.ContactDialog;
import org.columba.addressbook.gui.frame.AddressbookFrameMediator;
import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.util.ImageLoader;

/**
 * Edit properties of selected contact or group.
 * 
 * @author fdietz
 */
public class EditPropertiesAction extends DefaultTableAction {
	public EditPropertiesAction(FrameMediator frameController) {
		super(
			frameController,
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_properties"));

		// tooltip text
		putValue(
			SHORT_DESCRIPTION,
			AddressbookResourceLoader
				.getString("menu", "mainframe", "menu_file_properties_tooltip")
				.replaceAll("&", ""));

		putValue(
			TOOLBAR_NAME,
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_properties_toolbar"));

		// icons
		putValue(
			SMALL_ICON,
			ImageLoader.getSmallImageIcon("stock_edit-16.png"));
		putValue(LARGE_ICON, ImageLoader.getImageIcon("stock_edit.png"));

		setEnabled(false);
	}

	/**
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		AddressbookFrameMediator mediator =
			(AddressbookFrameMediator) frameMediator;

		// get selected contact/group card
		Object[] uids = mediator.getTable().getUids();

		// get selected folder
		AddressbookFolder folder =
			(AddressbookFolder) mediator.getTree().getSelectedFolder();

		if (uids.length == 0) {
			return;
		}

		//TODO: Why do we need this HeaderItem anyway?
		//      -> just get the card from the folder, wether it is a contact or
		// group card
		HeaderItem item = mediator.getTable().getView().getSelectedItem();

		if (item.isContact()) {
			ContactCard card = (ContactCard) folder.get(uids[0]);
			ContactDialog dialog = new ContactDialog(mediator.getView());

			// TODO: move this code to dialog
			dialog.updateComponents(card, true);
			dialog.setVisible(true);

			if (dialog.getResult()) {
				//TODO:move this code to dialog
				dialog.updateComponents(card, false);

				// modify card properties in folder
				folder.modify(card, uids[0]);

				// update table
				// TODO: fire event of table model instead
				mediator.getTable().getAddressbookModel().update();
			}
		} else {
			GroupListCard card = (GroupListCard) folder.get(uids[0]);

			EditGroupDialog dialog =
				new EditGroupDialog(mediator.getView(), null);

			Object[] groupUids = card.getUids();
			HeaderItemList members = folder.getHeaderItemList(groupUids);
			// TODO: move this code to dialog
			dialog.updateComponents(card, members, true);
			dialog.setVisible(true);

			if (dialog.getResult()) {
				// TODO: move this code to dialog
				dialog.updateComponents(card, null, false);

				// modify card properties in folder
				folder.modify(card, uids[0]);

				// update table
				// TODO: fire event of table model instead
				mediator.getTable().getAddressbookModel().update();
			}
		}
	}
}