references[0] = new FolderCommandReference(folder);

package org.columba.mail.gui.tree;

import java.util.Vector;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.gui.util.SelectionManager;
import org.columba.core.logging.ColumbaLogger;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
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
		references[0] = new FolderCommandReference((Folder) folder);

		return references;
	}

}