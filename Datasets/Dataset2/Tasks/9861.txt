if(OperatingSystem.isDOSDerived() || OperatingSystem.isMacOS())

/*
 * SettingsReloader.java - Utility class reloads macros and modes when necessary
 * Copyright (C) 2001 Slava Pestov
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

import java.io.File;
import org.gjt.sp.jedit.msg.VFSUpdate;

class SettingsReloader implements EBComponent
{
	public void handleMessage(EBMessage msg)
	{
		if(msg instanceof VFSUpdate)
		{
			VFSUpdate vmsg = (VFSUpdate)msg;
			maybeReload(vmsg.getPath());
		}
	}

	private void maybeReload(String path)
	{
		String jEditHome = jEdit.getJEditHome();
		String settingsDirectory = jEdit.getSettingsDirectory();
		String osName = System.getProperty("os.name");
		// On Windows and MacOS, path names are case insensitive
		if(osName.indexOf("Windows") != -1 || osName.indexOf("Mac") != -1)
		{
			path = path.toLowerCase();
			if(jEditHome != null)
				jEditHome = jEditHome.toLowerCase();
			if(settingsDirectory != null)
				settingsDirectory = settingsDirectory.toLowerCase();
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
		else if(path.endsWith(".xml") || path.endsWith("modes" + File.separator + "catalog"))
			jEdit.reloadModes();
	}
}