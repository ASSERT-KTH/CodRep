model.fireTableRowsUpdated(0,model.getRowCount());

/*
 * JCheckBoxList.java - A list, each item can be checked or unchecked
 * Copyright (C) 2000, 2001 Slava Pestov
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package org.gjt.sp.jedit.gui;

import javax.swing.table.*;
import javax.swing.*;
import java.util.Vector;

/**
 * @since jEdit 3.2pre9
 */
public class JCheckBoxList extends JTable
{
	/**
	 * Creates a checkbox list with the given list of objects. The elements
	 * of this array can either be Entry instances, or other objects (if the
	 * latter, they will default to being unchecked).
	 */
	public JCheckBoxList(Object[] items)
	{
		setModel(items);
	}

	/**
	 * Creates a checkbox list with the given list of objects. The elements
	 * of this vector can either be Entry instances, or other objects (if the
	 * latter, they will default to being unchecked).
	 */
	public JCheckBoxList(Vector items)
	{
		setModel(items);
	}

	/**
	 * Sets the model to the given list of objects. The elements of this
	 * array can either be Entry instances, or other objects (if the
	 * latter, they will default to being unchecked).
	 */
	public void setModel(Object[] items)
	{
		setModel(new CheckBoxListModel(items));
		init();
	}

	/**
	 * Sets the model to the given list of objects. The elements of this
	 * vector can either be Entry instances, or other objects (if the
	 * latter, they will default to being unchecked).
	 */
	public void setModel(Vector items)
	{
		setModel(new CheckBoxListModel(items));
		init();
	}

	public Object[] getCheckedValues()
	{
		Vector values = new Vector();
		CheckBoxListModel model = (CheckBoxListModel)getModel();
		for(int i = 0; i < model.items.size(); i++)
		{
			Entry entry = (Entry)model.items.elementAt(i);
			if(entry.checked)
				values.addElement(entry.value);
		}

		Object[] retVal = new Object[values.size()];
		values.copyInto(retVal);
		return retVal;
	}

	public void selectAll()
	{
		CheckBoxListModel model = (CheckBoxListModel)getModel();
		for(int i = 0; i < model.items.size(); i++)
		{
			Entry entry = (Entry)model.items.elementAt(i);
			entry.checked = true;
		}

		model.fireTableStructureChanged();
	}

	public Entry[] getValues()
	{
		CheckBoxListModel model = (CheckBoxListModel)getModel();
		Entry[] retVal = new Entry[model.items.size()];
		model.items.copyInto(retVal);
		return retVal;
	}

	public Object getSelectedValue()
	{
		int row = getSelectedRow();
		if(row == -1)
			return null;
		else
			return getModel().getValueAt(row,1);
	}

	// private members
	private void init()
	{
		getSelectionModel().setSelectionMode(ListSelectionModel
			.SINGLE_SELECTION);
		setShowGrid(false);
		setAutoResizeMode(JTable.AUTO_RESIZE_LAST_COLUMN);
		TableColumn column = getColumnModel().getColumn(0);
		int checkBoxWidth = new JCheckBox().getPreferredSize().width;
		column.setPreferredWidth(checkBoxWidth);
		column.setMinWidth(checkBoxWidth);
		column.setWidth(checkBoxWidth);
		column.setMaxWidth(checkBoxWidth);
		column.setResizable(false);
	}

	public static class Entry
	{
		boolean checked;
		Object value;

		public Entry(boolean checked, Object value)
		{
			this.checked = checked;
			this.value = value;
		}

		public boolean isChecked()
		{
			return checked;
		}

		public Object getValue()
		{
			return value;
		}
	}
}

class CheckBoxListModel extends AbstractTableModel
{
	Vector items;

	CheckBoxListModel(Vector _items)
	{
		items = new Vector(_items.size());
		for(int i = 0; i < _items.size(); i++)
		{
			items.addElement(createEntry(_items.elementAt(i)));
		}
	}

	CheckBoxListModel(Object[] _items)
	{
		items = new Vector(_items.length);
		for(int i = 0; i < _items.length; i++)
		{
			items.addElement(createEntry(_items[i]));
		}
	}

	private JCheckBoxList.Entry createEntry(Object obj)
	{
		if(obj instanceof JCheckBoxList.Entry)
			return (JCheckBoxList.Entry)obj;
		else
			return new JCheckBoxList.Entry(false,obj);
	}

	public int getRowCount()
	{
		return items.size();
	}

	public int getColumnCount()
	{
		return 2;
	}

	public String getColumnName(int col)
	{
		return null;
	}

	public Object getValueAt(int row, int col)
	{
		JCheckBoxList.Entry entry = (JCheckBoxList.Entry)items.elementAt(row);
		switch(col)
		{
		case 0:
			return new Boolean(entry.checked);
		case 1:
			return entry.value;
		default:
			throw new InternalError();
		}
	}

	public Class getColumnClass(int col)
	{
		switch(col)
		{
		case 0:
			return Boolean.class;
		case 1:
			return String.class;
		default:
			throw new InternalError();
		}
	}

	public boolean isCellEditable(int row, int col)
	{
		return col == 0;
	}

	public void setValueAt(Object value, int row, int col)
	{
		if(col == 0)
		{
			((JCheckBoxList.Entry)items.elementAt(row)).checked =
				(value.equals(Boolean.TRUE));
			fireTableRowsUpdated(row,row);
		}
	}
}