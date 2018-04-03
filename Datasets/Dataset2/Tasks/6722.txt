((ComposerController) getFrameMediator());

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

package org.columba.mail.gui.composer.action;

import java.awt.event.ActionEvent;

import org.columba.addressbook.gui.SelectAddressDialog;
import org.columba.core.action.FrameAction;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class AddressbookAction extends FrameAction {

	public AddressbookAction(ComposerController composerController) {
		super(
				composerController, 
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_addressbook"));

		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_message_addressbook_tooltip"));
		
		// action command
		setActionCommand("ADDRESSBOOK");
		
		// large icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("contact.png"));
		
		// small icon for menu
		setSmallIcon(ImageLoader.getImageIcon("contact_small.png"));
		
		// disable text in toolbar
		enableToolBarText(false);

	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {

		ComposerController composerController =
			((ComposerController) getFrameController());

		composerController.getHeaderController().cleanupHeaderItemList();

		SelectAddressDialog dialog =
			new SelectAddressDialog(
				composerController.getView(),
				composerController.getHeaderController().getHeaderItemLists());

		org.columba.addressbook.folder.Folder folder =
			(org.columba.addressbook.folder.Folder) MainInterface
				.addressbookTreeModel
				.getFolder(101);
		dialog.setHeaderList(folder.getHeaderItemList());

		dialog.setVisible(true);

		composerController.getHeaderController().setHeaderItemLists(
			dialog.getHeaderItemLists());

	}

}