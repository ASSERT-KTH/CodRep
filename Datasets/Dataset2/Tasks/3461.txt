FolderCommandReference r = ((MailFrameMediator) getFrameMediator())

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
package org.columba.mail.gui.table.action;

import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JMenuItem;

import org.columba.core.action.IMenu;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.gui.selection.SelectionChangedEvent;
import org.columba.core.gui.selection.SelectionListener;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.command.ColorMessageCommand;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.table.selection.TableSelectionChangedEvent;
import org.columba.mail.util.MailResourceLoader;

/**
 * Creates a menu with a list of colors to select.
 * 
 * @author fdietz
 */

public class ColorMessageMenu extends IMenu implements ActionListener,
		SelectionListener {
	// TODO: add central place, which keeps a list of all possible
	//       colors, and provides a custom color configuration possibility
	public static String[] items = {
			MailResourceLoader.getString("dialog", "color", "blue"),
			MailResourceLoader.getString("dialog", "color", "gray"),
			MailResourceLoader.getString("dialog", "color", "green"),
			MailResourceLoader.getString("dialog", "color", "red"),
			MailResourceLoader.getString("dialog", "color", "yellow"),
			MailResourceLoader.getString("dialog", "color", "custom") };

	public static Color[] colors = { Color.blue, Color.gray, Color.green,
			Color.red, Color.yellow, Color.black };

	/**
	 * @param controller
	 * @param caption
	 */
	public ColorMessageMenu(FrameMediator controller) {
		super(controller, MailResourceLoader.getString("dialog", "color",
				"menu_color_message"));

		createSubMenu();

		((MailFrameMediator) controller).registerTableSelectionListener(this);
	}

	protected void createSubMenu() {
		// TODO: implement custom menuitem renderer
		JMenuItem item = new JMenuItem(MailResourceLoader.getString("dialog",
				"color", "none"));
		item.setActionCommand("NONE");
		item.addActionListener(this);
		add(item);
		addSeparator();

		for (int i = 0; i < items.length; i++) {
			item = new JMenuItem(items[i]);
			item.setActionCommand(items[i]);
			item.addActionListener(this);
			add(item);
		}
	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		// get current message list selection
		FolderCommandReference r = ((MailFrameMediator) getController())
				.getTableSelection();

		if (action.equals("NONE")) {
			// remove color
			//			add color selection to reference

			r.setColorValue(0);

			// pass command to scheduler
			MainInterface.processor.addOp(new ColorMessageCommand(r));
		} else {
			// which menuitem was selected?
			int result = -1;

			for (int i = 0; i < items.length; i++) {
				if (action.equals(items[i])) {
					result = i;
					break;
				}
			}

			// add color selection to reference

			r.setColorValue(colors[result].getRGB());

			// pass command to scheduler
			MainInterface.processor.addOp(new ColorMessageCommand(r));
		}
	}

	public void selectionChanged(SelectionChangedEvent e) {
		if (((TableSelectionChangedEvent) e).getUids().length > 0) {
			setEnabled(true);
		} else {
			setEnabled(false);
		}
	}
}
