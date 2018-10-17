treeController.getTreeSelectionManager().getFolder().addFolder( name, "VirtualFolder" );

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

package org.columba.mail.gui.tree.action;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.JOptionPane;
import javax.swing.KeyStroke;

import org.columba.core.gui.util.ImageLoader;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.command.ApplyFilterCommand;
import org.columba.mail.folder.command.ExpungeFolderCommand;
import org.columba.mail.folder.command.RemoveFolderCommand;
import org.columba.mail.folder.command.RenameFolderCommand;
import org.columba.mail.folder.virtual.VirtualFolder;
import org.columba.mail.gui.action.BasicAction;
import org.columba.mail.gui.tree.TreeController;
import org.columba.mail.gui.tree.command.CreateSubFolderCommand;
import org.columba.mail.gui.tree.util.EditFolderDialog;
import org.columba.mail.util.MailResourceLoader;
import org.columba.core.main.MainInterface;

public class FolderTreeActionListener implements ActionListener {

	public BasicAction addAction;
	public BasicAction addVirtualAction;
	public BasicAction removeAction;
	public BasicAction renameAction;
	public BasicAction expungeAction;
	public BasicAction emptyAction;
	public BasicAction compactAction;
	public BasicAction applyFilterAction;
	public BasicAction filterPreferencesAction;
	public BasicAction moveupAction;
	public BasicAction movedownAction;
	public BasicAction subscribeAction;
	public BasicAction unsubscribeAction;

	private TreeController treeController;

	public FolderTreeActionListener(TreeController treeController) {
		this.treeController = treeController;

		initActions();
	}

	public void initActions() {

		addAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_newfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_newfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_newfolder"),
				"CREATE_SUBFOLDER",
				ImageLoader.getSmallImageIcon("folder.png"),
				ImageLoader.getImageIcon("folder.png"),
				'N',
				KeyStroke.getKeyStroke(KeyEvent.VK_N, ActionEvent.ALT_MASK));
		addAction.addActionListener(this);
		addAction.setEnabled(true);

		addVirtualAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_newvirtualfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_newvirtualfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_newvirtualfolder"),
				"CREATE_VIRTUAL_SUBFOLDER",
				ImageLoader.getSmallImageIcon("virtualfolder.png"),
				ImageLoader.getImageIcon("virtualfolder.png"),
				'0',
				KeyStroke.getKeyStroke(KeyEvent.VK_V, ActionEvent.ALT_MASK));
		addVirtualAction.addActionListener(this);
		addVirtualAction.setEnabled(true);

		renameAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_renamefolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_renamefolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_renamefolder"),
				"RENAME_FOLDER",
				null,
				null,
				'R',
				KeyStroke.getKeyStroke(KeyEvent.VK_F2, 0));
		renameAction.addActionListener(this);
		renameAction.setEnabled(true);

		removeAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_removefolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_removefolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_removefolder"),
				"REMOVE_FOLDER",
				ImageLoader.getSmallImageIcon("stock_delete-16.png"),
				ImageLoader.getImageIcon("stock_delete.png"),
				'D',
				KeyStroke.getKeyStroke(KeyEvent.VK_D, ActionEvent.ALT_MASK));
		removeAction.addActionListener(this);
		removeAction.setEnabled(true);

		expungeAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_expungefolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_expungefolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_expungefolder"),
				"EXPUNGE_FOLDER",
				null,
				null,
				'P',
				null);
		expungeAction.addActionListener(this);
		expungeAction.setEnabled(true);

		emptyAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_emptyfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_emptyfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_emptyfolder"),
				"EMPTY_FOLDER",
				null,
				null,
				'E',
				null);
		emptyAction.addActionListener(this);
		emptyAction.setEnabled(true);

		compactAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_compactfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_compactfolder"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_compactfolder"),
				"COMPACT_FOLDER",
				null,
				null,
				'F',
				null);
		compactAction.addActionListener(this);
		compactAction.setEnabled(true);
		//menu.addMenuEntry("FOLDER", addAction);

		applyFilterAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_applyfilter"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_applyfilter"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_applyfilter"),
				"APPLYFILTER",
				ImageLoader.getSmallImageIcon("apply-filters-16.png"),
				null,
				'F',
				null);
		applyFilterAction.addActionListener(this);
		applyFilterAction.setEnabled(true);

		filterPreferencesAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_filterconfig"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_filterconfig"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_filterconfig"),
				"FILTER_PREFERENCES",
				null,
				null,
				'U',
				null);
		filterPreferencesAction.addActionListener(this);
		filterPreferencesAction.setEnabled(true);

		moveupAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_moveup"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_moveup"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_moveup"),
				"MOVEUP",
				null,
				null,
				'0',
				null);
		moveupAction.addActionListener(this);
		moveupAction.setEnabled(true);

		movedownAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_movedown"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_movedown"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_movedown"),
				"movedown",
				null,
				null,
				'0',
				null);
		movedownAction.addActionListener(this);
		movedownAction.setEnabled(true);

		subscribeAction =
			new BasicAction(
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_subscribe"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_subscribe"),
				MailResourceLoader.getString(
					"menu",
					"mainframe",
					"menu_folder_subscribe"),
				"SUBSCRIBE",
				ImageLoader.getSmallImageIcon("remotehost.png"),
				ImageLoader.getImageIcon("remotehost.png"),
				'0',
				null);

		subscribeAction.addActionListener(this);
		subscribeAction.setEnabled(true);

	}

	public void actionPerformed(ActionEvent e) {

		String command = e.getActionCommand();

		if (command.equals("CREATE_SUBFOLDER")) {

			EditFolderDialog dialog = new EditFolderDialog("New Folder");
			dialog.showDialog();

			String name;

			if (dialog.success() == true) {
				// ok pressed
				name = dialog.getName();
			} else {
				// cancel pressed
				return;
			}

			FolderCommandReference[] r =
				(FolderCommandReference[]) treeController
					.getTreeSelectionManager()
					.getSelection();
			r[0].setFolderName(name);

			MainInterface.processor.addOp(new CreateSubFolderCommand(r));
		} else if (command.equals("CREATE_VIRTUAL_SUBFOLDER")) {
			EditFolderDialog dialog = new EditFolderDialog("New Folder");
			dialog.showDialog();

			String name;

			if (dialog.success() == true) {
				// ok pressed
				name = dialog.getName();
				
				try
				{
					treeController.getTreeSelectionManager().getFolder().addFolder( name, VirtualFolder.class );
					MainInterface.treeModel.nodeStructureChanged( treeController.getTreeSelectionManager().getFolder() );
					
				}
				catch ( Exception ex )
				{
					ex.printStackTrace();
				}
			} else {
				// cancel pressed
				return;
			}

			
			
			// FIXME

			/*
			EditFolderDialog dialog = TreeController.getInstance().getEditFolderDialog("New Folder");
			
			dialog.showDialog();
			
			String name;
			
			if (dialog.success() == true)
			{
				// ok pressed
				name = dialog.getName();
			}
			else
			{
				// cancel pressed
				return;
			}
			Folder vFolder = treeController.getView().getFolderTree().addVirtualFolder(name);
			changeActions();
			
			AdapterNode node = vFolder.getNode();
			
			SearchFrame searchDialog = new SearchFrame(vFolder);
			*/

		} else if (command.equals("RENAME_FOLDER")) {

			EditFolderDialog dialog = new EditFolderDialog("New Folder");
			dialog.showDialog();

			String name;

			if (dialog.success() == true) {
				// ok pressed
				name = dialog.getName();
			} else {
				// cancel pressed
				return;
			}

			FolderCommandReference[] r =
				(FolderCommandReference[]) treeController
					.getTreeSelectionManager()
					.getSelection();
			r[0].setFolderName(name);

			MainInterface.processor.addOp(new RenameFolderCommand(r));

		} else if (command.equals("APPLYFILTER")) {

			FolderCommandReference[] r =
				(FolderCommandReference[]) treeController
					.getTreeSelectionManager()
					.getSelection();

			//Folder folder = (Folder) r[0].getFolder();
			MainInterface.processor.addOp(new ApplyFilterCommand(r));

			/*
			Folder folder = treeController.getView().getSelected();
			Object[] uids = folder.getUids();
			
			FolderOperation op =
				new FolderOperation(Operation.FOLDER_APPLYFILTER, 10, uids, folder);
			MainInterface.crossbar.operate(op);
			
			
			changeActions();
			*/
		} else if (command.equals("REMOVE_FOLDER")) {

			FolderCommandReference[] r =
				(FolderCommandReference[]) treeController
					.getTreeSelectionManager()
					.getSelection();
			Folder folder = (Folder) r[0].getFolder();

			if (!folder.isLeaf()) {

				// warn user
				JOptionPane.showMessageDialog(
					null,
					"Your can only remove leaf folders!");
				return;
			}

			MainInterface.processor.addOp(new RemoveFolderCommand(r));

			/*
			Folder folder = treeController.getView().getSelected();
			
			FolderItem item = folder.getFolderItem();
			String access = item.getAccessRights();
			
			if (access.equals("user")) {
				if (item.getType().equals("virtual")) {
					Folder parent = (Folder) folder.getParent();
					folder.removeFromParent();
					TreeNodeEvent updateEvent =
						new TreeNodeEvent(
							parent,
							TreeNodeEvent.STRUCTURE_CHANGED);
			
					changeActions();
					return;
				}
			
				if (folder.isLeaf()) {
			
				} else {
					// warn user
					JOptionPane.showMessageDialog(
						null,
						"Your can only remove leaf folders !");
					return;
				}
			
			}
			
			changeActions();
			*/

		} else if (command.equals("FILTER_PREFERENCES")) {
			

			FolderCommandReference[] r =
				(FolderCommandReference[]) treeController
					.getTreeSelectionManager()
					.getSelection();
			Folder folder = (Folder) r[0].getFolder();

			if (folder == null)
				return;

			FolderItem item = folder.getFolderItem();
			if (item == null)
				return;

			folder.showFilterDialog(treeController.getMailFrameController());

			/*
			org.columba.mail.gui.config.filter.ConfigFrame dialog =
				new org.columba.mail.gui.config.filter.ConfigFrame(folder);
			*/

			/*
			if ((item.getType().equals("columba"))
				|| (item.getType().equals("imap"))) {
				FilterList filterList = folder.getFilterList();
			
				org.columba.mail.gui.config.filter.ConfigFrame dialog =
					new org.columba.mail.gui.config.filter.ConfigFrame(
						filterList);
			} else if (item.getType().equals("virtual")) {
				//AdapterNode searchNode = folder.getNode();
			
				SearchFrame dialog = new SearchFrame(folder);
				dialog.setVisible(true);
			}
			*/

		} else if (command.equals("EXPUNGE_FOLDER")) {

			ColumbaLogger.log.info("treeController=" + treeController);
			ColumbaLogger.log.info(
				"selectionmanager=" + treeController.getTreeSelectionManager());

			FolderCommandReference[] r =
				(FolderCommandReference[]) treeController
					.getTreeSelectionManager()
					.getSelection();

			/*
			Folder folder = (Folder) r[0].getFolder();
			FolderCommandReference[] result = new FolderCommandReference[2];
			result[0] = r[0];
			
			Folder trash = null;
			if (folder instanceof IMAPFolder) {
			} else {
				trash = (Folder) MainInterface.treeModel.getTrashFolder();
				ColumbaLogger.log.info("trash-folder" + trash);
			}
			
			result[1] = new FolderCommandReference(trash);
			*/

			ExpungeFolderCommand c = new ExpungeFolderCommand(r);

			MainInterface.processor.addOp(c);

		} else if (command.equals("EMPTY_FOLDER")) {
			Folder folder = treeController.getView().getSelected();

		} else if (command.equals("SUBSCRIBE")) {
			System.out.println("subscsribe");

			// FIXME
			/*
			Folder folder = treeController.getView().getSelected();
			FolderItem item = folder.getFolderItem();
			ImapRootFolder imapRootFolder = null;
			if ((item.getType().equals("imap")) || (item.getType().equals("imaproot")))
			{
				SubscribeDialog dialog = new SubscribeDialog();
				//dialog.pack();
				//dialog.setSize( dialog.getPreferredSize() );
			
				if (item.getType().equals("imap"))
				{
			
					imapRootFolder = ((ImapFolder) folder).getImapRootFolder();
					dialog.setFolder(imapRootFolder);
				}
				else
					dialog.setFolder(folder);
			
				dialog.showDialog();
			}
			*/
		}

	}

	public void changeActions() {
		removeAction.setEnabled(true);
		renameAction.setEnabled(true);
		/*
		FolderTreeNode treeNode = (FolderTreeNode) treeController.getSelected();
		
		Vector actions = treeNode.getSupportedActions();
		
		if (actions.contains(FolderTreeNode.REMOVE_FOLDER_ACTION)) {
			if (treeNode.isLeaf())
				removeAction.setEnabled(true);
			else
				removeAction.setEnabled(false);
		} else
			removeAction.setEnabled(false);
		
		if (actions.contains(FolderTreeNode.RENAME_FOLDER_ACTION))
			renameAction.setEnabled(true);
		else
			renameAction.setEnabled(false);
		*/

		/*
		Folder folder = (Folder) treeController.getSelected();
		if (folder == null)
			return;
		FolderItem item = folder.getFolderItem();
		
		addAction.setEnabled(true);
		addVirtualAction.setEnabled(true);
		
		if (item != null)
		{
			if (item.isSubfolderAllowed())
				addAction.setEnabled(true);
			else
				addAction.setEnabled(false);
		
			if ((item.getAccessRights().equals("user")) && (folder.isLeaf()))
				removeAction.setEnabled(true);
			else
				removeAction.setEnabled(false);
		
			if ((item.getAccessRights().equals("user")))
			{
				renameAction.setEnabled(true);
		
				FolderTreeNode parentFolder = (FolderTreeNode) folder.getParent();
				int index = parentFolder.getIndex(folder);
				int count = parentFolder.getChildCount();
		
				if (index >= 1)
					moveupAction.setEnabled(true);
				else
					moveupAction.setEnabled(false);
		
				if (index < count - 1)
					movedownAction.setEnabled(true);
				else
					movedownAction.setEnabled(false);
		
			}
			else
			{
				renameAction.setEnabled(false);
				movedownAction.setEnabled(false);
				moveupAction.setEnabled(false);
			}
		
			if (item.isMessageFolder())
			{
				/
				filterPreferencesAction.setEnabled(true);
		
				addVirtualAction.setEnabled(true);
			}
			else
			{
				applyFilterAction.setEnabled(false);
				filterPreferencesAction.setEnabled(false);
				addVirtualAction.setEnabled(false);
				expungeAction.setEnabled(false);
				emptyAction.setEnabled(false);
			}
		
			if ((item.getType().equals("imap")) || (item.getType().equals("imaproot")))
			{
				
				subscribeAction.setEnabled(true);
		
				filterPreferencesAction.setEnabled(true);
			}
			else
			{
				expungeAction.setEnabled(false);
				emptyAction.setEnabled(false);
				subscribeAction.setEnabled(false);
			}
		
			if (item.getType().equals("virtual"))
			{
				applyFilterAction.setEnabled(false);
				//                removeAction.setEnabled(true);
				addVirtualAction.setEnabled(false);
				filterPreferencesAction.setEnabled(true);
			}
		}
		else
		{
			System.out.println("item is null");
		}
		*/

	}

}