if (lastSelUids[0] == null)

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

import javax.swing.JComponent;
import javax.swing.JPopupMenu;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.TableColumn;
import javax.swing.tree.TreePath;

import org.columba.core.config.HeaderItem;
import org.columba.core.config.TableItem;
import org.columba.core.gui.focus.FocusOwner;
import org.columba.core.gui.util.treetable.Tree;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.core.util.SwingWorker;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.frame.ThreePaneMailFrameController;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.table.action.CopyAction;
import org.columba.mail.gui.table.action.CutAction;
import org.columba.mail.gui.table.action.DeleteAction;
import org.columba.mail.gui.table.action.PasteAction;
import org.columba.mail.gui.table.dnd.HeaderTableDnd;
import org.columba.mail.gui.table.dnd.MessageTransferHandler;
import org.columba.mail.gui.table.model.HeaderTableModel;
import org.columba.mail.gui.table.model.MessageNode;
import org.columba.mail.gui.table.model.TableModelChangedEvent;
import org.columba.mail.gui.table.model.TableModelFilter;
import org.columba.mail.gui.table.model.TableModelSorter;
import org.columba.mail.gui.table.model.TableModelThreadedView;
import org.columba.mail.gui.table.model.TableModelUpdateManager;
import org.columba.mail.gui.table.util.MarkAsReadTimer;
import org.columba.mail.message.HeaderList;

/**
 * This class shows the messageheaderlist
 *
 *
 * @version 0.9.1
 * @author Frederik
 */

public class TableController implements FocusOwner, ListSelectionListener {

	private TableView headerTable;
	private HeaderTableModel headerTableModel;

	private SwingWorker worker;
	private Folder folder;
	private HeaderList headerList;

	private FilterToolbar filterToolbar;

	private MessageNode[] messageNodes;

	private MessageNode node;
	private MessageNode oldNode;

	private Object[] selection;

	private HeaderTableMouseListener headerTableMouseListener;
	private HeaderTableDnd headerTableDnd;

	private FilterActionListener filterActionListener;

	private TableItem headerTableItem;

	private boolean folderChanged = false;

	private int counter = 1;

	protected TableView view;

	protected AbstractMailFrameController mailFrameController;

	protected Object[] newUidList;

	protected MarkAsReadTimer markAsReadTimer;

	protected TableMenu menu;

	protected TableModelFilter tableModelFilteredView;
	protected TableModelSorter tableModelSorter;
	protected TableModelThreadedView tableModelThreadedView;

	protected TableModelUpdateManager updateManager;

	public TableController(AbstractMailFrameController mailFrameController) {

		this.mailFrameController = mailFrameController;

		headerTableItem =
			(TableItem) MailConfig.getMainFrameOptionsConfig().getTableItem();

		headerTableModel = new HeaderTableModel(headerTableItem);

		tableModelFilteredView = new TableModelFilter(headerTableModel);

		tableModelThreadedView =
			new TableModelThreadedView(tableModelFilteredView);

		tableModelSorter = new TableModelSorter(tableModelThreadedView);

		updateManager = new TableModelUpdateManager(tableModelSorter);

		view = new TableView(headerTableModel);
		headerTableModel.setTree((Tree) view.getTree());

		headerTableMouseListener = new HeaderTableMouseListener(this);
		view.addMouseListener(headerTableMouseListener);

		filterActionListener = new FilterActionListener(this);
		// create a new markAsReadTimer
		markAsReadTimer = new MarkAsReadTimer(this);

		getView().setTransferHandler(new MessageTransferHandler(this));

		getView().setDragEnabled(false);

		getTableModelSorter().loadConfig(getView());

		// MouseListener sorts table when clicking on a column header
		new TableHeaderMouseListener(getView(), getTableModelSorter());

		// register at focus manager
		MainInterface.focusManager.registerComponent(this);

		// we need this for the focus manager
		getView().getSelectionModel().addListSelectionListener(this);

	}

	public TableView getView() {

		return view;
	}

	/**
	 * return FilterToolbar
	 */

	public FilterToolbar getFilterToolbar() {
		return filterToolbar;
	}

	/**
	 * return HeaderTableItem
	 */
	public TableItem getHeaderTableItem() {
		return headerTableItem;
	}

	/**
	 * save the column state:
	 *  - position
	 *  - size
	 *  - appearance
	 * of every column
	 */

