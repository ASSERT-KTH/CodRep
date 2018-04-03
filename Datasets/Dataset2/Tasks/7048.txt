import org.columba.core.gui.selection.SelectionHandler;

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

import java.util.LinkedList;
import java.util.ListIterator;

import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.tree.TreePath;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.gui.util.SelectionHandler;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;

public class TreeSelectionHandler
	extends SelectionHandler
	implements TreeSelectionListener {

	private TreeView view;
	private LinkedList selectedFolders;

	private final static Folder[] folderArray = { null };

	public TreeSelectionHandler(TreeView view) {
		super("mail.tree");
		this.view = view;
		view.addTreeSelectionListener(this);
		selectedFolders = new LinkedList();
	}

	/* (non-Javadoc)
	 * @see org.columba.core.gui.util.SelectionHandler#getSelection()
	 */
	public DefaultCommandReference[] getSelection() {
		FolderCommandReference[] references =
			new FolderCommandReference[selectedFolders.size()];
		ListIterator it = selectedFolders.listIterator();
		int i = 0;
		while (it.hasNext()) {
			references[i++] = new FolderCommandReference((Folder) it.next());
		}

		return references;
	}

	/* (non-Javadoc)
	 * @see javax.swing.event.TreeSelectionListener#valueChanged(javax.swing.event.TreeSelectionEvent)
	 */
	public void valueChanged(TreeSelectionEvent e) {

		// BUGFIX but don't know why that bug occurs 
		if (e.getPath() == null)
			return;
		/*
		if (view.getLastSelectedPathComponent() == null)
			return;
		
		newSelection = (FolderTreeNode) view.getLastSelectedPathComponent();
		
		if( selectedFolder != newSelection ) {
			selectedFolder = newSelection;
			ColumbaLogger.log.debug("Selected Folder = "+selectedFolder.getName());
			fireSelectionChanged(new FolderSelectionChangedEvent(selectedFolder));
		}
		*/

		for (int i = 0; i < e.getPaths().length; i++) {
			if (e.getPaths()[i].getLastPathComponent() instanceof Folder) {
				Folder folder = (Folder) e.getPaths()[i].getLastPathComponent();
				if (e.isAddedPath(i)) {
					ColumbaLogger.log.debug(
						"Folder added to Selection= " + folder.getName());
					selectedFolders.add(folder);
				} else {
					ColumbaLogger.log.debug(
						"Folder removed from Selection= " + folder.getName());
					selectedFolders.remove(folder);
				}
			}
		}

		fireSelectionChanged(
			new FolderSelectionChangedEvent(
				(Folder[]) selectedFolders.toArray(folderArray)));
	}

	public void setSelection(DefaultCommandReference[] selection) {
		view.clearSelection();
		view.requestFocus();

		TreePath path[] = new TreePath[selection.length];

		for (int i = 0; i < selection.length; i++) {
			path[i] =
				((FolderCommandReference) selection[i])
					.getFolder()
					.getSelectionTreePath();
			view.setLeadSelectionPath(path[i]);
			view.setAnchorSelectionPath(path[i]);
			view.expandPath(path[i]);
		}

		view.setSelectionPaths(path);
	}

}