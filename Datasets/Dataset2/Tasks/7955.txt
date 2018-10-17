if(current.getItemCount() >= 20 && i != list.length - 1)

/*
 * CurrentDirectoryMenu.java - File list menu
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

import javax.swing.*;
import java.awt.event.*;
import java.io.File;
import org.gjt.sp.jedit.browser.*;
import org.gjt.sp.jedit.io.VFSManager;
import org.gjt.sp.jedit.*;

public class CurrentDirectoryMenu extends EnhancedMenu
{
	//{{{ CurrentDirectoryMenu constructor
	public CurrentDirectoryMenu()
	{
		super("current-directory");
	} //}}}

	//{{{ setPopupMenuVisible() method
	public void setPopupMenuVisible(boolean b)
	{
		if(b)
		{
			final View view = GUIUtilities.getView(this);

			if(getMenuComponentCount() != 0)
				removeAll();

			final String path = MiscUtilities.getParentOfPath(
				view.getBuffer().getPath());
			JMenuItem mi = new JMenuItem(path);
			mi.setIcon(FileCellRenderer.openDirIcon);

			//{{{ Directory action listener...
			mi.addActionListener(new ActionListener()
			{
				public void actionPerformed(ActionEvent evt)
				{
					VFSBrowser.browseDirectory(view,path);
				}
			}); //}}}

			add(mi);
			addSeparator();

			if(view.getBuffer().getFile() == null)
			{
				mi = new JMenuItem(jEdit.getProperty(
					"current-directory.not-local"));
				mi.setEnabled(false);
				add(mi);
				super.setPopupMenuVisible(b);
				return;
			}

			File dir = new File(path);

			JMenu current = this;

			//{{{ ActionListener class
			ActionListener listener = new ActionListener()
			{
				public void actionPerformed(ActionEvent evt)
				{
					jEdit.openFile(view,evt.getActionCommand());
				}
			}; //}}}

			// for filtering out backups
			String backupPrefix = jEdit.getProperty("backup.prefix");
			String backupSuffix = jEdit.getProperty("backup.suffix");

			String[] list = dir.list();
			if(list == null || list.length == 0)
			{
				mi = new JMenuItem(jEdit.getProperty(
					"current-directory.no-files"));
				mi.setEnabled(false);
				add(mi);
			}
			else
			{
				MiscUtilities.quicksort(list,
					new MiscUtilities.StringICaseCompare());
				for(int i = 0; i < list.length; i++)
				{
					String name = list[i];

					// skip marker files
					if(name.endsWith(".marks"))
						continue;

					// skip autosave files
					if(name.startsWith("#") && name.endsWith("#"))
						continue;

					// skip backup files
					if((backupPrefix.length() != 0
						&& name.startsWith(backupPrefix))
						|| (backupSuffix.length() != 0
						&& name.endsWith(backupSuffix)))
						continue;

					// skip directories
					File file = new File(path,name);
					if(file.isDirectory())
						continue;

					mi = new JMenuItem(name);
					mi.setActionCommand(file.getPath());
					mi.addActionListener(listener);
					mi.setIcon(FileCellRenderer.fileIcon);

					if(current.getItemCount() >= 20)
					{
						//current.addSeparator();
						JMenu newCurrent = new JMenu(
							jEdit.getProperty(
							"common.more"));
						current.add(newCurrent);
						current = newCurrent;
					}
					current.add(mi);
				}
			}

		}

		super.setPopupMenuVisible(b);
	} //}}}
}