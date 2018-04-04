import org.columba.mail.gui.table.model.MessageNode;

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
package org.columba.mail.gui.table.action;

import java.awt.event.ActionEvent;

import javax.swing.tree.DefaultMutableTreeNode;

import org.columba.core.action.JAbstractAction;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.main.MainInterface;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.frame.TableOwnerInterface;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.util.MessageNode;

/**
 * @author waffel
 *
 * The upAction is the action when you pressing the up key (not on NUM-PAD). 
 * If you do so, the previouseMessage up your key is selected and shown in the
 * message-view. If no more message up your key, then nothing changed.
 */

public class UpAction extends JAbstractAction {
	
	TableController tableController;
	AbstractMailFrameController frameController;

	public UpAction(AbstractMailFrameController frameController) {
		super();
		this.tableController = ( (TableOwnerInterface) frameController).getTableController();
		this.frameController = frameController;
		
	}
	
	/* (non-Javadoc)
	 * @see java.awt.event.ActionListener#actionPerformed(java.awt.event.ActionEvent)
	 */
	public void actionPerformed(ActionEvent arg0) {
		ColumbaLogger.log.debug("action up performed");
		// getting last selection
		FolderCommandReference[] r = frameController.getTableSelection();
		FolderCommandReference ref = r[0];
		ColumbaLogger.log.debug("folderCommandRef: "+ref);
		// getting current uid
		Object[] uids = ref.getUids();
		ColumbaLogger.log.debug("curr uids: "+uids);
		// getting current node (under the selection)
		DefaultMutableTreeNode currNode = tableController.getView().getMessagNode(uids[0]);
		ColumbaLogger.log.debug("currNode: "+currNode);
		// getting prev node
		DefaultMutableTreeNode prevNode = currNode.getPreviousNode();
		ColumbaLogger.log.debug("prevNode: "+prevNode);
		Object[] prevUids = new Object[1];
		prevUids[0] = ((MessageNode)prevNode).getUid();
		ColumbaLogger.log.debug("prevUids: "+prevUids);
		ref.setUids(prevUids);
		
		// check if the node is not null
		MessageNode[] nodes = new MessageNode[prevUids.length];
		for (int i = 0; i < prevUids.length; i++) {
			nodes[i] = tableController.getHeaderTableModel().getMessageNode(prevUids[i]);
		}
		boolean node_ok = true;
		for (int i = 0; i < nodes.length; i++) {
			if (nodes[i]== null) {
				node_ok = false;
				break;
			}
		}
		// if the node is not null
		if (node_ok) {
			// select it
			tableController.setSelected(prevUids);
			// saving the last selection for the current folder
			((Folder)ref.getFolder()).setLastSelection(prevUids[0]);
			int row = tableController.getView().getSelectedRow();
			tableController.getView().scrollRectToVisible(tableController.getView().getCellRect(row,0,false));
					
			FolderCommandReference[] refNew = new FolderCommandReference[1]; 
			refNew[0] = new FolderCommandReference( ref.getFolder(), prevUids); 
			// view the message under the new node
			MainInterface.processor.addOp(new ViewMessageCommand(frameController, refNew));
		}
		
	}

}