view = new TreeView(mailFrameController, model);

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
package org.columba.mail.gui.tree;

import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.event.TreeExpansionEvent;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.event.TreeWillExpandListener;
import javax.swing.tree.ExpandVetoException;
import javax.swing.tree.TreePath;

import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.command.ViewHeaderListCommand;
import org.columba.mail.gui.tree.action.FolderTreeActionListener;
import org.columba.mail.gui.tree.command.FetchSubFolderListCommand;
import org.columba.mail.gui.tree.selection.TreeSelectionHandler;
import org.columba.mail.gui.tree.selection.TreeSelectionManager;
import org.columba.mail.gui.tree.util.FolderInfoPanel;
import org.columba.mail.gui.tree.util.FolderTreeCellRenderer;

/**
 * this class shows the the folder hierarchy
 */

public class TreeController implements TreeSelectionListener,
TreeWillExpandListener //, TreeNodeChangeListener
{
	private TreeView folderTree;
	private boolean b = false;
	private TreePath treePath;
	//private JPopupMenu popup;

	private FolderInfoPanel messageFolderInfoPanel;

	private FolderTreeActionListener actionListener;

	public JScrollPane scrollPane;

	private FolderTreeNode oldSelection;

	//private FolderTreeMenu menu;

	private FolderTreeMouseListener mouseListener;

	protected TreeSelectionManager treeSelectionManager;

	private FolderTreeNode selectedFolder;

	private TreeModel model;

	private TreeView view;

	private MailFrameController mailFrameController;

	protected TreeMenu menu;

	public TreeController(
		MailFrameController mailFrameController,
		TreeModel model) {

		this.model = model;
		this.mailFrameController = mailFrameController;

		view = new TreeView(model);

		actionListener = new FolderTreeActionListener(this);

		treeSelectionManager = new TreeSelectionManager();
		
		mailFrameController.getSelectionManager().addSelectionHandler(new TreeSelectionHandler(view));
		//view.addTreeSelectionListener(this);

		//folderTreeActionListener = new FolderTreeActionListener(this);
		view.addTreeWillExpandListener(this);

		mouseListener = new FolderTreeMouseListener(this);

		view.addMouseListener(mouseListener);

		// FIXME
		
		//FolderTreeDnd dnd = new FolderTreeDnd(this);

		//scrollPane = new JScrollPane(getFolderTree().getTree());

		//menu = new FolderTreeMenu(this);
		menu = new TreeMenu(mailFrameController);

		FolderTreeCellRenderer renderer = new FolderTreeCellRenderer(true);
		view.setCellRenderer(renderer);
		
		getView().addTreeSelectionListener(this);

		//MainInterface.focusManager.registerComponent( new TreeFocusOwner(this) );
	}

	public void treeWillExpand(TreeExpansionEvent e)
		throws ExpandVetoException {

		System.out.println("treeWillExpand=" + e.getPath().toString());

		FolderTreeNode treeNode =
			(FolderTreeNode) e.getPath().getLastPathComponent();

		if (treeNode == null)
			return;

		FolderCommandReference[] cr = new FolderCommandReference[1];
		cr[0] = new FolderCommandReference(treeNode);

		MainInterface.processor.addOp(new FetchSubFolderListCommand(cr));
	}

	public void treeWillCollapse(TreeExpansionEvent e) {
	}

	public TreeModel getModel() {
		return model;
	}

	public TreeView getView() {
		return view;
	}

	public FolderTreeActionListener getActionListener() {
		return actionListener;
	}

	public void setSelected(Folder folder) {
		view.clearSelection();

		TreePath path = folder.getSelectionTreePath();

		view.requestFocus();
		view.setLeadSelectionPath(path);
		view.setAnchorSelectionPath(path);
		view.expandPath(path);

		//view.setSelectionRow( view.getRowForPath(path) );
		treeSelectionManager.fireFolderSelectionEvent(selectedFolder, folder);

		this.selectedFolder = folder;

		//selectedFolder = (FolderTreeNode) view.getLastSelectedPathComponent();

		//getActionListener().changeActions();

		MainInterface.processor.addOp(
			new ViewHeaderListCommand(
				getMailFrameController(),
				treeSelectionManager.getSelection()));
	}

	/*
	// this method is called when the user selects another folder
	
	public void valueChanged(TreeSelectionEvent e) {
	
		// BUGFIX but don't know why that bug occurs 
		if (view.getLastSelectedPathComponent() == null)
			return;
	
		treeSelectionManager.fireFolderSelectionEvent(
			selectedFolder,
			(FolderTreeNode) view.getLastSelectedPathComponent());
	
		selectedFolder = (FolderTreeNode) view.getLastSelectedPathComponent();
	
		getActionListener().changeActions();
	
		//if (selectedFolder == null) return;
	}
	*/
	public JPopupMenu getPopupMenu() {
		return menu;
	}

	public FolderTreeNode getSelected() {
		return selectedFolder;
	}

	public void selectFolder() {
		/*
				if ( view.getLastSelectedPathComponent() == null ) return;
				
				if (  !getSelected().equals(oldSelection))
				{
				MainInterface.processor.addOp(
					new ViewHeaderListCommand(
						getMailFrameController(),
						treeSelectionManager.getSelection()));
					oldSelection = getSelected();
				}
		*/
	}

	/**
	 * Returns the treeSelectionManager.
	 * @return TreeSelectionManager
	 */
	public TreeSelectionManager getTreeSelectionManager() {
		return treeSelectionManager;
	}

	/**
	 * Returns the mailFrameController.
	 * @return MailFrameController
	 */
	public MailFrameController getMailFrameController() {
		return mailFrameController;
	}

	/* (non-Javadoc)
	 * @see javax.swing.event.TreeSelectionListener#valueChanged(javax.swing.event.TreeSelectionEvent)
	 */
	public void valueChanged(TreeSelectionEvent ev) {
		TreePath path = ev.getPath();
		
		if ( path != null )
		{
			FolderTreeNode node = (FolderTreeNode) path.getLastPathComponent();
			
			getTreeSelectionManager().fireFolderSelectionEvent(null, node);	
		}
	
	}
	

}