	public void saveColumnConfig() {
		TableItem tableItem =
			(TableItem) MailConfig.getMainFrameOptionsConfig().getTableItem();

		if (MainInterface.DEBUG) {
			ColumbaLogger.log.info("save table column config");
		}

		getTableModelSorter().saveConfig();
		//.clone();
		//v.removeEnabledItem();

		for (int i = 0; i < tableItem.getChildCount(); i++) {
			HeaderItem v = tableItem.getHeaderItem(i);
			boolean enabled = v.getBoolean("enabled");
			if (enabled == false)
				continue;

			String c = v.get("name");
			ColumbaLogger.log.debug("name=" + c);

			TableColumn tc = getView().getColumn(c);

			v.set("size", tc.getWidth());
			if (MainInterface.DEBUG) {
				ColumbaLogger.log.debug("size" + tc.getWidth());
			}
			try {
				int index = getView().getColumnModel().getColumnIndex(c);
				v.set("position", index);
			} catch (IllegalArgumentException ex) {
				ex.printStackTrace();
			}

		}

	}

	/**
	 * return the Model which contains a HeaderList
	 */
	public HeaderTableModel getHeaderTableModel() {
		return headerTableModel;

	}

	/**
	 * return ActionListener for FilterToolbar
	 */
	public FilterActionListener getFilterActionListener() {
		return filterActionListener;
	}

	public void setSelected(Object[] uids) {
		MessageNode[] nodes = new MessageNode[uids.length];

		for (int i = 0; i < uids.length; i++) {
			nodes[i] = getHeaderTableModel().getMessageNode(uids[i]);
		}

		TreePath[] paths = new TreePath[nodes.length];

		for (int i = 0; i < nodes.length; i++) {
			paths[i] = new TreePath(nodes[i].getPath());

		}

		view.getTree().setSelectionPaths(paths);

		// FIXME
		//getTableSelectionManager().fireMessageSelectionEvent(null, uids);
	}

	/************************** actions ********************************/

	/**
	 * create the PopupMenu
	 */
	public void createPopupMenu() {
		menu = new TableMenu(mailFrameController);
	}

	/**
	 * return the PopupMenu for the table
	 */
	public JPopupMenu getPopupMenu() {

		return menu;
	}

	// method is called when folder data changed
	// the method updates the model

	public void tableChanged(TableModelChangedEvent event) throws Exception {
		if (MainInterface.DEBUG) {
			ColumbaLogger.log.info("event=" + event);
		}

		FolderTreeNode folder = event.getSrcFolder();

		if (folder == null) {
			if (event.getEventType() == TableModelChangedEvent.UPDATE)
				getHeaderTableModel().update();

			//fireTableChangedEvent(event);
			return;
		}

		FolderCommandReference[] r =
			(FolderCommandReference[]) mailFrameController
				.getSelectionManager()
				.getSelection("mail.table");
		Folder srcFolder = (Folder) r[0].getFolder();

		if (getMailFrameController() instanceof ThreePaneMailFrameController) {
			if (srcFolder != null)
				((ThreePaneMailFrameController) getMailFrameController())
					.treeController
					.getView()
					.makeVisible(srcFolder.getSelectionTreePath());
		}

		if (!folder.equals(srcFolder))
			return;
		//System.out.println("headertableviewer->folderChanged");

		switch (event.getEventType()) {
			case TableModelChangedEvent.SET :
				{

					updateManager.set(event.getHeaderList());

					break;
				}
			case TableModelChangedEvent.UPDATE :
				{

					updateManager.update();

					break;
				}

			case TableModelChangedEvent.REMOVE :
				{

					updateManager.remove(event.getUids());

					break;
				}
			case TableModelChangedEvent.MARK :
				{

					updateManager.modify(event.getUids());

					try {

						ColumbaLogger.log.debug("tableChangedEvent.Mark");
						// fixme: i don't know if this is the right point to do this
						// here we reselect the current marked message

						// getting the last selected uid
						Object[] lastSelUids = new Object[1];
						lastSelUids[0] = ((Folder) folder).getLastSelection();
						// selecting the message
						if (lastSelUids == null)
							break;

						setSelected(lastSelUids);
						int selRow = getView().getSelectedRow();
						// scroll to the position of the selection
						getView().scrollRectToVisible(
							getView().getCellRect(selRow, 0, false));
						getView().requestFocus();
					} catch (Exception ex) {
						ex.printStackTrace();
					}

					break;
				}
		}

		if (getMailFrameController() instanceof ThreePaneMailFrameController) {

			((ThreePaneMailFrameController) getMailFrameController())
				.folderInfoPanel
				.setFolder(srcFolder);
		}

		//fireTableChangedEvent(event);
	}

	/**
	 * Returns the mailFrameController.
	 * @return MailFrameController
	 */
	public AbstractMailFrameController getMailFrameController() {
		return mailFrameController;
	}

	/**
	 * Returns the markAsReadTimer.
	 * @return MarkAsReadTimer
	 */
	public MarkAsReadTimer getMarkAsReadTimer() {
		return markAsReadTimer;
	}

