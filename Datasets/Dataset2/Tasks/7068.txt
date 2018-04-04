import org.columba.ristretto.message.MessageFolderInfo;

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
package org.columba.mail.gui.tree.util;

import java.awt.Color;
import java.awt.Component;
import java.awt.Font;

import javax.swing.ImageIcon;
import javax.swing.JTree;
import javax.swing.UIManager;
import javax.swing.border.Border;
import javax.swing.tree.DefaultTreeCellRenderer;

import org.columba.core.gui.util.ImageLoader;
import org.columba.mail.config.FolderItem;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.FolderTreeNode;
import org.columba.mail.folder.MessageFolderInfo;

/**
 * This class is used for the mail folder tree. It it extended from JLabel and shows the folder names in a tree.
 */
public class FolderTreeCellRenderer
	extends DefaultTreeCellRenderer //extends JLabel implements TreeCellRenderer
{
	Border unselectedBorder = null;
	Border selectedBorder = null;
	boolean isBordered = true;
	boolean bool;
	//TreeController treeController;

	private ImageIcon defaultIcon, localhostIcon, remotehostIcon, virtualfolderIcon;

	private Font plainFont, boldFont, italicFont;

	/**
	 * Generates a new CellRenderer. In this contructor font and images are set to local variables. The fonts are
	 * depended on the current UIManager.
	 * @param bool i don't know (waffel)
	 */
	public FolderTreeCellRenderer(boolean bool) {
		super();

		//this.treeController = treeController;

		this.bool = bool;

		boldFont = UIManager.getFont("Tree.font");
		boldFont = boldFont.deriveFont(Font.BOLD);
		italicFont = UIManager.getFont("Tree.font");
		italicFont = italicFont.deriveFont(Font.ITALIC);
		plainFont = UIManager.getFont("Tree.font");

		defaultIcon = ImageLoader.getSmallImageIcon("folder.png");
		localhostIcon = ImageLoader.getSmallImageIcon("localhost.png");

		remotehostIcon = ImageLoader.getSmallImageIcon("remotehost.png");
		virtualfolderIcon = ImageLoader.getSmallImageIcon("virtualfolder.png");

	}

	/**
	 * The tooltip text and unseen counter for the current folder component are set. If the folder has unseen Messages the
	 * folder self is show as bold and the unseen message counter is added to the folder label. The folder becomes a tooltip
	 * where infos (unseen, recent, total) are set. If the folder is an Imap-folder and not selectable the folder is set to
	 * italic with a darkgrey background.  
	 * @see javax.swing.tree.TreeCellRenderer#getTreeCellRendererComponent(javax.swing.JTree, java.lang.Object, boolean, boolean, boolean, int, boolean)
	 */
	public Component getTreeCellRendererComponent(
		JTree tree,
		Object value,
		boolean isSelected,
		boolean expanded,
		boolean leaf,
		int row,
		boolean hasFocusVar) {

		// setting default Values
		setFont(plainFont);
		setToolTipText("");

		// TODO why we call this? the return value is never used. (waffel)
		super.getTreeCellRendererComponent(
			tree,
			value,
			isSelected,
			expanded,
			leaf,
			row,
			hasFocusVar);

		Folder folder = null;

		// try to cast the given value to Folder
		try {
			folder = (Folder) value;
			// if there is an Exception, then set for the Label (this) the String from the FolderTreeNode. The value MUST BE HERE
			// a tree node
			// TODO i don't know if in any case the value is a FolderTreeNode if it is not a Folder (waffel)
		} catch (Exception ex) {
			setText(((FolderTreeNode) value).toString());
			return this;
		}

		// if the value was an folder
		if (folder != null) {
			// getting folder info
			MessageFolderInfo info = folder.getMessageFolderInfo();
			// getting unseen value
			int unseen = info.getUnseen();
			// mark name bold if folder contains any unseen messages
			// the default is alrady set to plain
			if (unseen > 0) {
				setFont(boldFont);
			}

			FolderItem item = folder.getFolderItem();
			if (item != null) {
				String name;
				name = item.get("property", "name");

				// append unseen count to folder name
				if (unseen > 0)
					name = name + " (" + unseen + ") ";

				// set tooltip text
				StringBuffer buf = new StringBuffer();
				buf.append("<html><body>&nbsp;Total: " + info.getExists());
				buf.append("<br>&nbsp;Unseen: " + unseen);
				buf.append("<br>&nbsp;Recent: " + info.getRecent());
				buf.append("</body></html>");
				setToolTipText(buf.toString());

				setText(name);

				// set icons
				if (expanded) {
					setIcon(folder.getExpandedIcon());
				} else {
					setIcon(folder.getCollapsedIcon());
				}

				// important for imap
				// is this folder is not selectable 
				if (!item.getBoolean("selectable", true)) {
					setFont(italicFont);
					setForeground(Color.darkGray);
				}
			}
		}
		return this;
	}
}