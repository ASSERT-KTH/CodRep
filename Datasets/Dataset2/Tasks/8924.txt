getFrameMediator().getSelectionManager().setSelection("mail.tree", refs);

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

package org.columba.mail.pop3.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.util.ListIterator;

import javax.swing.KeyStroke;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.command.POP3CommandReference;
import org.columba.mail.main.MailInterface;
import org.columba.mail.pop3.POP3ServerController;
import org.columba.mail.pop3.command.FetchNewMessagesCommand;
import org.columba.mail.util.MailResourceLoader;

public class ReceiveMessagesAction extends FrameAction {

	public ReceiveMessagesAction(AbstractFrameController controller) {
		super(
				controller,
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_file_receive"));
		setActionCommand("RECEIVE");
		setAcceleratorKey(
				KeyStroke.getKeyStroke(
					KeyEvent.VK_T, ActionEvent.CTRL_MASK));
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		
		// Select INBOX
		FolderCommandReference[] refs = new FolderCommandReference[1];
		refs[0] = new FolderCommandReference(MailInterface.treeModel.getFolder(101));
		getFrameController().getSelectionManager().setSelection("mail.tree", refs);
		
		// Fetch Messages
		
		ListIterator iterator = MailInterface.popServerCollection.getServerIterator();

		while( iterator.hasNext() ) {
			POP3ServerController controller =
				(POP3ServerController) iterator.next();

			boolean excludeFromCheckAll = controller.getAccountItem().getPopItem().getBoolean("exclude_from_checkall",false);
			
			if ( excludeFromCheckAll == true ) continue;
			  
			POP3CommandReference[] r = new POP3CommandReference[1];
			r[0] = new POP3CommandReference(controller);

			FetchNewMessagesCommand c =
				new FetchNewMessagesCommand(r);

			
			MainInterface.processor.addOp(c);
		}		
	}

}