	/* (non-Javadoc)
		 * @see org.columba.mail.gui.frame.ViewHeaderListInterface#showHeaderList(org.columba.mail.folder.Folder, org.columba.mail.message.HeaderList)
		 */
	public void showHeaderList(Folder folder, HeaderList headerList)
		throws Exception {

		boolean enableThreadedView =
			folder.getFolderItem().getBoolean(
				"property",
				"enable_threaded_view",
				false);

		getView().enableThreadedView(enableThreadedView);

		getTableModelThreadedView().toggleView(enableThreadedView);

		TableModelChangedEvent ev =
			new TableModelChangedEvent(
				TableModelChangedEvent.SET,
				folder,
				headerList);

		tableChanged(ev);

		boolean ascending = getTableModelSorter().getSortingOrder();
		int row = getView().getTree().getRowCount();
		// row count == 0 --> empty table
		if ( row == 0 ) return;
		
		getView().clearSelection();
		// if the last selection for the current folder is null, then we show the
		// first/last message in the table and scroll to it.
		if (folder.getLastSelection() == null) {
			// changing the selection to the first/last row based on ascending state
			
			Object uid = null;
			if ( ascending == true )
				uid = view.selectFirstRow();
			else 
				uid = view.selectLastRow();
				
			// no messages in this folder
			if ( uid == null ) return;
			
			Object[] uids = new Object[1];
			uids[0] = uid;

			FolderCommandReference[] refNew = new FolderCommandReference[1];
			refNew[0] = new FolderCommandReference(folder, uids);

			// view the message under the new node
			MainInterface.processor.addOp(
				new ViewMessageCommand(mailFrameController, refNew));

		} else {
			// if a lastSelection for this folder is set
			
			// getting the last selected uid
			Object[] lastSelUids = new Object[1];
			lastSelUids[0] = folder.getLastSelection();
			
			// no messages in this folder
			if ( lastSelUids[0] == null ) return;
					 
			// selecting the message
			setSelected(lastSelUids);
			int selRow = getView().getSelectedRow();
			
			// scroll to the position of the selection
			getView().scrollRectToVisible(
				getView().getCellRect(selRow, 0, false));
			getView().requestFocus();
			
			// create command reference
			FolderCommandReference[] refNew = new FolderCommandReference[1];
			refNew[0] = new FolderCommandReference(folder, lastSelUids);
			
			// view the message under the new node
			MainInterface.processor.addOp(
				new ViewMessageCommand(mailFrameController, refNew));
		}

	}

	/************* implement getter/setter methods *********************/

	/**
	 * return the table model sorter
	 */
	public TableModelSorter getTableModelSorter() {
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
	public TableModelFilter getTableModelFilteredView() {
		return tableModelFilteredView;
	}

	/**
	 * @return
	 */
	public TableModelUpdateManager getUpdateManager() {
		return updateManager;
	}

	/********************* FocusOwner interface ************************/

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#copy()
	 */
	public void copy() {
		new CopyAction(getMailFrameController()).actionPerformed(null);

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#cut()
	 */
	public void cut() {
		new CutAction(getMailFrameController()).actionPerformed(null);

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#delete()
	 */
	public void delete() {
		new DeleteAction(getMailFrameController()).actionPerformed(null);

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#getComponent()
	 */
	public JComponent getComponent() {
		return getView();
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isCopyActionEnabled()
	 */
	public boolean isCopyActionEnabled() {
		if (getView().getSelectedNodes().length > 0)
			return true;

		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isCutActionEnabled()
	 */
	public boolean isCutActionEnabled() {
		if (getView().getSelectedNodes().length > 0)
			return true;

		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isDeleteActionEnabled()
	 */
	public boolean isDeleteActionEnabled() {
		if (getView().getSelectedNodes().length > 0)
			return true;

		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isPasteActionEnabled()
	 */
	public boolean isPasteActionEnabled() {
		if (MainInterface.clipboardManager.getMessageSelection() == null)
			return false;

		if (MainInterface.clipboardManager.getMessageSelection().length > 0)
			return true;

		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isRedoActionEnabled()
	 */
	public boolean isRedoActionEnabled() {
		// action not supported
		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isSelectAllActionEnabled()
	 */
	public boolean isSelectAllActionEnabled() {
		if (getView().getRowCount() > 0)
			return true;

		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#isUndoActionEnabled()
	 */
	public boolean isUndoActionEnabled() {
		// action not supported
		return false;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#paste()
	 */
	public void paste() {
		new PasteAction(getMailFrameController()).actionPerformed(null);

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#redo()
	 */
	public void redo() {
		// action not supported

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#selectAll()
	 */
	public void selectAll() {
		getView().selectAll();

	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.focus.FocusOwner#undo()
	 */
	public void undo() {
		// todo is not supported

	}

	/*************************** ListSelectionListener interface **************/

	/* (non-Javadoc)
	 * @see javax.swing.event.ListSelectionListener#valueChanged(javax.swing.event.ListSelectionEvent)
	 */
	public void valueChanged(ListSelectionEvent arg0) {
		MainInterface.focusManager.updateActions();

	}

}