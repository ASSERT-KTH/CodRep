public String getDefaultChild() {

package org.columba.mail.folder;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.FolderItem;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class Root extends FolderTreeNode {

	
	FolderItem item;
	public Root(XmlElement node) {
			super(new FolderItem(node));
	}

	/**
	 * @see org.columba.modules.mail.folder.FolderTreeNode#instanceNewChildNode(AdapterNode, FolderItem)
	 */
	public Class getDefaultChild() {
		return null;
	}

	public void createChildren(WorkerStatusController c) {
	}



}