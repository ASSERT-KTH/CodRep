final View view = GUIUtilities.getView(this);

/*
 * RecentFilesMenu.java - Recent file list menu
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2000, 2001 Slava Pestov
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 */

package org.gjt.sp.jedit.gui;

//{{{ Imports
import javax.swing.*;
import java.awt.event.*;
import java.util.Vector;
import org.gjt.sp.jedit.browser.FileCellRenderer;
import org.gjt.sp.jedit.io.VFSManager;
import org.gjt.sp.jedit.io.VFS;
import org.gjt.sp.jedit.*;
//}}}

public class RecentFilesMenu extends EnhancedMenu
{
	//{{{ RecentFilesMenu constructor
	public RecentFilesMenu()
	{
		super("recent-files");
	} //}}}

	//{{{ setPopupMenuVisible() method
	public void setPopupMenuVisible(boolean b)
	{
		if(b)
		{
			final View view = EditAction.getView(this);

			if(getMenuComponentCount() != 0)
				removeAll();

			//{{{ ActionListener...
			ActionListener actionListener = new ActionListener()
			{
				public void actionPerformed(ActionEvent evt)
				{
					jEdit.openFile(view,evt.getActionCommand());
					view.getStatus().setMessage(null);
				}
			}; //}}}

			//{{{ MouseListener...
			MouseListener mouseListener = new MouseAdapter()
			{
				public void mouseEntered(MouseEvent evt)
				{
					view.getStatus().setMessage(
						((JMenuItem)evt.getSource())
						.getActionCommand());
				}

				public void mouseExited(MouseEvent evt)
				{
					view.getStatus().setMessage(null);
				}
			}; //}}}

			Vector recentVector = BufferHistory.getBufferHistory();

			if(recentVector.size() == 0)
			{
				add(GUIUtilities.loadMenuItem("no-recent-files"));
				super.setPopupMenuVisible(b);
				return;
			}

			Vector menuItems = new Vector();
			boolean sort = jEdit.getBooleanProperty("sortRecent");

			/*
			 * While recentVector has 50 entries or so, we only display
			 * a few of those in the menu (otherwise it will be way too
			 * long)
			 */
			int recentFileCount = Math.min(recentVector.size(),
				jEdit.getIntegerProperty("history",25));

			for(int i = recentVector.size() - 1;
				i >= recentVector.size() - recentFileCount;
				i--)
			{
				String path = ((BufferHistory.Entry)recentVector
					.elementAt(i)).path;
				VFS vfs = VFSManager.getVFSForPath(path);
				JMenuItem menuItem = new JMenuItem(vfs.getFileName(path));
				menuItem.setActionCommand(path);
				menuItem.addActionListener(actionListener);
				menuItem.addMouseListener(mouseListener);
				menuItem.setIcon(FileCellRenderer.fileIcon);

				if(sort)
					menuItems.addElement(menuItem);
				else
					add(menuItem);
			}

			if(sort)
			{
				MiscUtilities.quicksort(menuItems,
					new MiscUtilities.MenuItemCompare());
				for(int i = 0; i < menuItems.size(); i++)
				{
					add((JMenuItem)menuItems.elementAt(i));
				}
			}
		}

		super.setPopupMenuVisible(b);
	} //}}}
}