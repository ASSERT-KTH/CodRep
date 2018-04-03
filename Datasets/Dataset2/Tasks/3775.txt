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

package org.columba.mail.gui.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.util.MailResourceLoader;

public class NewMessageAction extends FrameAction {

	public NewMessageAction(FrameController controller) {
		super(
			controller,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_new"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_new_toolbar"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_message_new_tooltip"),
			"NEW_MESSAGE",
			ImageLoader.getSmallImageIcon("stock_edit-16.png"),
			ImageLoader.getImageIcon("stock_edit.png"),
			'N',
			KeyStroke.getKeyStroke(KeyEvent.VK_M, ActionEvent.CTRL_MASK));
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		//((MailFrameModel)MainInterface.frameModel).getComposerModel().openView();
		new ComposerModel().openView();
		
		/*
		ComposerController controller = new ComposerController();
		controller.showComposerWindow();
		*/
	}

}