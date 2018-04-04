setTreeCellRenderer(new SubjectTreeCellRenderer());

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
package org.columba.mail.gui.table;

import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.MissingResourceException;
import java.util.Vector;

import javax.swing.JTable;
import javax.swing.event.MouseInputListener;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.tree.TreePath;

import org.columba.core.config.HeaderItem;
import org.columba.core.config.TableItem;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.treetable.JTreeTable;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.table.plugins.BooleanHeaderRenderer;
import org.columba.mail.gui.table.plugins.BooleanRenderer;
import org.columba.mail.gui.table.plugins.CommonHeaderRenderer;
import org.columba.mail.gui.table.plugins.DateHeaderRenderer;
import org.columba.mail.gui.table.plugins.FlaggedRenderer;
import org.columba.mail.gui.table.plugins.HeaderTableCommonRenderer;
import org.columba.mail.gui.table.plugins.HeaderTableDateRenderer;
import org.columba.mail.gui.table.plugins.HeaderTableSizeRenderer;
import org.columba.mail.gui.table.plugins.PriorityRenderer;
import org.columba.mail.gui.table.plugins.StatusRenderer;
import org.columba.mail.gui.table.util.MessageNode;
import org.columba.mail.gui.table.util.SubjectTreeCellRenderer;
import org.columba.mail.gui.table.util.TableModelFilteredView;
import org.columba.mail.gui.table.util.TableModelThreadedView;
import org.columba.mail.message.HeaderList;
import org.columba.mail.util.MailResourceLoader;

/**
 * This widget is a mix between a JTable and a JTree
 * ( we need the JTree for the Threaded viewing of mailing lists )
 *
 * @version 0.9.1
 * @author Frederik
 */
public class TableView extends JTreeTable {

	protected HeaderTableModel headerTableModel;

	private int selectedRow = 0;
	private int update = 0;

	//private ListSelectionModel listSelectionModel;

	private String column;

	//private JTreeTable table;

	private Vector tableModelPlugins;

	protected TableModelFilteredView tableModelFilteredView;
	protected HeaderTableModelSorter tableModelSorter;
	protected TableModelThreadedView tableModelThreadedView;

	protected HeaderList headerList;

	public TableView(HeaderTableModel headerTableModel) {
		super(headerTableModel);

		this.headerTableModel = headerTableModel;

		tableModelFilteredView = new TableModelFilteredView(headerTableModel);

		tableModelSorter = new HeaderTableModelSorter(headerTableModel);
		tableModelSorter.setWindowItem(
			MailConfig.getMainFrameOptionsConfig().getWindowItem());

		tableModelThreadedView = new TableModelThreadedView(headerTableModel);

		//table = new JTreeTable( headerTableModel );

		//setUI(new ColumbaBasicTableUI());

		headerTableModel.registerPlugin(tableModelFilteredView);
		headerTableModel.registerPlugin(tableModelThreadedView);
		headerTableModel.registerPlugin(tableModelSorter);

		try {
			initRenderer(false);
			//headerTableModel.update();

		} catch (Exception ex) {
			ex.printStackTrace();
		}

		addMouseListenerToHeaderInTable();
		
		//setSelectionModel(new HeaderTableSelectionModel());

	}

	protected void addMouseListenerToHeaderInTable() {

		final JTable tableView = this;

		tableView.setColumnSelectionAllowed(false);

		MouseAdapter listMouseListener = new MouseAdapter() {
			public void mouseClicked(MouseEvent e) {
				TableColumnModel columnModel = tableView.getColumnModel();
				int viewColumn = columnModel.getColumnIndexAtX(e.getX());
				int column = tableView.convertColumnIndexToModel(viewColumn);

				if (e.getClickCount() == 1 && column != -1) {
					getTableModelSorter().setSortingColumn(column);
					headerTableModel.update();

				}
			}
		};

		JTableHeader th = tableView.getTableHeader();
		th.addMouseListener(listMouseListener);

	}

	public void enableThreadedView(boolean b) {

		if (b == true) {
			//tree.setRootVisible(true);

			TableColumn tc = null;
			try {
				tc = getColumn("Subject");
				tc.setCellRenderer(null);

			} catch (Exception ex) {
				System.out.println(
					"headerTable->registerRenderer: " + ex.getMessage());
			}

			setTreeCellRenderer(new SubjectTreeCellRenderer(getTree()));

		} else {
			//tree.setRootVisible(false);

			setTreeCellRenderer(null);
			TableColumn tc = null;
			try {
				tc = getColumn("Subject");
				tc.setCellRenderer(
					new HeaderTableCommonRenderer(getTree(), "Subject"));

			} catch (Exception ex) {
				System.out.println(
					"headerTable->registerRenderer: " + ex.getMessage());
			}
		}

	}

	/**
	 * sets the header, which is going to be viewed
	 *
	 * @param f a <code>Folder</code>
	 * @see Folder
	 */

