import org.columba.api.plugin.IExtensionInterface;

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
package org.columba.mail.gui.table.plugins;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;

import javax.swing.JTable;
import javax.swing.UIManager;
import javax.swing.table.DefaultTableCellRenderer;

import org.columba.core.plugin.IExtensionInterface;
import org.columba.mail.gui.table.model.MessageNode;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.IColumbaHeader;
import org.columba.ristretto.message.Flags;

/**
 * 
 * 
 * The is basic class every renderer should inherite
 * 
 * It is responsible for paint the background/foreground and borders and gives
 * us a central place for optimization
 * 
 * @author dietz
 */
public class DefaultLabelRenderer extends DefaultTableCellRenderer implements
		IExtensionInterface {
	// private Border unselectedBorder = null;
	//
	// private Border selectedBorder = null;
	//
	// private Color background;
	//
	// private Color foreground;

	private Font plainFont;

	private Font boldFont;

	private Font underlinedFont;

	// private boolean isBordered = true;

	/**
	 * Constructor for DefaultLabelRenderer.
	 */
	public DefaultLabelRenderer() {
		super();

		boldFont = UIManager.getFont("Tree.font");
		boldFont = boldFont.deriveFont(Font.BOLD);

		plainFont = UIManager.getFont("Tree.font");

		underlinedFont = UIManager.getFont("Tree.font");
		underlinedFont = underlinedFont.deriveFont(Font.ITALIC);

	}

	/**
	 * @see javax.swing.table.TableCellRenderer#getTableCellRendererComponent(javax.swing.JTable,
	 *      java.lang.Object, boolean, boolean, int, int)
	 */
	public Component getTableCellRendererComponent(JTable table, Object value,
			boolean isSelected, boolean hasFocus, int row, int column) {

		super.getTableCellRendererComponent(table, value, isSelected, hasFocus,
				row, column);

		setBorder(null);

		// TreePath path = tree.getPathForRow(row);
		MessageNode messageNode = (MessageNode) value;

		IColumbaHeader header = messageNode.getHeader();

		if (header == null) {
			System.out.println("header is null");

			return this;
		}

		Flags flags = ((ColumbaHeader) header).getFlags();

		if (flags != null) {
			// mark as bold if message is unseen
			if (!flags.getSeen()) {
				if (!getFont().equals(boldFont)) {
					setFont(boldFont);
				}
			} else if (messageNode.isHasRecentChildren()) {
				if (!getFont().equals(underlinedFont)) {
					setFont(underlinedFont);
				}
			} else if (!getFont().equals(plainFont)) {
				setFont(plainFont);
			}
		}

		Color msgColor = (Color) header.get("columba.color");

		if (msgColor != null) {
			if (msgColor.equals(Color.BLACK) == false)
				setForeground(msgColor);
		}

		return this;
	}

}