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
package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

import javax.swing.KeyStroke;

import org.columba.core.action.CheckBoxAction;
import org.columba.core.gui.FrameController;
import org.columba.core.gui.util.SelectionChangedEvent;
import org.columba.core.gui.util.SelectionListener;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.TableChangeListener;
import org.columba.mail.gui.table.TableChangedEvent;
import org.columba.mail.gui.tree.FolderSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class ThreadedViewAction
	extends CheckBoxAction
	implements TableChangeListener, SelectionListener {

	/**
	 * Constructor for ThreadedViewAction.
	 * @param frameController
	 * @param name
	 * @param longDescription
	 * @param actionCommand
	 * @param small_icon
	 * @param big_icon
	 * @param mnemonic
	 * @param keyStroke
	 */
	public ThreadedViewAction(FrameController frameController) {
		super(
			frameController,
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_view_viewthreaded"),
			MailResourceLoader.getString(
				"menu",
				"mainframe",
				"menu_view_viewthreaded_tooltip"),
			"VIEW_THREADED",
			null,
			null,
			'0',
			KeyStroke.getKeyStroke(KeyEvent.VK_T, ActionEvent.CTRL_MASK));

		/*
		(
			(
				MailFrameController) frameController)
					.tableController
					.addTableChangedListener(
			this);
*/
		setEnabled(false);
	}

	public void tableChanged(TableChangedEvent e) {
		ColumbaLogger.log.info("event=" + e);

		if (e.getEventType() == TableChangedEvent.UPDATE) {
			Folder folder =
				(Folder) ((MailFrameController) frameController)
					.tableController
					.getTableSelectionManager()
					.getFolder();
			boolean enableThreadedView =
				folder.getFolderItem().getBoolean(
					"property",
					"enable_threaded_view",
					false);

			updateTable(enableThreadedView);

			getCheckBoxMenuItem().setSelected(enableThreadedView);

		}
	}

	public void actionPerformed(ActionEvent e) {
		/*
		JCheckBoxMenuItem item = (JCheckBoxMenuItem) e.getSource();

		Folder folder =
			(Folder) ((MailFrameController) frameController)
				.tableController
				.getTableSelectionManager()
				.getFolder();

		boolean enableThreadedView = item.isSelected();
		folder.getFolderItem().set(
			"property",
			"enable_threaded_view",
			enableThreadedView);
		*/
		
		updateTable(getState());
	}

	protected void updateTable(boolean enableThreadedView) {
		((MailFrameController) frameController)
			.tableController
			.getHeaderTableModel()
			.getTableModelThreadedView()
			.toggleView(enableThreadedView);

		((MailFrameController) frameController)
			.tableController
			.getView()
			.enableThreadedView(enableThreadedView);
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.util.SelectionListener#selectionChanged(org.columba.core.gui.util.SelectionChangedEvent)
	 */
	public void selectionChanged(SelectionChangedEvent e) {
		Folder[] selection = ((FolderSelectionChangedEvent) e).getSelected();
		if (selection.length == 1)
			setEnabled(true);
		else
			setEnabled(false);
	}

}