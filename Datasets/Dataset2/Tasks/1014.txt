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

package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;

import org.columba.core.action.FrameAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.CopyMessageCommand;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment go to 
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class CopyMessageAction
	extends FrameAction
	implements SelectionListener {

	public CopyMessageAction(AbstractFrameController frameController) {
		super(
				frameController,
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_message_copy"));
		
		// toolbar text
		setToolBarName(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_message_copy_toolbar"));
		
		// tooltip text
		setTooltipText(
				MailResourceLoader.getString(
					"menu", "mainframe", "menu_message_copy_tooltip"));
		
		// action command
		setActionCommand("COPY_MESSAGE");
		
		// icons
		setSmallIcon(ImageLoader.getSmallImageIcon("copymessage_small.png"));
		setLargeIcon(ImageLoader.getImageIcon("copy-message.png"));
		
		// disable toolbar text
		enableToolBarText(false);
		
		setEnabled(false);
		((AbstractMailFrameController) frameController).registerTableSelectionListener(
			this);
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent evt) {
		SelectFolderDialog dialog =
			MainInterface.treeModel.getSelectFolderDialog();

		if (dialog.success()) {

			Folder destFolder = dialog.getSelectedFolder();

			FolderCommandReference[] result = new FolderCommandReference[2];
			FolderCommandReference[] r1 =
			((AbstractMailFrameController) getFrameController()).getTableSelection();
			FolderCommandReference r2 = new FolderCommandReference(destFolder);

			result[0] = r1[0];
			result[1] = r2;
			CopyMessageCommand c = new CopyMessageCommand(result);

			MainInterface.processor.addOp(c);
		}
	}

	/* (non-Javadoc)
			 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
			 */
	public void selectionChanged(SelectionChangedEvent e) {
		setEnabled(((TableSelectionChangedEvent) e).getUids().length > 0);
	}
}