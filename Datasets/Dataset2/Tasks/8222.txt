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

import javax.swing.ImageIcon;
import javax.swing.JTable;
import javax.swing.JTree;
import javax.swing.SwingConstants;

import org.columba.mail.gui.table.util.MessageNode;

public class BooleanRenderer extends DefaultLabelRenderer {

	boolean bool;
	//String str;
	ImageIcon image;
	String key;
	
	public BooleanRenderer(JTree tree, boolean bool, ImageIcon image, String key) {
		super(tree);
	
		this.bool = bool;
		//this.str = str;
		this.image = image;
		this.key = key;
		setHorizontalAlignment(SwingConstants.CENTER);
		//setOpaque(true); //MUST do this for background to show up.
	}

	public Component getTableCellRendererComponent(
		JTable table,
		Object value,
		boolean isSelected,
		boolean hasFocus,
		int row,
		int column) {

		super.getTableCellRendererComponent(
			table,
			value,
			isSelected,
			hasFocus,
			row,
			column);

		if (value == null) {
			setIcon(null);
			return this;
		}

		if (value instanceof String)
			return this;

		
		if (bool == true) {
			Boolean b = (Boolean) ( (MessageNode)value).getHeader().get(key);
			if (b == null)
				return this;

			if (b.equals(Boolean.TRUE)) {
				setIcon(image);
			} else {
				setIcon(null);
			}
		} else {
			Boolean b = (Boolean) value;
			if (b == null)
				return this;

			if (b.equals(Boolean.FALSE)) {
				setIcon(image);
			} else {
				setIcon(null);
			}
		}
		
		return this;
	}
}