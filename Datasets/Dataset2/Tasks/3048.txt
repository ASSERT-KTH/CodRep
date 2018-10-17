"org.columba.addressbook.folder");

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

package org.columba.addressbook.gui.tree;

import java.util.Enumeration;

import javax.swing.tree.DefaultTreeModel;

import org.columba.addressbook.config.FolderItem;
import org.columba.addressbook.folder.Root;
import org.columba.addressbook.plugin.FolderPluginHandler;
import org.columba.core.config.DefaultXmlConfig;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.xml.XmlElement;

public class AddressbookTreeModel extends DefaultTreeModel {
	//private AddressbookTreeNode rootNode;

	protected DefaultXmlConfig folderXmlConfig;

	private final Class[] FOLDER_ITEM_ARG = new Class[] { FolderItem.class };

	public AddressbookTreeModel(XmlElement root) {
		super(new Root(root));

		//this.folderXmlConfig = xmlConfig;

		//System.out.println("root1=" + getRoot().toString());
		createDirectories(
			((AddressbookTreeNode) getRoot()).getNode(),
			(AddressbookTreeNode) getRoot());
	}

	public void createDirectories(
		XmlElement parentTreeNode,
		AddressbookTreeNode parentFolder) {
		int count = parentTreeNode.count();

		XmlElement child;

		for (int i = 0; i < count; i++) {
			child = parentTreeNode.getElement(i);
			String name = child.getName();
			//XmlElement nameNode = child.getName();
			//                System.out.println( "node: "+child );
			//                System.out.println( "nodename: "+nameNode.getValue());

			/*
			if ((name.equals("tree")) || (name.equals("folder"))) {
				FolderTreeNode folder = add(child, parentFolder);
				if (folder != null)
					createDirectories(child, folder);
			}
			*/
			if (name.equals("folder")) {
				AddressbookTreeNode folder = add(child, parentFolder);
				if (folder != null)
					createDirectories(child, folder);
			}
		}
	}

	public AddressbookTreeNode add(
		XmlElement childNode,
		AddressbookTreeNode parentFolder) {

		FolderItem item = new FolderItem(childNode);

		if (item == null)
			return null;

		// i18n stuff

		String name = null;

		//XmlElement.printNode(item.getRoot(), "");

		int uid = item.getInteger("uid");

		/*
		try {
			if (uid == 100)
				name = MailResourceLoader.getString("tree", "localfolders");
			else if (uid == 101)
				name = MailResourceLoader.getString("tree", "inbox");
		
			else if (uid == 102)
				name = MailResourceLoader.getString("tree", "drafts");
		
			else if (uid == 103)
				name = MailResourceLoader.getString("tree", "outbox");
		
			else if (uid == 104)
				name = MailResourceLoader.getString("tree", "sent");
		
			else if (uid == 105)
				name = MailResourceLoader.getString("tree", "trash");
		
			else if (uid == 106)
				name = MailResourceLoader.getString("tree", "search");
			else if (uid == 107)
				name = MailResourceLoader.getString("tree", "templates");
		
			else
				name = item.get("property", "name");
		
			item.set("property", "name", name);
		
		} catch (MissingResourceException ex) {
			name = item.get("property", "name");
		}
		*/

		name = item.get("property", "name");

		// now instanciate the folder classes

		String type = item.get("type");

		Object[] args = { item };

		FolderPluginHandler handler = null;
		try {
			handler =
				(FolderPluginHandler) MainInterface.pluginManager.getHandler(
					"addressbook_folder");
		} catch (PluginHandlerNotFoundException ex) {
			NotifyDialog d = new NotifyDialog();
			d.showDialog(ex);
		}

		AddressbookTreeNode folder = null;
		try {

			folder = (AddressbookTreeNode) handler.getPlugin(type, args);
			parentFolder.add(folder);
		} catch (Exception ex) {
			ex.printStackTrace();
		}

		return folder;

		/*
		if (item.getType().equals("columba")) {
			//ColumbaFolder f = new ColumbaFolder(childNode, item);
			CachedMHFolder f = new CachedMHFolder(childNode, item);
		
			FilterList list = new FilterList(f);
			parentFolder.add(f);
		
			return f;
		} else if (item.getType().equals("virtual")) {
		
			VirtualFolder f = new VirtualFolder(childNode, item);
			Search search = new Search(childNode, f);
			parentFolder.add(f);
		
			return f;
		} else if (item.getType().equals("outbox")) {
		
			OutboxFolder f = new OutboxFolder(childNode, item);
			parentFolder.add(f); // Do never exchange with line below!!
		
			return f;
		
		} else if (item.getType().equals("imap")) {
			AccountItem accountItem =
				MailConfig.getAccountList().uidGet(item.getAccountUid());
		
			ImapItem item2 = accountItem.getImapItem();
		
			IMAPRootFolder imapRootFolder = null;
		
			IMAPFolder f =
				new IMAPFolder(childNode, item, item2, imapRootFolder);
			FilterList list = new FilterList(f);
			parentFolder.add(f);
		
			return f;
		
		} else if (item.getType().equals("imaproot")) {
		
			AccountItem accountItem =
				MailConfig.getAccountList().uidGet(item.getAccountUid());
		
			ImapItem item2 = accountItem.getImapItem();
		
			IMAPRootFolder f =
				new IMAPRootFolder(
					childNode,
					item,
					item2,
					item.getAccountUid());
			f.setName(accountItem.getName());
			parentFolder.add(f);
		
			return f;
		}
		*/
		//return null;
	}

	public AddressbookTreeNode getFolder(int uid) {
		AddressbookTreeNode root = (AddressbookTreeNode) getRoot();

		for (Enumeration e = root.breadthFirstEnumeration();
			e.hasMoreElements();
			) {
			AddressbookTreeNode node = (AddressbookTreeNode) e.nextElement();
			if (node instanceof Root)
				continue;

			int id = node.getUid();

			if (uid == id) {

				return node;
			}

		}
		return null;

	}

	/* ===================================================================== */
	// methods for TreeModel implementation

	/*
	public Object getRoot() {
		return rootNode;
	}
	
	public boolean isLeaf(Object aNode) {
		AddressbookTreeNode node = (AddressbookTreeNode) aNode;
		if (node.getChildCount() > 0)
			return false;
		return true;
	}
	
	public int getChildCount(Object parent) {
		AddressbookTreeNode node = (AddressbookTreeNode) parent;
		return node.getChildCount();
	}
	
	public Object getChild(Object parent, int index) {
		AddressbookTreeNode node = (AddressbookTreeNode) parent;
		return node.getChildAt(index);
	}
	
	public int getIndexOfChild(Object parent, Object child) {
		AddressbookTreeNode node = (AddressbookTreeNode) parent;
		return node.getIndex((AddressbookTreeNode) child);
	}
	*/
}