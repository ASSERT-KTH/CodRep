import org.columba.core.plugin.MenuPluginHandler;

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
package org.columba.core.gui.menu;

import java.awt.event.MouseAdapter;

import javax.swing.JMenu;
import javax.swing.JMenuBar;

import org.columba.core.action.BasicAction;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.*;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.xml.XmlElement;

public class Menu extends JMenuBar {

	private MouseAdapter handler;

	private CMenu fetchMessageSubmenu;
	private CMenu manageSubmenu;
	private CMenu sortSubMenu;

	private JMenu fileMenu;
	private JMenu editMenu;
	private JMenu viewMenu;
	private JMenu folderMenu;
	private JMenu messageMenu;
	private JMenu utilitiesMenu;
	private JMenu helpMenu;

	//XmlElement menuRoot;

	private AbstractFrameController frameController;

	protected MenuBarGenerator menuGenerator;

	public Menu(String xmlRoot, AbstractFrameController frameController) {
		super();

		this.frameController = frameController;

		menuGenerator =
			createMenuBarGeneratorInstance(xmlRoot, frameController);

		menuGenerator.createMenuBar(this);

		try {

			(
				(MenuPluginHandler) MainInterface.pluginManager.getHandler(
					"org.columba.core.menu")).insertPlugins(
				this);
		} catch (PluginHandlerNotFoundException ex) {
			NotifyDialog d = new NotifyDialog();
			d.showDialog(ex);
		}
	}

	public MenuBarGenerator createMenuBarGeneratorInstance(
		String xmlRoot,
		AbstractFrameController frameController) {
		if (menuGenerator == null) {
			menuGenerator = new MenuBarGenerator(frameController, xmlRoot);
		}

		return menuGenerator;
	}

	public void extendMenuFromFile(String path) {
		menuGenerator.extendMenuFromFile(path);
		menuGenerator.createMenuBar(this);
	}

	public void extendMenu(XmlElement menuExtension) {
		menuGenerator.extendMenu(menuExtension);
		menuGenerator.createMenuBar(this);
	}

	public void addMenuEntry(String id, BasicAction action) {

		CMenuItem menuItem = new CMenuItem(action);
		menuItem.addMouseListener(handler);

		JMenu menu = getMenu(id);
		menu.add(menuItem);

	}

	public JMenu getMenu(String id) {

		for (int i = 0; i < getMenuCount(); i++) {
			JMenu menu = (JMenu) getComponent(i);

			if (menu.getActionCommand().equalsIgnoreCase(id)) {
				// found the right menu

				return menu;
			}
		}

		return null;
	}

	public void addMenuSeparator(String id) {

		for (int i = 0; i < getMenuCount(); i++) {
			JMenu menu = (JMenu) getComponent(i);

			if (menu.getActionCommand().equalsIgnoreCase(id)) {
				// found the right menu

				menu.addSeparator();
			}
		}

	}

}