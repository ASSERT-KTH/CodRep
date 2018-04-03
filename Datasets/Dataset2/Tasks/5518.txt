import org.columba.addressbook.gui.dialog.group.EditGroupDialog;

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
import org.columba.addressbook.folder.GroupListCard;
import org.columba.addressbook.gui.EditGroupDialog;
import org.columba.addressbook.gui.frame.AddressbookFrameMediator;
import org.columba.addressbook.util.AddressbookResourceLoader;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.util.ImageLoader;

/**
 * Add new groupw card to selected addressbook.
 * 
 * @author fdietz
 */
public class AddGroupCardAction extends DefaultTreeAction {
	public AddGroupCardAction(FrameMediator frameController) {
		super(
			frameController,
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_addgroup"));

		// tooltip text
		putValue(
			SHORT_DESCRIPTION,
			AddressbookResourceLoader
				.getString("menu", "mainframe", "menu_file_addgroup_tooltip")
				.replaceAll("&", ""));

		putValue(
			TOOLBAR_NAME,
			AddressbookResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_file_addgroup_toolbar"));

		// icons
		putValue(SMALL_ICON, ImageLoader.getSmallImageIcon("group_small.png"));
		putValue(LARGE_ICON, ImageLoader.getImageIcon("group.png"));
	}

	/**
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		AddressbookFrameMediator mediator =
			(AddressbookFrameMediator) frameMediator;

		// get selected folder
		AddressbookFolder folder =
			(AddressbookFolder) mediator.getTree().getSelectedFolder();

		if (folder == null) {
			return;
		}

		EditGroupDialog dialog = new EditGroupDialog(mediator.getView(), null);

		if (dialog.getResult()) {
			// Ok
			GroupListCard card = new GroupListCard();

			// TODO:move this code to dialog
			dialog.updateComponents(card, null, false);
			dialog.setVisible(true);

			// add new group to folder
			folder.add(card);

			// update table
			// TODO: fire event of table model instead
			mediator.getTable().getAddressbookModel().update();
		}
	}
}