import org.columba.mail.gui.table.selection.TableSelectionManager;

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
package org.columba.mail.gui.attachment;

import java.util.Vector;

import org.columba.core.command.DefaultCommandReference;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.gui.table.MessageSelectionListener;
import org.columba.mail.gui.table.TableSelectionManager;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class AttachmentSelectionManager extends TableSelectionManager implements MessageSelectionListener {

	protected Integer[] address;

	protected Vector attachmentListenerList;
	/**
	 * Constructor for AttachmentSelectionManager.
	 */
	public AttachmentSelectionManager() {
		super();
		attachmentListenerList = new Vector();
	}

	public void addAttachmentSelectionListener(AttachmentSelectionListener listener) {
		attachmentListenerList.add(listener);
	}

	public void fireAttachmentSelectionEvent(Integer[] old, Integer[] newAddress) {
		address = newAddress;

		for (int i = 0; i < treeListenerList.size(); i++) {
			AttachmentSelectionListener l =
				(AttachmentSelectionListener) attachmentListenerList.get(i);
			l.attachmentSelectionChanged(newAddress);
		}
	}

	public Integer[] getAddress()
	{
		return address;
	}

	public DefaultCommandReference[] getSelection() {
		//System.out.println("folder="+getFolder());
		//System.out.println("uids="+getUids());
		
		FolderCommandReference[] references = new FolderCommandReference[1];
		references[0] =
			new FolderCommandReference((Folder) getFolder(), getUids(), address);

		return references;
	}
	
	public void setFolder( FolderTreeNode node )
	{
		this.folder = node;
	}
	
	public void setUids( Object[] uids )
	{
		this.uids = uids;
	}
	
	/**
	 * @see org.columba.mail.gui.table.MessageSelectionListener#messageSelectionChanged(java.lang.Object)
	 */
	public void messageSelectionChanged(Object[] newUidList) {
		uids = newUidList;
	}

}