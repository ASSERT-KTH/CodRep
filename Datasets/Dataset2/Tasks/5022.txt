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
import java.awt.event.ActionListener;

import javax.swing.ButtonGroup;
import javax.swing.JRadioButtonMenuItem;

import org.columba.core.action.IMenu;
import org.columba.core.config.TableItem;
import org.columba.core.gui.FrameController;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.util.MailResourceLoader;

public class SortMessagesMenu extends IMenu implements ActionListener {
	
	private ButtonGroup menuButtons;

	public SortMessagesMenu(FrameController controller) {
		super(controller, MailResourceLoader.getString(
		"menu",
		"mainframe",
		"menu_view_sort"));
		
		createSubMenu();
	}

	protected void createSubMenu() {
		TableItem item = ((MailFrameController)getController()).tableController.getHeaderTableItem();
		int headerCount= item.getChildCount();
		menuButtons = new ButtonGroup();
		JRadioButtonMenuItem headerMenuItem;
		
		for( int i=0; i<headerCount; i++) {
			headerMenuItem = new JRadioButtonMenuItem(item.getChildElement(i).getAttribute("name"));
			headerMenuItem.setActionCommand(Integer.toString(i));
			headerMenuItem.addActionListener(this);
			menuButtons.add(headerMenuItem);
			add(headerMenuItem);
		}
	}

	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent e) {
		int selectedColumn = Integer.parseInt(e.getActionCommand());
	}

}