import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.gui.config.filter;

import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.table.TableColumn;

import org.columba.core.config.Config;
import org.columba.mail.filter.FilterList;
import org.columba.mail.gui.config.filter.util.FilterHeaderRenderer;
import org.columba.mail.gui.config.filter.util.StringFilterRenderer;
import org.columba.mail.util.MailResourceLoader;
import org.columba.main.MainInterface;

class FilterListTable extends JTable {
	private FilterListDataModel model;
	private Config config;
	private FilterList filterList;

	public FilterListTable(FilterList filterList, ConfigFrame frame) {
		super();
		this.filterList = filterList;
		config = MainInterface.config;

		setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

		model = new FilterListDataModel(filterList);
		//update();

		setModel(model);

		setShowGrid(false);
		setIntercellSpacing(new java.awt.Dimension(0, 0));

		TableColumn tc =
			getColumn(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"enabled_tableheader"));
		//tc.setCellRenderer( new BooleanFilterRenderer() );
		tc.setHeaderRenderer(
			new FilterHeaderRenderer(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"enabled_tableheader")));
		tc.setMaxWidth(80);
		tc.setMinWidth(80);

		tc =
			getColumn(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"description_tableheader"));
		tc.setCellRenderer(new StringFilterRenderer());
		tc.setHeaderRenderer(
			new FilterHeaderRenderer(
				MailResourceLoader.getString(
					"dialog",
					"filter",
					"description_tableheader")));

		sizeColumnsToFit(AUTO_RESIZE_NEXT_COLUMN);
	}

	public void update() {
		model.fireTableDataChanged();

	}

}