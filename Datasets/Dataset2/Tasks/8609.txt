out.write("# Java heap size, in megabytes\n");

/*
 * OperatingSystem.java
 * Copyright (C) 1999, 2000, 2001 Slava Pestov
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

package installer;

import java.io.*;

/*
 * Abstracts away operating-specific stuff, like finding out the installation
 * directory, creating a shortcut to start to program, and such.
 */
public abstract class OperatingSystem
{
	public abstract String getInstallDirectory(String name, String version);

	public String getShortcutDirectory(String name, String version)
	{
		return null;
	}

	public void createScript(Install installer, String installDir,
		String binDir, String name) throws IOException {}

	public void mkdirs(String directory) throws IOException
	{
		File file = new File(directory);
		if(!file.exists())
			file.mkdirs();
	}

	public static OperatingSystem getOperatingSystem()
	{
		if(os != null)
			return os;

		String osName = System.getProperty("os.name");
		if(osName.indexOf("Windows") != -1)
			os = new Windows();
		else if(osName.indexOf("Mac") != -1)
			os = new MacOS();
		else if(osName.indexOf("OS/2") != -1)
			os = new HalfAnOS();
		else
			os = new Unix();

		return os;
	}

	public static class MacOS extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "/Applications/" + name + " " + version;
		}
	}

	public static class Unix extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "/usr/local/share/" + name.toLowerCase()
				+ "/" + version;
		}

		public String getShortcutDirectory(String name, String version)
		{
			return "/usr/local/bin";
		}

		public void createScript(Install installer,
			String installDir, String binDir, String name)
			throws IOException
		{
			// create app start script
			String script = binDir + File.separatorChar
				+ name.toLowerCase();

			// Delete existing copy
			new File(script).delete();

			// Write simple script
			FileWriter out = new FileWriter(script);
			out.write("#!/bin/sh\n");
			out.write("# Java heap size, in megabytes (see doc/README.txt)\n");
			out.write("JAVA_HEAP_SIZE=32\n");
			out.write("exec "
				+ System.getProperty("java.home")
				+ "/bin/java -mx${JAVA_HEAP_SIZE}m ${"
				+ name.toUpperCase() + "} ");

			String jar = installDir + File.separator
				+ name.toLowerCase() + ".jar";

			out.write("-jar \"" + jar + "\" $@\n");

			out.close();

			// Make it executable
			String[] chmodArgs = { "chmod", "755", script };
			exec(chmodArgs);
		}

		public void mkdirs(String directory) throws IOException
		{
			File file = new File(directory);
			if(!file.exists())
			{
				String[] mkdirArgs = { "mkdir", "-m", "755",
					"-p", directory };
				exec(mkdirArgs);
			}
		}

		public void exec(String[] args) throws IOException
		{
			Process proc = Runtime.getRuntime().exec(args);
			proc.getInputStream().close();
			proc.getOutputStream().close();
			proc.getErrorStream().close();
			try
			{
				proc.waitFor();
			}
			catch(InterruptedException ie)
			{
			}
		}
	}

	public static class Windows extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "C:\\Program Files\\" + name + " " + version;
		}

		public void createScript(Install installer,
			String installDir, String binDir, String name)
			throws IOException
		{
			// run jEditLauncher installation
			File executable = new File(installDir,"jedit.exe");
			if(!executable.exists())
				return;

			String[] args = { executable.getPath(), "/i",
				System.getProperty("java.home")
				+ File.separator
				+ "bin" };

			try
			{
				Runtime.getRuntime().exec(args).waitFor();
			}
			catch(IOException io)
			{
			}
			catch(InterruptedException ie)
			{
			}
		}
	}

	public static class HalfAnOS extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "C:\\" + name + " " + version;
		}
	}

	// private members
	private static OperatingSystem os;
}