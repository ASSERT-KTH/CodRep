selected= Boolean.valueOf(checkbox.isSelected());



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

package org.columba.core.gui.checkablelist;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.DefaultCellEditor;
import javax.swing.JCheckBox;
import javax.swing.JTable;

/**
 * 
 *
 * @author fdietz
 */
public class CheckableListEditor
	extends DefaultCellEditor
	implements ActionListener {

	private JCheckBox checkbox;
	private Boolean selected;

	/**
	 * 
	 */
	public CheckableListEditor() {
		super(new JCheckBox());


		checkbox= new JCheckBox();
		checkbox.addActionListener(this);
		checkbox.setOpaque(true);
		checkbox.setBorder(BorderFactory.createEmptyBorder(0, 2, 0, 0));		
	}

	public Component getTableCellEditorComponent(
		JTable table,
		Object value,
		boolean isSelected,
		int row,
		int column) {

		if (isSelected) {
			checkbox.setForeground(table.getSelectionForeground());
			checkbox.setBackground(table.getSelectionBackground());
		} else {
			checkbox.setForeground(table.getForeground());
			checkbox.setBackground(table.getBackground());
		}

		checkbox.setSelected(((Boolean) value).booleanValue());

		return checkbox;
	}

	/**
	 * @see javax.swing.CellEditor#getCellEditorValue()
	 */
	public Object getCellEditorValue() {

		return selected;
	}

	public void actionPerformed(ActionEvent e) {

		//item.setSelected(checkbox.isSelected());
		selected= new Boolean(checkbox.isSelected());

		fireEditingStopped(); //Make the renderer reappear.

	}

	/**
	 * @see javax.swing.DefaultCellEditor#getComponent()
	 */
	public Component getComponent() {
		return checkbox;
	}

}