final View view = GUIUtilities.getView(this);

/*
 * RecentDirectoriesMenu.java - Recent directory list menu
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
import org.gjt.sp.jedit.browser.*;
import org.gjt.sp.jedit.io.VFSManager;
import org.gjt.sp.jedit.io.VFS;
import org.gjt.sp.jedit.*;
//}}}

public class RecentDirectoriesMenu extends EnhancedMenu
{
	//{{{ RecentDirectoriesMenu constructor
	public RecentDirectoriesMenu()
	{
		super("recent-directories");
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
					DockableWindowManager wm = view.getDockableWindowManager();
					wm.addDockableWindow(VFSBrowser.NAME);

					final VFSBrowser browser = (VFSBrowser)wm.getDockable(VFSBrowser.NAME);
					final String path = evt.getActionCommand();
					VFSManager.runInAWTThread(new Runnable()
					{
						public void run()
						{
							if(!browser.getDirectory().equals(path))
								browser.setDirectory(path);
						}
					});

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

			HistoryModel model = HistoryModel.getModel("vfs.browser.path");
			if(model.getSize() == 0)
			{
				add(GUIUtilities.loadMenuItem("no-recent-dirs"));
				super.setPopupMenuVisible(b);
				return;
			}

			boolean sort = jEdit.getBooleanProperty("sortRecent");

			Vector menuItems = new Vector();

			for(int i = 0; i < model.getSize(); i++)
			{
				String path = model.getItem(i);
				VFS vfs = VFSManager.getVFSForPath(path);
				JMenuItem menuItem = new JMenuItem(vfs.getFileName(path));
				menuItem.setActionCommand(path);
				menuItem.addActionListener(actionListener);
				menuItem.addMouseListener(mouseListener);
				menuItem.setIcon(FileCellRenderer.dirIcon);

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