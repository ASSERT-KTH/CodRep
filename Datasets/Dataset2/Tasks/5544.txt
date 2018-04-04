if (lockSize) {

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

import java.util.List;

import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.tree.TreePath;

import org.columba.core.config.HeaderItem;
import org.columba.core.config.TableItem;
import org.columba.core.gui.util.ImageLoader;
import org.columba.core.gui.util.treetable.TreeTable;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.table.model.HeaderTableModel;
import org.columba.mail.gui.table.model.MessageNode;
import org.columba.mail.gui.table.plugins.BasicHeaderRenderer;
import org.columba.mail.gui.table.plugins.BasicRenderer;
import org.columba.mail.gui.table.plugins.BooleanHeaderRenderer;
import org.columba.mail.gui.table.plugins.DefaultLabelRenderer;
import org.columba.mail.message.HeaderList;
import org.columba.mail.plugin.TableRendererPluginHandler;

/**
 * This widget is a mix between a JTable and a JTree
 * ( we need the JTree for the Threaded viewing of mailing lists )
 *
 * @version 0.9.1
 * @author fdietz
 */
public class TableView extends TreeTable {

	protected HeaderTableModel headerTableModel;

	private int selectedRow = 0;
	private int update = 0;

	//private ListSelectionModel listSelectionModel;

	private String column;

	private List tableModelPlugins;

	protected HeaderList headerList;

	public TableView(HeaderTableModel headerTableModel) {
		super();

		this.headerTableModel = headerTableModel;

		setModel(headerTableModel);

		//setSelectionModel(new HeaderTableSelectionModel());

		//setUI(new ColumbaBasicTableUI());

		getTree().setCellRenderer(new SubjectTreeRenderer());

		try {
			initRenderer();
			//headerTableModel.update();

		} catch (Exception ex) {
			ex.printStackTrace();
		}

		adjustColumn();
	}

	public void enableThreadedView(boolean b) {
		if (b) {
			//tree.setRootVisible(true);

			TableColumn tc = null;
			try {
				tc = getColumn("Subject");
				tc.setCellRenderer(null);

			} catch (Exception ex) {
				System.out.println(
					"headerTable->registerRenderer: " + ex.getMessage());
			}

			((HeaderTableModel) getModel()).enableThreadedView(true);

			//getTree().setCellRenderer()new SubjectTreeCellRenderer());

		} else {
			//tree.setRootVisible(false);

			 ((HeaderTableModel) getModel()).enableThreadedView(false);
			//setTreeCellRenderer(null);
			TableColumn tc = null;
			try {
				tc = getColumn("Subject");
				tc.setCellRenderer(new BasicRenderer("columba.subject"));

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

	protected void adjustColumn() {
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

			TableColumn tc = null;

			//ColumbaLogger.log.debug("name=" + name);

			try {
				tc = getColumn(name);
			} catch (Exception ex) {
				System.out.println(
					"headerTable->registerRenderer: " + ex.getMessage());
			}

			if (tc == null)
				continue;

			tc.setPreferredWidth(size);

			try {
				int index = getColumnModel().getColumnIndex(name);
				getColumnModel().moveColumn(index, position);
			} catch (Exception ex) {
				ex.printStackTrace();
			}
		}
	}

	/**
	 * initialize all renderers for the columns
	 * 
	 * @param b
	 * @throws Exception
	 */
	protected void initRenderer() throws Exception {
		TableItem tableItem =
			(TableItem) MailConfig.getMainFrameOptionsConfig().getTableItem();

		TableRendererPluginHandler handler = null;
		try {
			handler =
				(
					TableRendererPluginHandler) MainInterface
						.pluginManager
						.getHandler(
					"org.columba.mail.tablerenderer");

		} catch (PluginHandlerNotFoundException ex) {
			ex.printStackTrace();
		}

		for (int i = 0; i < tableItem.count(); i++) {
			HeaderItem v = tableItem.getHeaderItem(i);
			boolean enabled = v.getBoolean("enabled");

			if (enabled == false)
				continue;

			String name = v.get("name");
			int size = v.getInteger("size");
			int position = v.getInteger("position");

			DefaultLabelRenderer r = null;

			if (handler.exists(name))
				r = (DefaultLabelRenderer) handler.getPlugin(name, null);

			if (r == null) {
				// no specific renderer found
				// -> use default one

				r = new BasicRenderer(name);

				registerRenderer(
					name,
					r,
					new BasicHeaderRenderer(),
					size,
					false,
					position);

			} else {

				String image = handler.getAttribute(name, "icon");
				String fixed = handler.getAttribute(name, "size");
				boolean lockSize = false;
				if (fixed != null) {

					if (fixed.equals("fixed")) {
						size = 23;
						lockSize = true;
					}
				}

				if (lockSize == true) {

					registerRenderer(
						name,
						r,
						new BooleanHeaderRenderer(
							ImageLoader.getSmallImageIcon(image)),
						size,
						lockSize,
						position);
				} else {
					registerRenderer(
						name,
						r,
						new BasicHeaderRenderer(),
						size,
						lockSize,
						position);
				}
			}

		}

	}

	public void registerRenderer(
		String name,
		DefaultLabelRenderer cell,
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

	public MessageNode getSelectedNode() {

		MessageNode node =
			(MessageNode) getTree().getLastSelectedPathComponent();

		return node;

	}

	public MessageNode[] getSelectedNodes() {
		int[] rows = null;
		MessageNode[] nodes = null;

		rows = getSelectedRows();
		nodes = new MessageNode[rows.length];

		for (int i = 0; i < rows.length; i++) {
			TreePath treePath = getTree().getPathForRow(rows[i]);
			if ( treePath == null ) continue;
			
			nodes[i] = (MessageNode) treePath.getLastPathComponent();

		}
		return nodes;
	}

	public MessageNode getMessagNode(Object uid) {
		return headerTableModel.getMessageNode(uid);
	}

	/**
	 * Select first row and make it visible.
	 * 
	 * @return 	uid of selected row
	 */
	public Object selectFirstRow() {
		Object uid = null;

		//	if there are entries in the table
		if (getRowCount() > 0) {

			// changing the selection to the first row
			changeSelection(0, 0, true, false);

			// getting the node
			MessageNode selectedNode = (MessageNode) getValueAt(0, 0);

			// and getting the uid for this node
			uid = selectedNode.getUid();

			// scrolling to the first row
			scrollRectToVisible(getCellRect(0, 0, false));
			requestFocus();

			return uid;
		}

		return null;
	}

	/**
	 * Select last row and make it visible
	 * 
	 * @return 	uid of selected row
	 */
	public Object selectLastRow() {
		Object uid = null;

		//	if there are entries in the table
		if (getRowCount() > 0) {

			// changing the selection to the first row
			changeSelection(getRowCount() - 1, 0, true, false);

			// getting the node
			MessageNode selectedNode =
				(MessageNode) getValueAt(getRowCount() - 1, 0);

			// and getting the uid for this node
			uid = selectedNode.getUid();

			// scrolling to the first row
			scrollRectToVisible(getCellRect(getRowCount() - 1, 0,false));
			requestFocus();

			return uid;
		}

		return null;
	}

	/**
	 * Change the selection to the specified row
	 * 
	 * 
	 * @param row		row to selected
	 */
	public void selectRow(int row) {
		if (getRowCount() > 0) {
			if ( row<0 ) row = 0;
			if ( row >= getRowCount() ) row = getRowCount() -1;
			
			// changing the selection to the specified row
			changeSelection(row, 0, true, false);

			// getting the node
			MessageNode selectedNode =
				(MessageNode) getValueAt(row, 0);

			// and getting the uid for this node
			Object uid = selectedNode.getUid();

			// scrolling to the first row
			scrollRectToVisible(getCellRect(row, 0, false));
			requestFocus();

		}
	}

}