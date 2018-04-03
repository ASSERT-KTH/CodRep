import org.columba.mail.gui.table.model.MessageNode;

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

import java.awt.Component;
import java.awt.Font;

import javax.swing.JTable;
import javax.swing.JTree;
import javax.swing.SwingConstants;
import javax.swing.UIManager;

import org.columba.mail.gui.table.util.MessageNode;

public class HeaderTableSizeRenderer extends DefaultLabelRenderer {

	private JTree tree;
	private Font plainFont, boldFont;

	public HeaderTableSizeRenderer(JTree tree) {
		super(tree);
		this.tree = tree;

		setHorizontalAlignment(SwingConstants.RIGHT);

		//setOpaque(true); //MUST do this for background to show up.

		boldFont = UIManager.getFont("Tree.font");
		boldFont = boldFont.deriveFont(Font.BOLD);

		plainFont = UIManager.getFont("Tree.font");
	}

	public void updateUI() {
		super.updateUI();

		boldFont = UIManager.getFont("Tree.font");
		boldFont = boldFont.deriveFont(Font.BOLD);

		plainFont = UIManager.getFont("Tree.font");
	}

	public Component getTableCellRendererComponent(
		JTable table,
		Object value,
		boolean isSelected,
		boolean hasFocus,
		int row,
		int column) {

		

		if (value == null) {
			setText("");
			return this;
		}

		setText( ((MessageNode)value).getHeader().get("columba.size")  + "KB");

		return super.getTableCellRendererComponent(
		table,
		value,
		isSelected,
		hasFocus,
		row,
		column);
	}
}