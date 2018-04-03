final ComposerController composerController = (ComposerController ) getFrameMediator();

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
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.ComposerCommandReference;
import org.columba.mail.folder.outbox.OutboxFolder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.main.MailInterface;
import org.columba.mail.smtp.command.SendMessageCommand;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class SendAction extends FrameAction {

	public SendAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "composer", "menu_file_send"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_file_send_tooltip"));

		// toolbar text
		setToolBarText(
				MailResourceLoader.getString(
					"menu", "composer", "menu_file_send_toolbar"));
		enableToolBarText(true);
		
		// action command
		setActionCommand("SEND");
		
		// large icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("send-24.png"));
		
		// small icon for menu
		setSmallIcon(ImageLoader.getSmallImageIcon("send-16.png"));
		
		// shortcut key
		setAcceleratorKey(
				KeyStroke.getKeyStroke(
					KeyEvent.VK_ENTER, ActionEvent.CTRL_MASK));
	
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		final ComposerController composerController = (ComposerController ) getFrameController();
		
		if (composerController.checkState())
			return;

		/*
		ComposerOperation op =
			new ComposerOperation(
				Operation.COMPOSER_SEND,
				0,
				composerInterface.composerController);
		
		MainInterface.crossbar.operate(op);
		*/

		OutboxFolder outboxFolder =
			(OutboxFolder) MailInterface.treeModel.getFolder(103);

		ComposerCommandReference[] r = new ComposerCommandReference[1];
		r[0] = new ComposerCommandReference(
				composerController,
				outboxFolder);

		SendMessageCommand c = new SendMessageCommand(r);

		MainInterface.processor.addOp(c);
	}
}