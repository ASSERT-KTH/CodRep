return Boolean.valueOf(item.isSelected());

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
import java.util.Vector;

import javax.swing.table.AbstractTableModel;

/**
 * 
 *
 * @author fdietz
 */
public class CheckableItemListTableModel extends AbstractTableModel {
	private Vector data;

	private final static String[] columns= { "Boolean", "String" };

	/**
	 * 
	 */
	public CheckableItemListTableModel() {
		super();

		data= new Vector();

	}

	/**
	 * @see javax.swing.table.TableModel#getColumnCount()
	 */
	public int getColumnCount() {
		// two column
		return columns.length;
	}

	/**
	 * @see javax.swing.table.TableModel#getRowCount()
	 */
	public int getRowCount() {
		return data.size();
	}

	/**
	 * @see javax.swing.table.TableModel#getValueAt(int, int)
	 */
	public Object getValueAt(int row, int column) {

		CheckableItem item= (CheckableItem) data.get(row);

		if (column == 0)
			return new Boolean(item.isSelected());

		else
			return item.toString();

	}

	public void addElement(CheckableItem item) {
		data.add(item);
	}

	public void setElement(int index, CheckableItem item) {
		data.set(index, item);
	}

	/**
	 * @see javax.swing.table.TableModel#getColumnClass(int)
	 */
	public Class getColumnClass(int column) {
		return getValueAt(0, column).getClass();
	}

	/**
	 * @see javax.swing.table.TableModel#isCellEditable(int, int)
	 */
	public boolean isCellEditable(int row, int column) {
		if (column == 0)
			return true;

		else
			return false;
	}

	/**
	 * @see javax.swing.table.TableModel#setValueAt(java.lang.Object, int, int)
	 */
	public void setValueAt(Object value, int row, int column) {

		CheckableItem item= (CheckableItem) data.get(row);

		if (column == 0)
			item.setSelected(((Boolean) value).booleanValue());

	}

	/**
	 * @see javax.swing.table.TableModel#getColumnName(int)
	 */
	public String getColumnName(int column) {
		return columns[column];
	}
	
	public int count() {
		return data.size();
	}

	public CheckableItem getElement(int index) {
		return (CheckableItem) data.get(index);
	}
	
	public void updateRow(CheckableItem item) {
		int index = data.indexOf(item);
		fireTableRowsUpdated(index, index);
	}
}