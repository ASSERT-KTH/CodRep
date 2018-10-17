import org.columba.core.gui.selection.SelectionManager;

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

import java.util.Vector;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.gui.SelectionManager;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.FolderTreeNode;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class TreeSelectionManager extends SelectionManager {

	protected FolderTreeNode folder;
	
	protected Vector treeListenerList;
	
	/**
	 * Constructor for TreeSelectionManager.
	 */
	public TreeSelectionManager() {
		super();
		treeListenerList = new Vector();
	}
	
	public FolderTreeNode getFolder() {
		return folder;
	}
	
	public void addFolderSelectionListener(FolderSelectionListener listener) {
		treeListenerList.add(listener);
	}
	
	public void fireFolderSelectionEvent(
		FolderTreeNode oldFolder,
		FolderTreeNode newFolder) {
		folder = newFolder;

		for (int i = 0; i < treeListenerList.size(); i++) {
			FolderSelectionListener l =
				(FolderSelectionListener) treeListenerList.get(i);
			l.folderSelectionChanged(newFolder);
		}
	}
	
	public DefaultCommandReference[] getSelection()
	{
		ColumbaLogger.log.info("folder="+folder);
		
		FolderCommandReference[] references = new FolderCommandReference[1];
		references[0] = new FolderCommandReference(folder);

		return references;
	}

}