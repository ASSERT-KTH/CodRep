setIcon(folder.getIcon());

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
package org.columba.addressbook.gui.tree.util;

import java.awt.Component;

import javax.swing.JTree;
import javax.swing.border.Border;
import javax.swing.tree.DefaultTreeCellRenderer;

import org.columba.addressbook.folder.AddressbookTreeNode;

@SuppressWarnings({"serial","serial"})
public class AddressbookTreeCellRenderer extends DefaultTreeCellRenderer {
	Border unselectedBorder = null;

	Border selectedBorder = null;

	boolean isBordered = true;

	boolean bool;

	public AddressbookTreeCellRenderer(boolean bool) {
		super();

		this.bool = bool;

	}

	public Component getTreeCellRendererComponent(JTree tree, Object value,
			boolean isSelected, boolean expanded, boolean leaf, int row,
			boolean hasFocus) {
		super.getTreeCellRendererComponent(tree, value, isSelected, expanded,
				leaf, row, hasFocus);

		AddressbookTreeNode folder = (AddressbookTreeNode) value;

		if (folder == null) {
			return this;
		}

		setText(folder.getName());
		setIcon(folder.getCollapsedIcon());

		return this;
	}
}