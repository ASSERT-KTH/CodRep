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

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.logging.Logger;

import javax.swing.JMenuBar;
import javax.swing.JMenuItem;

import org.columba.core.action.AbstractColumbaAction;

public class ExtendableMenuBar extends JMenuBar {

	private static final Logger LOG = Logger
			.getLogger("org.columba.core.gui.menu");

	private Hashtable map = new Hashtable();

	public ExtendableMenuBar() {
		super();
	}

	public void add(ExtendableMenu menu) {
		Enumeration e = menu.getSubmenuEnumeration();
		while (e.hasMoreElements()) {
			ExtendableMenu submenu = (ExtendableMenu) e.nextElement();
			map.put(submenu.getId(), submenu);
		}

		super.add(menu);
	}
	
	public void insert(ExtendableMenu menu) {
		Enumeration e = menu.getSubmenuEnumeration();
		while (e.hasMoreElements()) {
			ExtendableMenu submenu = (ExtendableMenu) e.nextElement();
			map.put(submenu.getId(), submenu);
		}
		
		super.add(menu, getMenuCount()-2);
		
	}

	public ExtendableMenu getMenu(String menuId) {
		if (map.containsKey(menuId) == false) {
			LOG.severe("no menu with id " + menuId + " found");
			return null;
		}

		ExtendableMenu menu = (ExtendableMenu) map.get(menuId);

		return menu;
	}

	public void insertMenuItem(String menuId, String placeholderId,
			JMenuItem menuItem) {
		if (map.containsKey(menuId) == false)
			throw new IllegalArgumentException("no menu with id " + menuId
					+ " found");

		ExtendableMenu menu = (ExtendableMenu) map.get(menuId);
		menu.insert(menuItem, placeholderId);
	}

	public void insertAction(String menuId, String placeholderId,
			AbstractColumbaAction action) {
		if (map.containsKey(menuId) == false)
			throw new IllegalArgumentException("no menu with id " + menuId
					+ " found");

		ExtendableMenu menu = (ExtendableMenu) map.get(menuId);
		menu.insert(action, placeholderId);
	}

}