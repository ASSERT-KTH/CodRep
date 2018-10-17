((AbstractMailFrameController) getFrameMediator()).getTableSelection();

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

package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.gui.composer.command.ReplyToMailingListCommand;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class ReplyToListAction
	extends FrameAction
	implements SelectionListener {

	public ReplyToListAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_message_replyto"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_message_replyto_tooltip"));
		
		// action command
		setActionCommand("REPLY_MAILINGLIST");
		
		setEnabled(false);
		((AbstractMailFrameController) frameController).registerTableSelectionListener(
			this);
	}

	

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		FolderCommandReference[] r =
			((AbstractMailFrameController) getFrameController()).getTableSelection();
		MainInterface.processor.addOp(new ReplyToMailingListCommand(r));
	}
	/* (non-Javadoc)
			 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
			 */
	public void selectionChanged(SelectionChangedEvent e) {
		setEnabled(((TableSelectionChangedEvent) e).getUids().length > 0);
	}
}