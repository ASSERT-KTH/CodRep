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
import java.util.ListIterator;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.pop3.POP3ServerController;
import org.columba.mail.pop3.command.FetchNewMessagesCommand;
import org.columba.mail.util.MailResourceLoader;

public class ReceiveSendAction extends FrameAction {

	public ReceiveSendAction(AbstractFrameController controller) {
		super(
				controller,
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_file_receivesend"));
					
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_file_receivesend_tooltip"));
					
		// toolbar text
		setToolBarName(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_file_receivesend_toolbar"));
		
		// action command
		setActionCommand("RECEIVESEND");

		// small icon for menu
		setSmallIcon(ImageLoader.getSmallImageIcon("send-receive.png"));
		
		// large icon for toolbar
		setLargeIcon(ImageLoader.getImageIcon("send-24-receive.png"));
		
		// shortcut key
		setAcceleratorKey(
				KeyStroke.getKeyStroke(KeyEvent.VK_F9, 0));
		
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		ListIterator iterator = MainInterface.popServerCollection.getServerIterator(); 

		while (iterator.hasNext()) {
			POP3ServerController controller =
				(POP3ServerController) iterator.next();

			boolean excludeFromCheckAll = controller.getAccountItem().getPopItem().getBoolean("exclude_from_checkall",false);
			
			if (excludeFromCheckAll) continue;
						
			POP3CommandReference[] r = new POP3CommandReference[1];
			r[0] = new POP3CommandReference(controller);

			FetchNewMessagesCommand c =
				new FetchNewMessagesCommand( r);

			MainInterface.processor.addOp(c);
		}
	}
}