"org.columba.mail.folder");

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

import java.util.Enumeration;
import java.util.MissingResourceException;

import javax.swing.tree.DefaultTreeModel;

import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.FolderItem;
import org.columba.mail.config.FolderXmlConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.Root;
import org.columba.mail.gui.tree.util.SelectFolderDialog;
import org.columba.mail.gui.tree.util.TreeNodeList;
import org.columba.mail.plugin.FolderPluginHandler;
import org.columba.mail.util.MailResourceLoader;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class TreeModel extends DefaultTreeModel {
	protected FolderXmlConfig folderXmlConfig;

	private final Class[] FOLDER_ITEM_ARG = new Class[] { FolderItem.class };

	public TreeModel(FolderXmlConfig folderConfig) {
		super(new Root(folderConfig.getRoot().getElement("tree")));

		//System.out.println("root-uid=" + rootNode.getUid());
		this.folderXmlConfig = folderConfig;

		//System.out.println("root1=" + getRoot().toString());
		createDirectories(
			((FolderTreeNode) getRoot()).getNode(),
			(FolderTreeNode) getRoot());

		//System.out.println("root2=" + getRoot());

	}

	public void createDirectories(
		XmlElement parentTreeNode,
		FolderTreeNode parentFolder) {
		int count = parentTreeNode.count();

		XmlElement child;

		if (count > 0) {
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
					FolderTreeNode folder = add(child, parentFolder);
					if (folder != null)
						createDirectories(child, folder);
				}

			}
		}
	}

	public FolderTreeNode add(
		XmlElement childNode,
		FolderTreeNode parentFolder) {

		FolderItem item = new FolderItem(childNode);

		if (item == null)
			return null;

		// i18n stuff

		String name = null;

		//XmlElement.printNode(item.getRoot(), "");

		int uid = item.getInteger("uid");

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

		// now instanciate the folder classes

		String type = item.get("type");

		FolderPluginHandler handler =
			(FolderPluginHandler) MainInterface.pluginManager.getHandler(
				"folder");

		Object[] args = { item };

		FolderTreeNode folder = null;
		try {

			folder = (FolderTreeNode) handler.getPlugin(type, args);
			parentFolder.add(folder);
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		return folder;

		/*
		ClassLoader loader = ClassLoader.getSystemClassLoader();
		try {
			Class actClass = loader.loadClass(className);
			//System.out.println("superclass="+actClass.getSuperclass().getName());
			
			
			
			Constructor c = actClass.getConstructor(FOLDER_ITEM_ARG);
			
			if( c != null ) {
				Object[] args ={item};
			
				FolderTreeNode folder = (FolderTreeNode) c.newInstance( args);
				parentFolder.add( folder );
			
				return folder;
			}
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		*/
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
		
	}

	public FolderTreeNode getFolder(int uid) {
		FolderTreeNode root = (FolderTreeNode) getRoot();

		for (Enumeration e = root.breadthFirstEnumeration();
			e.hasMoreElements();
			) {
			FolderTreeNode node = (FolderTreeNode) e.nextElement();

			int id = node.getUid();

			if (uid == id) {

				return node;
			}

		}
		return null;

	}

	public FolderTreeNode getTrashFolder() {
		return getFolder(105);
	}

	public FolderTreeNode getImapFolder(int accountUid) {

		FolderTreeNode root = (FolderTreeNode) getRoot();

		for (Enumeration e = root.breadthFirstEnumeration();
			e.hasMoreElements();
			) {
			FolderTreeNode node = (FolderTreeNode) e.nextElement();

			if (node instanceof Folder) {
				Folder folder = (Folder) node;

				FolderItem item = folder.getFolderItem();
				if (item == null)
					continue;

				if (item
					.get("type")
					.equals("IMAPRootFolder")) {
					int account = item.getInteger("account_uid");

					if (account == accountUid) {
						int uid = item.getInteger("uid");

						return getFolder(uid);
					}

				}
			}

		}
		return null;

	}

	public FolderTreeNode getFolder(TreeNodeList list) {

		FolderTreeNode folder = null;

		FolderTreeNode parentFolder = (FolderTreeNode) getRoot();

		if (list == null)
			return parentFolder;

		if (list.count() == 0) {
			System.out.println("list count == null ");

			return parentFolder;
		}

		FolderTreeNode child = parentFolder;
		for (int i = 0; i < list.count(); i++) {
			String str = list.get(i);
			System.out.println("str: " + str);
			child = findFolder(child, str);
		}

		return child;

	}

	public FolderTreeNode findFolder(FolderTreeNode parentFolder, String str) {

		int count = parentFolder.getChildCount();
		FolderTreeNode child;
		FolderTreeNode folder;

		for (Enumeration e = parentFolder.children(); e.hasMoreElements();) {
			child = (FolderTreeNode) e.nextElement();

			if (child.getName().equals(str))
				return child;
			/*
			if (child instanceof Folder) {
				Folder f = (Folder) child;
				//System.out.println( "child: "+child.getName());
				if (f.getName().equals(str))
					return child;
			}
			*/
		}

		return null;
	}

	public SelectFolderDialog getSelectFolderDialog() {
		return new SelectFolderDialog();
	}

}