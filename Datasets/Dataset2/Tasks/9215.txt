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

package org.columba.mail.gui.config.filter.plugins;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;

import org.columba.mail.filter.FilterAction;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.config.filter.ActionList;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.gui.tree.util.TreeNodeList;
import org.columba.main.MainInterface;

public class FolderChooserActionRow extends DefaultActionRow implements ActionListener {

	private JButton treePathButton;

	public FolderChooserActionRow(ActionList list, FilterAction action) {
		super(list, action);

	}

	public void updateComponents(boolean b) {
		super.updateComponents(b);

		if (b) {
			int uid = filterAction.getUid();
			Folder folder = (Folder) MainInterface.treeModel.getFolder(uid);
			String treePath = folder.getTreePath();

			treePathButton.setText(treePath);
		} else {
			String treePath = treePathButton.getText();
			TreeNodeList list = new TreeNodeList(treePath);
			Folder folder = (Folder) MainInterface.treeModel.getFolder(list);
			int uid = folder.getUid();
			filterAction.setUid(uid);
		}

	}

	public void initComponents() {
		super.initComponents();

		treePathButton = new JButton();
		treePathButton.addActionListener(this);
		treePathButton.setActionCommand("TREEPATH");
		
		addComponent(treePathButton);

	}

	public void actionPerformed(ActionEvent e) {
		String action = e.getActionCommand();

		if (action.equals("TREEPATH")) {
			SelectFolderDialog dialog =
				MainInterface
					.treeModel
					.getSelectFolderDialog();
			

			if (dialog.success()) {
				Folder folder = dialog.getSelectedFolder();

				String treePath = folder.getTreePath();

				treePathButton.setText(treePath);
			}

		} 
	}

}