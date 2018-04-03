//table.setupRenderer();

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.addressbook.gui.frame;

import java.awt.BorderLayout;
import java.awt.Container;

import javax.swing.BorderFactory;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;

import org.columba.addressbook.gui.menu.AddressbookMenu;
import org.columba.addressbook.gui.table.TableView;
import org.columba.addressbook.gui.tree.TreeView;
import org.columba.addressbook.main.AddressbookInterface;
import org.columba.core.gui.frame.AbstractFrameView;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.menu.Menu;
import org.columba.core.gui.toolbar.ToolBar;
import org.columba.core.gui.util.UIFSplitPane;

public class AddressbookFrameView extends AbstractFrameView {

	public AddressbookFrameView(FrameMediator frameController) {
		super(frameController);

	}

	/**
	 * @see org.columba.core.gui.FrameView#createMenu(org.columba.core.gui.FrameController)
	 */
	protected Menu createMenu(FrameMediator controller) {
		Menu menu =
			new AddressbookMenu("org/columba/core/action/menu.xml", controller);
		menu.extendMenuFromFile("org/columba/addressbook/action/menu.xml");

		return menu;
	}

	/**
	 * @see org.columba.core.gui.FrameView#createToolbar(org.columba.core.gui.FrameController)
	 */
	protected ToolBar createToolbar(FrameMediator controller) {
		return new ToolBar(
			AddressbookInterface.config.get("main_toolbar").getElement(
				"toolbar"),
			controller);
	}

	public void init(TreeView tree, TableView table) {
		Container c = getContentPane();

		table.setupRenderer();

		JScrollPane treeScrollPane = new JScrollPane(tree);
		treeScrollPane.setBorder(BorderFactory.createEmptyBorder(2, 2, 2, 2));
		
		JScrollPane tableScrollPane = new JScrollPane(table);
		
		JSplitPane splitPane =
			new UIFSplitPane(JSplitPane.HORIZONTAL_SPLIT, treeScrollPane, tableScrollPane);
		splitPane.setBorder(null);

		c.add(splitPane, BorderLayout.CENTER);

	}
}