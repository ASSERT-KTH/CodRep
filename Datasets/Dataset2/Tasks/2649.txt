return item.get(columns[column]);

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
package org.columba.addressbook.gui.table.model;

import javax.swing.table.AbstractTableModel;

import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;

/**
 * Simple table model, using an extended TableModel interface.
 * 
 * @author fdietz
 */
public class AddressbookTableModel
	extends AbstractTableModel
	implements HeaderListTableModel {

	private String[] columns =
		{ "type", "displayname", "email;internet", "url" };

	private HeaderItemList rows;

	public AddressbookTableModel() {
		super();

		rows = new HeaderItemList();

	}

	public HeaderItemList getHeaderList() {
		return rows;
	}

	public void setHeaderList(HeaderItemList list) {
		this.rows = list;

		fireTableDataChanged();
	}

	public void update() {
		fireTableDataChanged();
	}

	/**
	 * @see javax.swing.table.TableModel#getColumnCount()
	 */
	public int getColumnCount() {
		return columns.length;
	}

	/**
	 * @see javax.swing.table.TableModel#getRowCount()
	 */
	public int getRowCount() {
		return rows.count();
	}

	/**
	 * @see javax.swing.table.TableModel#getValueAt(int, int)
	 */
	public Object getValueAt(int row, int column) {
		HeaderItem item = rows.get(row);

		return item;
	}

}