	protected void initRenderer(boolean b) throws Exception {

		TableItem tableItem =
			(TableItem) MailConfig.getMainFrameOptionsConfig().getTableItem();

		//.clone();
		//v.removeEnabledItem();

		for (int i = 0; i < tableItem.count(); i++) {
			HeaderItem v = tableItem.getHeaderItem(i);
			boolean enabled = v.getBoolean("enabled");

			if (enabled == false)
				continue;

			String name = v.get("name");
			int size = v.getInteger("size");
			int position = v.getInteger("position");

			if (name.equalsIgnoreCase("size")) {
				registerRenderer(
					"Size",
					new HeaderTableSizeRenderer(getTree()),
					new CommonHeaderRenderer(
						name,
						MailResourceLoader.getString("header", "size"),
						getTableModelSorter()),
					size,
					false,
					position);
			} else if (name.equalsIgnoreCase("Status")) {

				registerRenderer(
					"Status",
					new StatusRenderer(getTree()),
					new BooleanHeaderRenderer(
						true,
						name,
						getTableModelSorter()),
					23,
					true,
					position);
			} else if (name.equalsIgnoreCase("Flagged")) {
				registerRenderer(
					"Flagged",
					new FlaggedRenderer(getTree()),
					new BooleanHeaderRenderer(
						true,
						name,
						getTableModelSorter()),
					23,
					true,
					position);
			} else if (name.equalsIgnoreCase("Attachment")) {
				registerRenderer(
					"Attachment",
					new BooleanRenderer(
						getTree(),
						true,
						ImageLoader.getSmallImageIcon("attachment.png"),
						"columba.attachment"),
					new BooleanHeaderRenderer(
						true,
						name,
						getTableModelSorter()),
					23,
					true,
					position);
			} else if (name.equalsIgnoreCase("Date")) {
				registerRenderer(
					"Date",
					new HeaderTableDateRenderer(getTree(), true),
					new DateHeaderRenderer(
						name,
						MailResourceLoader.getString("header", "date"),
						getTableModelSorter()),
					size,
					false,
					position);

			} else if (name.equalsIgnoreCase("Priority")) {
				registerRenderer(
					"Priority",
					new PriorityRenderer(getTree(), true),
					new BooleanHeaderRenderer(
						true,
						name,
						getTableModelSorter()),
					23,
					true,
					position);

			} else if (name.equalsIgnoreCase("Subject")) {

				registerRenderer(
					"Subject",
					new HeaderTableCommonRenderer(getTree(), "Subject"),
					new CommonHeaderRenderer(
						name,
						MailResourceLoader.getString("header", "subject"),
						getTableModelSorter()),
					size,
					false,
					position);
			} else {
				String str = new String();
				try {
					str =
						MailResourceLoader.getString(
							"header",
							name.toLowerCase());

				} catch (MissingResourceException ex) {
					System.out.println(ex.getMessage());

				}

				if (str.length() == 0)
					registerRenderer(
						name,
						new HeaderTableCommonRenderer(getTree(), name),
						new CommonHeaderRenderer(
							name,
							name,
							getTableModelSorter()),
						size,
						false,
						position);

				else
					registerRenderer(
						name,
						new HeaderTableCommonRenderer(getTree(), str),
						new CommonHeaderRenderer(
							name,
							str,
							getTableModelSorter()),
						size,
						false,
						position);

			}
		}

	}

	public void registerRenderer(
		String name,
		TableCellRenderer cell,
		TableCellRenderer header,
		int size,
		boolean lockSize,
		int position) {
		TableColumn tc = null;

		//ColumbaLogger.log.debug("name=" + name);

		try {
			tc = getColumn(name);
		} catch (Exception ex) {
			System.out.println(
				"headerTable->registerRenderer: " + ex.getMessage());
		}

		if (tc == null)
			return;

		if (cell != null)
			tc.setCellRenderer(cell);

		if (header != null)
			tc.setHeaderRenderer(header);

		if (lockSize) {
			tc.setMaxWidth(size);
			tc.setMinWidth(size);
		} else {
			//ColumbaLogger.log.debug("setting size =" + size);

			tc.setPreferredWidth(size);
		}

		try {
			int index = getColumnModel().getColumnIndex(name);
			getColumnModel().moveColumn(index, position);
		} catch (Exception ex) {
			ex.printStackTrace();
		}
	}

	public void registerRenderer(
		String name,
		TableCellRenderer cell,
		TableCellRenderer header,
		int size,
		boolean lockSize) {
		TableColumn tc = null;

		try {
			tc = getColumn(name);
		} catch (Exception ex) {
			System.out.println(
				"headerTable->registerRenderer: " + ex.getMessage());
		}

		if (tc == null)
			return;

		if (cell != null)
			tc.setCellRenderer(cell);

		if (header != null)
			tc.setHeaderRenderer(header);

		if (lockSize) {
			tc.setMaxWidth(size);
			tc.setMinWidth(size);
		} else
			tc.setPreferredWidth(size);

	}

	/**
	 * return the table model sorter
	 */
	public HeaderTableModelSorter getTableModelSorter() {
		return tableModelSorter;
	}

	/**
	 * return the threaded view model
	 */
	public TableModelThreadedView getTableModelThreadedView() {
		return tableModelThreadedView;
	}

	/**
	 * return the filtered view model
	 */
	public TableModelFilteredView getTableModelFilteredView() {
		return tableModelFilteredView;
	}

	public MessageNode getSelectedNode() {

		MessageNode node =
			(MessageNode) getTree().getLastSelectedPathComponent();

		return node;

	}

	/*
	public int getSelectedRowCount()
	{
	    int[] rows = table.getSelectedRows();
	
		if ( rows == null ) return 0;
		
	    return rows.length;
	}
	*/
	public MessageNode[] getSelectedNodes() {

		int[] rows = null;
		MessageNode[] nodes = null;

		rows = getSelectedRows();
		nodes = new MessageNode[rows.length];

		for (int i = 0; i < rows.length; i++) {
			TreePath treePath = getTree().getPathForRow(rows[i]);
			nodes[i] = (MessageNode) treePath.getLastPathComponent();

		}

		return nodes;

	}

	public MessageNode getMessagNode(Object uid) {
		return headerTableModel.getMessageNode(uid);
	}

	protected MouseInputListener createMouseInputListener() {
		return null;
	}

}
