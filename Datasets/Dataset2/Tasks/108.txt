protected Lock myLock;

package org.columba.mail.folder;

import java.util.Hashtable;

import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreeNode;

import org.columba.core.command.WorkerStatusController;
import org.columba.core.config.AdapterNode;
import org.columba.core.util.Lock;
import org.columba.main.MainInterface;
import org.columba.mail.config.FolderItem;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public abstract class FolderTreeNode
	extends DefaultMutableTreeNode
	implements TreeNodeInterface {

	protected AdapterNode node;
	private Lock myLock;

	public FolderTreeNode(AdapterNode node) {

		super();
		this.node = node;
		myLock = new Lock(this);
	}

	public int getUid() {
		return -1;
	}

	public CapabilityList getSupportedActions() {
		CapabilityList v = CapabilityList.getDefaultFolderCapabilities();

		Hashtable table = getAttributes();

		if (table.contains("accessrights")) {
			String accessrights = (String) table.get("accessrights");

			if (accessrights.equals("user")) {
				v.add(CapabilityList.RENAME_FOLDER_ACTION);
				v.add(CapabilityList.REMOVE_FOLDER_ACTION);
			}
		}

		if (table.contains("messagefolder")) {
			String messagefolder = (String) table.get("messagefolder");

			if (messagefolder.equals("true")) {
				v.add(CapabilityList.FOLDER_SHOW_HEADERLIST_ACTION);
			}
		}

		return v;

	}

	public synchronized boolean tryToGetLock() {
		return myLock.tryToGetLock();
	}
	
	public void releaseLock()
	{
		myLock.release();
	}

	public AdapterNode getNode() {
		return node;
	}

	public String getName() {
		return toString();
	}

	public void setName(String s) {
		this.setUserObject(s);
	}

	public String toString() {
		return (String) this.getUserObject();
	}

	public void insert(Folder newFolder, int newIndex) {

		Folder oldParent = (Folder) newFolder.getParent();
		int oldIndex = oldParent.getIndex(newFolder);
		oldParent.remove(oldIndex);

		AdapterNode oldParentNode = oldParent.getNode();
		AdapterNode newChildNode = newFolder.getNode();
		oldParentNode.removeChild(newChildNode);

		newFolder.setParent(this);
		children.insertElementAt(newFolder, newIndex);

		AdapterNode newParentNode = node;

		int j = -1;
		boolean inserted = false;
		for (int i = 0; i < newParentNode.getChildCount(); i++) {
			AdapterNode n = newParentNode.getChildAt(i);
			String name = n.getName();

			if (name.equals("folder")) {
				j++;
			}

			if (j == newIndex) {
				newParentNode.insert(newChildNode, i);
				inserted = true;
				System.out.println("------> adapternode insert correctly");
			}
		}

		if (inserted == false) {
			if (j + 1 == newIndex) {
				newParentNode.appendChild(newChildNode);
				System.out.println("------> adapternode appended correctly");
			}
		}

		//oldParent.fireTreeNodeStructureUpdate();
		//fireTreeNodeStructureUpdate();
	}

	public void removeFromParent() {
		AdapterNode childAdapterNode = getNode();
		childAdapterNode.remove();

		super.removeFromParent();
	}

	public void removeFolder() throws Exception {
		removeFromParent();
	}

	public void remove(FolderTreeNode childNode) {
		FolderTreeNode childFolder = (FolderTreeNode) childNode;
		AdapterNode childAdapterNode = childFolder.getNode();
		childAdapterNode.remove();

		int index = getIndex(childFolder);
		children.removeElementAt(index);
		//fireTreeNodeStructureUpdate();

		//return childFolder;
	}

	public abstract Folder instanceNewChildNode(
		AdapterNode node,
		FolderItem item);

	public abstract Hashtable getAttributes();

	public abstract void createChildren(WorkerStatusController worker);

	public FolderTreeNode addSubFolder(Hashtable attributes) throws Exception {
		AdapterNode node = MainInterface.treeModel.addFolder(this, attributes);
		FolderItem item = MainInterface.treeModel.getItem(node);

		Folder subFolder = instanceNewChildNode(node, item);
		add(subFolder);

		return subFolder;
	}

	public boolean addFolder(String name) throws Exception {
		Hashtable attributes = getAttributes();
		attributes.put("name", name);

		FolderTreeNode folder = addSubFolder(attributes);
		return true;
	}

	/*
	public void removeFromParent()
	{
		
		Folder parentFolder = (Folder) getParent();
		parentFolder.remove(this);
		
	}
	*/

	/*
	public void moveUp()
	{
		Folder parentFolder = (Folder) getParent();
		if (parentFolder == null)
			return;
	
		AdapterNode parentNode = parentFolder.getNode();
	
		int childCount = parentFolder.getChildCount();
	
		int childIndex = parentFolder.getIndex((Folder) this);
		if (childIndex == -1)
			return;
		if (childIndex == 0)
			return;
	
		parentFolder.insert(this, childIndex - 1);
	
	}
	*/

	/*
	public void moveDown()
	{
		Folder parentFolder = (Folder) getParent();
		if (parentFolder == null)
			return;
	
		AdapterNode parentNode = parentFolder.getNode();
	
		int childCount = parentFolder.getChildCount();
	
		int childIndex = parentFolder.getIndex((Folder) this);
		if (childIndex == -1)
			return;
		if (childIndex >= childCount - 1)
			return;
	
		parentFolder.insert(this, childIndex + 1);
	}
	*/

	public TreeNode getChild(String str) {
		for (int i = 0; i < getChildCount(); i++) {
			Folder child = (Folder) getChildAt(i);
			String name = child.getName();

			if (name.equalsIgnoreCase(str))
				return child;
		}
		return null;
	}

	public void append(Folder newFolder) {
		Folder oldParent = (Folder) newFolder.getParent();
		int oldIndex = oldParent.getIndex(newFolder);
		oldParent.remove(oldIndex);

		AdapterNode oldParentNode = oldParent.getNode();
		AdapterNode newChildNode = newFolder.getNode();
		oldParentNode.removeChild(newChildNode);

		newFolder.setParent(this);
		children.add(newFolder);

		AdapterNode newParentNode = node;
		newParentNode.appendChild(newChildNode);

		// oldParent.fireTreeNodeStructureUpdate();
		// fireTreeNodeStructureUpdate();
	}

}