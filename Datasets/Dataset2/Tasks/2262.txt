import org.columba.core.filter.FilterList;

///The contents of this file are subject to the Mozilla Public License Version 1.1
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
package org.columba.mail.gui.config.filter;

import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableColumn;

import org.columba.mail.filter.FilterList;


class FilterListTable extends JTable {
    public FilterListTable(FilterList filterList, ConfigFrame frame) {
        super(new FilterListDataModel(filterList));
        setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        setShowGrid(false);
        setIntercellSpacing(new java.awt.Dimension(0, 0));

        TableColumn tc = getColumnModel().getColumn(1);
        tc.setMaxWidth(80);
        tc.setMinWidth(80);

        DefaultTableCellRenderer renderer = (DefaultTableCellRenderer) tableHeader.getDefaultRenderer();
        renderer.setHorizontalAlignment(DefaultTableCellRenderer.LEFT);
    }

    public void update() {
        ((FilterListDataModel) getModel()).fireTableDataChanged();
    }

    /**
     * The specified row has been updated and should be repainted.
     * @param row the row that has been updated.
     */
    public void update(int row) {
        ((FilterListDataModel) getModel()).fireTableRowsUpdated(row, row);
    }

    /**
     * Sets the specified row indicies to be selected in the table.
     * Note that this clears all previous selections.
     * @param selectedRows an array of integers containing the indices of
     * all rows that are to be selected.
     */
    public void setRowSelection(int[] selectedRows) {
        ListSelectionModel model = getSelectionModel();
        model.setValueIsAdjusting(true);
        model.clearSelection();

        for (int i = 0; i < selectedRows.length; i++) {
            model.addSelectionInterval(selectedRows[i], selectedRows[i]);
        }

        model.setValueIsAdjusting(false);
    }
}