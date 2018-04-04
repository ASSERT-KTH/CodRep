new FolderTreeCellRenderer(true);

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

package org.columba.mail.gui.tree;

import javax.swing.JPopupMenu;
import javax.swing.JScrollPane;
import javax.swing.event.TreeExpansionEvent;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.event.TreeWillExpandListener;
import javax.swing.tree.ExpandVetoException;
import javax.swing.tree.TreePath;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.table.command.ViewHeaderListCommand;
import org.columba.mail.gui.tree.action.FolderTreeActionListener;
import org.columba.mail.gui.tree.action.FolderTreeMouseListener;
import org.columba.mail.gui.tree.command.FetchSubFolderListCommand;
import org.columba.mail.gui.tree.menu.FolderTreeMenu;
import org.columba.mail.gui.tree.util.FolderInfoPanel;
import org.columba.mail.gui.tree.util.FolderTreeCellRenderer;
import org.columba.core.main.MainInterface;

/**
 * this class shows the the folder hierarchy
 */

public class TreeController
implements TreeSelectionListener,
		TreeWillExpandListener //, TreeNodeChangeListener
{
	private TreeView folderTree;
	private boolean b = false;
	private TreePath treePath;
	private JPopupMenu popup;

	private FolderInfoPanel messageFolderInfoPanel;

	private FolderTreeActionListener actionListener;

	public JScrollPane scrollPane;

	private FolderTreeNode oldSelection;

	private FolderTreeMenu menu;

	private FolderTreeMouseListener mouseListener;

	protected TreeSelectionManager treeSelectionManager;

	private FolderTreeNode selectedFolder;

	private TreeModel model;

	private TreeView view;

	private MailFrameController mailFrameController;

	public TreeController(
		MailFrameController mailFrameController,
		TreeModel model) {

		this.model = model;
		this.mailFrameController = mailFrameController;

		view = new TreeView(model);

		actionListener = new FolderTreeActionListener(this);

		treeSelectionManager = new TreeSelectionManager();

		view.addTreeSelectionListener(this);

		//folderTreeActionListener = new FolderTreeActionListener(this);
		view.addTreeWillExpandListener(this);

		mouseListener = new FolderTreeMouseListener(this);

		view.addMouseListener(mouseListener);

		FolderTreeDnd dnd = new FolderTreeDnd(this);

		//scrollPane = new JScrollPane(getFolderTree().getTree());

		menu = new FolderTreeMenu(this);

		FolderTreeCellRenderer renderer =
			new FolderTreeCellRenderer(this, true);
		view.setCellRenderer(renderer);

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

	public void treeWillCollapse(TreeExpansionEvent e) {}

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

		getActionListener().changeActions();

		MainInterface.processor.addOp(
			new ViewHeaderListCommand(
				getMailFrameController(),
				treeSelectionManager.getSelection()));
	}

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

	public JPopupMenu getPopupMenu() {
		return menu.getPopupMenu();
	}

	public FolderTreeNode getSelected() {
		return selectedFolder;
	}

	public void selectFolder() {

		if ( view.getLastSelectedPathComponent() == null ) return;
		
		if (  !getSelected().equals(oldSelection))
		{
		MainInterface.processor.addOp(
			new ViewHeaderListCommand(
				getMailFrameController(),
				treeSelectionManager.getSelection()));
			oldSelection = getSelected();
		}
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
}