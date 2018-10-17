controller.getModel().setAccountItem(config.get(i));

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
package org.columba.mail.gui.composer;

import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;

import javax.swing.JCheckBoxMenuItem;

import org.columba.mail.config.AccountItem;
import org.columba.mail.config.AccountList;
import org.columba.mail.config.MailConfig;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AccountController implements ItemListener {
	AccountView view;
	ComposerController controller;

	JCheckBoxMenuItem signMenuItem;
	JCheckBoxMenuItem encryptMenuItem;

	public AccountController(ComposerController controller) {
		this.controller = controller;
		
		view = new AccountView(this);
		
		AccountList config = MailConfig.getAccountList();

		for (int i = 0; i < config.count(); i++) {
			view.addItem(config.get(i));
			if (i == 0) {
				view.setSelectedItem(config.get(i));
				((ComposerModel)controller.getModel()).setAccountItem(config.get(i));
			}
		}

		view.addItemListener(this);
	}

	/*
	public void setSecurityMenuItems(
		JCheckBoxMenuItem signItem,
		JCheckBoxMenuItem encryptItem) {
		signMenuItem = signItem;
		encryptMenuItem = encryptItem;

		AccountItem item = (AccountItem) view.getSelectedItem();

		PGPItem pgpItem = item.getPGPItem();
		if( pgpItem.getBoolean("enabled") ) {
			signMenuItem.setEnabled(true);
			encryptMenuItem.setEnabled(true);
			
			model.setSignMessage(pgpItem.getBoolean("always_sign"));
			model.setEncryptMessage(pgpItem.getBoolean("always_encrypt"));
		}
	}
*/

	public void itemStateChanged(ItemEvent e) {
		if (e.getStateChange() == ItemEvent.SELECTED) {
			updateComponents(false);
			/*
			AccountItem item = (AccountItem) view.getSelectedItem();
			composerInterface.identityInfoPanel.set(item);
			
			PGPItem pgpItem = item.getPGPItem();
			signMenuItem.setEnabled(pgpItem.getBoolean("enabled"));
			signMenuItem.setSelected(pgpItem.getBoolean("always_sign"));

			encryptMenuItem.setEnabled(pgpItem.getBoolean("enabled"));
			encryptMenuItem.setSelected(pgpItem.getBoolean("always_encrypt"));
			*/
		}
	}

	public void updateComponents(boolean b) {
		if (b == true) {
			view.setSelectedItem(((ComposerModel)controller.getModel()).getAccountItem());
			
			/*
			encryptMenuItem.setSelected(model.isEncryptMessage());
			signMenuItem.setSelected(model.isSignMessage());
			*/
		} else {
			((ComposerModel)controller.getModel()).setAccountItem((AccountItem) view.getSelectedItem());
			
			/*
			model.setSignMessage(signMenuItem.isSelected());
			model.setEncryptMessage(encryptMenuItem.isSelected());
			*/
		}
	}

}