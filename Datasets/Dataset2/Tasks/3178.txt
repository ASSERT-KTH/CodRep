if(path.startsWith(dir))

/*
 * SettingsReloader.java - Utility class reloads macros and modes when necessary
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2001, 2003 Slava Pestov
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

package org.gjt.sp.jedit;

//{{{ Imports
import java.io.File;
import org.gjt.sp.jedit.io.VFS;
import org.gjt.sp.jedit.io.VFSManager;
import org.gjt.sp.jedit.msg.VFSUpdate;
import org.gjt.sp.jedit.search.*;
//}}}

class SettingsReloader implements EBComponent
{
	//{{{ handleMessage() method
	public void handleMessage(EBMessage msg)
	{
		if(msg instanceof VFSUpdate)
		{
			VFSUpdate vmsg = (VFSUpdate)msg;
			maybeReload(vmsg.getPath());
		}
	} //}}}

	//{{{ maybeReload() method
	private void maybeReload(String path)
	{
		String jEditHome = jEdit.getJEditHome();
		String settingsDirectory = jEdit.getSettingsDirectory();

		if(!MiscUtilities.isURL(path))
			path = MiscUtilities.resolveSymlinks(path);

		// On Windows and MacOS, path names are case insensitive
		if((VFSManager.getVFSForPath(path).getCapabilities()
			& VFS.CASE_INSENSITIVE_CAP) != 0)
		{
			path = path.toLowerCase();
			jEditHome = jEditHome.toLowerCase();
			settingsDirectory = settingsDirectory.toLowerCase();
		}

		// XXX: does this really belong here?
		SearchFileSet fileset = SearchAndReplace.getSearchFileSet();
		if(fileset instanceof DirectoryListSet)
		{
			DirectoryListSet dirset = (DirectoryListSet)fileset;
			String dir = MiscUtilities.resolveSymlinks(
				dirset.getDirectory());
			if(path.startsWith(dirset.getDirectory()))
				dirset.invalidateCachedList();
		}

		if(jEditHome != null && path.startsWith(jEditHome))
			path = path.substring(jEditHome.length());
		else if(settingsDirectory != null && path.startsWith(settingsDirectory))
			path = path.substring(settingsDirectory.length());
		else
		{
			// not in settings directory or jEdit home directory.
			// no need to reload anything.
			return;
		}

		if(path.startsWith(File.separator) || path.startsWith("/"))
			path = path.substring(1);

		if(path.startsWith("macros"))
			Macros.loadMacros();
		else if(path.startsWith("modes") && (path.endsWith(".xml")
			|| path.endsWith("catalog")))
			jEdit.reloadModes();
	} //}}}
}