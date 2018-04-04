fireTableDataChanged();

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
package org.columba.addressbook.gui.table;

import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;
import org.columba.addressbook.gui.table.util.HeaderColumnInterface;
import org.columba.addressbook.gui.table.util.TableModelFilteredView;
import org.columba.addressbook.gui.table.util.TableModelPlugin;
import org.columba.addressbook.gui.table.util.TableModelSorter;

import org.columba.core.logging.ColumbaLogger;

import java.util.Hashtable;
import java.util.List;
import java.util.Vector;

import javax.swing.table.AbstractTableModel;


public class AddressbookTableModel extends AbstractTableModel {
    private List columns;
    private Hashtable table;
    private HeaderItemList rows;
    private List tableModelPlugins;
    private HeaderItem selected;
    public boolean editable = false;

    public AddressbookTableModel() {
        super();

        rows = new HeaderItemList();

        columns = new Vector();

        tableModelPlugins = new Vector();
    }

    public void registerPlugin(TableModelPlugin plugin) {
        tableModelPlugins.add(plugin);
    }

    public int getSize() {
        return getHeaderList().count();
    }

    public void removeItem(Object[] items) {
        for (int i = 0; i < items.length; i++) {
            getHeaderList().remove((HeaderItem) items[i]);
        }

        // recreate whole tablemodel
        update();
    }

    public TableModelFilteredView getTableModelFilteredView() {
        return (TableModelFilteredView) tableModelPlugins.get(0);
    }

    public TableModelSorter getTableModelSorter() {
        return (TableModelSorter) tableModelPlugins.get(1);
    }

    public HeaderItemList getHeaderList() {
        return rows;
    }

    public void update() {
        fireTableDataChanged();
    }

    public HeaderItem getSelectedItem() {
        return selected;
    }

    public void setSelectedItem(HeaderItem selected) {
        this.selected = selected;
    }

    public void addItem(HeaderItem item) throws Exception {
        ColumbaLogger.log.info("item=" + item.toString());

        int count = 0;

        if (getHeaderList() != null) {
            count = getHeaderList().count();
        }

        if (count == 0) {
            rows = new HeaderItemList();

            // first message
            getHeaderList().add(item);

            //fireTableRowsInserted(0, 0);
            update();
        } else {
            setSelectedItem(item);

            boolean result = true;

            if (tableModelPlugins.size() != 0) {
                result = getTableModelFilteredView().manipulateModel(TableModelPlugin.NODES_INSERTED);
            }

            if (result == true) {
                if (tableModelPlugins.size() != 0) {
                    int index = getTableModelSorter().getInsertionSortIndex(item);

                    getHeaderList().insertElementAt(item, index);

                    fireTableRowsInserted(index, index);
                } else {
                    getHeaderList().add(item);

                    //fireTableRowsInserted(getRowCount() - 1, getRowCount() - 1);
                    update();
                }
            }
        }
    }

    public void addColumn(HeaderColumnInterface column) {
        String name = column.getName();

        columns.add(column);

        fireTableStructureChanged();
    }

    public HeaderColumnInterface getHeaderColumn(String name) {
        int index = getColumnNumber(name);

        return (HeaderColumnInterface) columns.get(index);
    }

    public void setHeaderList(HeaderItemList list) {
        if (list == null) {
            ColumbaLogger.log.info("list == null");
            rows = new HeaderItemList();

            fireTableDataChanged();

            return;
        }

        ColumbaLogger.log.info("list size=" + list.count());

        List clone = (Vector) ((Vector) list.getVector()).clone();
        rows = new HeaderItemList(clone);

        if (tableModelPlugins.size() != 0) {
            getTableModelSorter().manipulateModel(TableModelPlugin.STRUCTURE_CHANGE);
        }

        fireTableDataChanged();
    }

    public void setHeaderItem(int row, HeaderItem item) {
        rows.replace(row, item);

        //fireTableDataChanged();
    }

    public int getColumnCount() {
        return columns.size();
    }

    public int getRowCount() {
        if (rows == null) {
            return 0;
        } else {
            return rows.count();
        }
    }

    public String getColumnName(int col) {
        HeaderColumnInterface column = (HeaderColumnInterface) columns.get(col);
        String name = column.getName();

        return name;
    }

    public int getColumnNumber(String str) {
        for (int i = 0; i < getColumnCount(); i++) {
            if (str.equals(getColumnName(i))) {
                return i;
            }
        }

        return -1;
    }

    public HeaderItem getHeaderItem(int row) {
        if (rows == null) {
            return null;
        }

        HeaderItem item = rows.get(row);

        return item;
    }

    public Object getValueAt(int row, int col) {
        if (rows == null) {
            return null;
        }

        HeaderItem item = rows.get(row);

        HeaderColumnInterface column = (HeaderColumnInterface) columns.get(col);
        String name = column.getName();

        Object value = column.getValue(item);

        return value;
    }

    public Class getColumnClass(int c) {
        if (rows == null) {
            return null;
        }

        return getValueAt(0, c).getClass();
    }

    public boolean isCellEditable(int row, int col) {
        if (editable == false) {
            return false;
        }

        if ((col == 0) || (col == 1)) {
            return true;
        } else {
            return false;
        }
    }

    public void setValueAt(Object value, int row, int col) {
        if (col == 1) {
            HeaderItem item = rows.get(row);

            item.add("displayname", value);
            fireTableCellUpdated(row, col);
        } else if (col == 0) {
            HeaderItem item = rows.get(row);
            item.add("field", value);
            fireTableCellUpdated(row, col);
        }
    }
}