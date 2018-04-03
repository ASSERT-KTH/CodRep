import org.columba.core.gui.action.AbstractColumbaAction;

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
package org.columba.core.gui.menu;

import java.awt.event.ActionEvent;

import javax.swing.JCheckBoxMenuItem;
import javax.swing.JFrame;
import javax.swing.JMenuItem;
import javax.swing.JRadioButtonMenuItem;

import org.columba.core.action.AbstractColumbaAction;

public class MenuTest {
	private static final String MENUID1 = "menu1";

	private static final String MENUID2 = "menu2";

	private static final String PLACEHOLDER1 = "placeholder1";

	private static final String PLACEHOLDER2 = "placeholder2";

	private ExtendableMenu createMenu() {

		ExtendableMenu menu = new ExtendableMenu(MENUID1, "menu2");

		menu.add(new JMenuItem("test1"));
		menu.add(new JCheckBoxMenuItem("test2"));
		menu.addPlaceholder(PLACEHOLDER1);
		menu.add(new JRadioButtonMenuItem("test4"));

		menu.insert(createAction("sub-test1"), PLACEHOLDER1);

		ExtendableMenu submenu = new ExtendableMenu(MENUID2, "sublabel1");

		submenu.add(createAction("test5"));
		submenu.addPlaceholder(PLACEHOLDER2);
		menu.add(submenu);

		submenu.insert(createAction("sub-test2"), PLACEHOLDER2);

		menu.add(createAction("test7"));

		return menu;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		MenuTest test = new MenuTest();

		ExtendableMenu menu = test.createMenu();

		JFrame frame = new JFrame();
		frame.setSize(640, 480);
		ExtendableMenuBar mb = new ExtendableMenuBar();
		mb.add(menu);

		mb.insertMenuItem(MENUID1, PLACEHOLDER1, new JMenuItem("dynamic item"));
		mb.insertMenuItem(MENUID2, PLACEHOLDER2, new JMenuItem(
				"dynamic subitem 2"));

		frame.setJMenuBar(mb);
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setLocationRelativeTo(null);
		frame.setVisible(true);
	}

	private TestAction createAction(String str) {
		return new TestAction(str);
	}

	class TestAction extends AbstractColumbaAction {
		public TestAction(String str) {
			super(null, str);
		}

		public void actionPerformed(ActionEvent e) {
			// do nothing
		}
	}
}