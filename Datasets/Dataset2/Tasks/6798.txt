return "";

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
package org.columba.mail.gui.config.pop3preprocessor;

import org.columba.core.xml.XmlElement;

import javax.swing.table.AbstractTableModel;


class FilterListTableModel extends AbstractTableModel {
    final String[] columnNames = { "Name", "Enabled", };
    private XmlElement filterList;

    public FilterListTableModel(XmlElement list) {
        super();
        this.filterList = list;
    }

    public int getColumnCount() {
        return columnNames.length;
    }

    public int getRowCount() {
        return filterList.count();
    }

    public String getColumnName(int col) {
        return columnNames[col];
    }

    public Object getValueAt(int row, int col) {
        XmlElement filter = filterList.getElement(row);

        // this shouldn't happen at any time
        if (filter == null) {
            return "";
        }

        if (col == 0) {
            // description
            String description = filter.getAttribute("name");

            if (description == null) {
                return new String();
            }

            return description;
        } else {
            // enabled/disabled
            return Boolean.valueOf(filter.getAttribute("enabled"));
        }
    }

    public Class getColumnClass(int c) {
        if (c == 0) {
            return String.class;
        } else {
            return Boolean.class;
        }
    }

    public boolean isCellEditable(int row, int col) {
        if (col == 1) {
            return true;
        } else {
            return false;
        }
    }

    public void setValueAt(Object value, int row, int col) {
        XmlElement filter = filterList.getElement(row);
        filter.addAttribute("enabled", (String) value);
    }
}