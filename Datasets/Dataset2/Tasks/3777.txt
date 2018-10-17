setToolBarText(

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
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.util.MailResourceLoader;

public class NewMessageAction extends FrameAction {

	public NewMessageAction(AbstractFrameController controller) {
		super(controller, 
				MailResourceLoader.getString(
						"menu", "mainframe", "menu_message_new"));
		setToolBarName(
				MailResourceLoader.getString(
						"menu", "mainframe", "menu_message_new_toolbar"));
		setTooltipText(
				MailResourceLoader.getString(
						"menu", "mainframe", "menu_message_new_tooltip"));		
		setActionCommand("NEW_MESSAGE");
		setSmallIcon(ImageLoader.getSmallImageIcon("stock_edit-16.png"));
		setLargeIcon(ImageLoader.getImageIcon("stock_edit.png"));
		setAcceleratorKey(
				KeyStroke.getKeyStroke(
						KeyEvent.VK_M, ActionEvent.CTRL_MASK));		
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {

		// Open a new composer. Choice btw. text and html will be based on
		// stored option
		new ComposerController();
		
	}

}