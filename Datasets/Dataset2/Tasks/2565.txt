import org.columba.ristretto.message.HeaderInterface;

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
package org.columba.mail.gui.table.model;

import java.util.List;

import javax.swing.tree.DefaultMutableTreeNode;

import org.columba.mail.message.HeaderInterface;

/**
 * Title:
 * Description:
 * Copyright:    Copyright (c) 2001
 * Company:
 * @author
 * @version 1.0
 */

public class MessageNode extends DefaultMutableTreeNode {
	
	protected  Object uid;

	protected boolean hasRecentChildren;
	 
	public MessageNode(Object header, Object uid) {
		super(header);

		this.uid = uid;
	}

	public List getVector() {
		return children;
	}

	public void setUid(Object uid) {
		this.uid = uid;
	}
	public Object getUid() {
		return uid;
	}

	public HeaderInterface getHeader() {
		return (HeaderInterface) getUserObject();
	}

	public static Object[] toUidArray(Object[] nodes) {
		if (nodes[0] instanceof MessageNode) {
			Object[] newUidList = new Object[nodes.length];
			for (int i = 0; i < nodes.length; i++) {
				newUidList[i] = ((MessageNode) nodes[i]).getUid();
				//System.out.println("node=" + newUidList[i]);
			}
			return newUidList;
		} else
			return nodes;
	}

	/**
	 * Returns the hasRecentChildren.
	 * @return boolean
	 */
	public boolean isHasRecentChildren() {
		return hasRecentChildren;
	}

	/**
	 * Sets the hasRecentChildren.
	 * @param hasRecentChildren The hasRecentChildren to set
	 */
	public void setHasRecentChildren(boolean hasRecentChildren) {
		this.hasRecentChildren = hasRecentChildren;
	}
	
}