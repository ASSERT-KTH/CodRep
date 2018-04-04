public static Icon filesystemIcon = GUIUtilities.loadIcon("DriveSmall.png");

/*
 * FileCellRenderer.java - renders list and tree cells for the VFS browser
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999 Jason Ginchereau
 * Portions copyright (C) 2001 Slava Pestov
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package org.gjt.sp.jedit.browser;

//{{{ Imports
import java.awt.*;
import javax.swing.*;
import javax.swing.tree.*;
import javax.swing.border.*;
import org.gjt.sp.jedit.io.VFS;
import org.gjt.sp.jedit.*;
//}}}

public class FileCellRenderer extends DefaultTreeCellRenderer
{
	public static Icon fileIcon = GUIUtilities.loadIcon("File.png");
	public static Icon openFileIcon = GUIUtilities.loadIcon("OpenFile.png");
	public static Icon dirIcon = GUIUtilities.loadIcon("Folder.png");
	public static Icon openDirIcon = GUIUtilities.loadIcon("OpenFolder.png");
	public static Icon filesystemIcon = GUIUtilities.loadIcon("Drive.png");
	public static Icon loadingIcon = GUIUtilities.loadIcon("ReloadSmall.png");

	//{{{ FileCellRenderer constructor
	public FileCellRenderer()
	{
		plainFont = UIManager.getFont("Tree.font");
		boldFont = plainFont.deriveFont(Font.BOLD);
		setBorder(new EmptyBorder(1,0,1,0));
	} //}}}

	//{{{ getTreeCellRendererComponent() method
	public Component getTreeCellRendererComponent(JTree tree, Object value,
		boolean sel, boolean expanded, boolean leaf, int row,
		boolean focus)
	{
		super.getTreeCellRendererComponent(tree,value,sel,expanded,
			leaf,row,focus);

		DefaultMutableTreeNode treeNode = (DefaultMutableTreeNode)value;
		Object userObject = treeNode.getUserObject();
		if(userObject instanceof VFS.DirectoryEntry)
		{
			VFS.DirectoryEntry file = (VFS.DirectoryEntry)userObject;

			underlined = (jEdit.getBuffer(file.path) != null);

			setIcon(showIcons
				? getIconForFile(file,expanded)
				: null);
			setFont(file.type == VFS.DirectoryEntry.FILE
				? plainFont : boldFont);
			setText(file.name);

			if(!sel)
			{
				Color color = file.getColor();

				setForeground(color == null
					? UIManager.getColor("Tree.foreground")
					: color);
			}
		}
		else if(userObject instanceof BrowserView.LoadingPlaceholder)
		{
			setIcon(showIcons ? loadingIcon : null);
			setFont(plainFont);
			setText(jEdit.getProperty("vfs.browser.tree.loading"));
			underlined = false;
		}
		else if(userObject instanceof String)
		{
			setIcon(showIcons ? dirIcon : null);
			setFont(boldFont);
			setText((String)userObject);
			underlined = false;
		}
		else
		{
			// userObject is null?
			setIcon(null);
			setText(null);
		}

		return this;
	} //}}}

	//{{{ paintComponent() method
	public void paintComponent(Graphics g)
	{
		if(underlined)
		{
			Font font = getFont();

			FontMetrics fm = getFontMetrics(getFont());
			int x, y;
			if(getIcon() == null)
			{
				x = 0;
				y = fm.getAscent() + 2;
			}
			else
			{
				x = getIcon().getIconWidth() + getIconTextGap();
				y = Math.max(fm.getAscent() + 2,16);
			}
			g.setColor(getForeground());
			g.drawLine(x,y,x + fm.stringWidth(getText()),y);
		}

		super.paintComponent(g);
	} //}}}

	//{{{ Package-private members
	boolean showIcons;

	//{{{ propertiesChanged() method
	void propertiesChanged()
	{
		showIcons = jEdit.getBooleanProperty("vfs.browser.showIcons");
	} //}}}

	//}}}

	//{{{ Private members

	//{{{ Instance members
	private Font plainFont;
	private Font boldFont;

	private boolean underlined;
	//}}}

	//{{{ getIconForFile() method
	private Icon getIconForFile(VFS.DirectoryEntry file, boolean expanded)
	{
		if(file.type == VFS.DirectoryEntry.DIRECTORY)
			return (expanded ? openDirIcon : dirIcon);
		else if(file.type == VFS.DirectoryEntry.FILESYSTEM)
			return filesystemIcon;
		else if(jEdit.getBuffer(file.path) != null)
			return openFileIcon;
		else
			return fileIcon;
	} //}}}

	//}}}
}