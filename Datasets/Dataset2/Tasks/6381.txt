public FolderChildrenIterator(IMailFolder parent) {

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

package org.columba.mail.folder;

import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.List;

import javax.swing.tree.TreeNode;


/**
 * Iterate through all children using depth-first search.
 * 
 * @author tstich
 */
public class FolderChildrenIterator {
	private List folderList;
	Iterator folderIterator;
	
	public FolderChildrenIterator(AbstractFolder parent) {
		folderList = new ArrayList();
		Enumeration childEnum = parent.children();
		while( childEnum.hasMoreElements() ) {
			appendAllChildren(folderList, (TreeNode)childEnum.nextElement());
		}
		
		folderIterator = folderList.iterator();
	}
	
	private void appendAllChildren(List folderList, TreeNode folder) {		
		folderList.add(folder);		
		if( folder.getChildCount() > 0) {
			Enumeration childEnum = folder.children();
			while( childEnum.hasMoreElements() ) {
				appendAllChildren(folderList, (TreeNode) childEnum.nextElement());
			}
		}
	}
	
	public boolean hasMoreChildren() {
		return folderIterator.hasNext();
	}

	public AbstractFolder nextChild() {
		return (AbstractFolder) folderIterator.next();
	}
	
}