return "./" + name.toLowerCase() + "/" + version;

/*
 * OperatingSystem.java
 *
 * Originally written by Slava Pestov for the jEdit installer project. This work
 * has been placed into the public domain. You may use this work in any way and
 * for any purpose you wish.
 *
 * THIS SOFTWARE IS PROVIDED AS-IS WITHOUT WARRANTY OF ANY KIND, NOT EVEN THE
 * IMPLIED WARRANTY OF MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE, ASSUMES
 * _NO_ RESPONSIBILITY FOR ANY CONSEQUENCE RESULTING FROM THE USE, MODIFICATION,
 * OR REDISTRIBUTION OF THIS SOFTWARE.
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

	public abstract static class OSTask
	{
		protected Install installer;
		protected String name;
		protected String label;
		protected String directory;
		protected boolean enabled;

		public OSTask(Install installer, String name)
		{
			this.installer = installer;
			this.name = name;
			this.label = installer.getProperty("ostask." + name + ".label");
			this.directory = getDefaultDirectory(installer);

			// on by default
			enabled = true;
		}

		public String getName()
		{
			return name;
		}

		public String getLabel()
		{
			return label;
		}

		public String getDefaultDirectory(Install installer)
		{
			return null;
		}

		public String getDirectory()
		{
			return directory;
		}

		public boolean isEnabled()
		{
			return enabled;
		}

		public void setEnabled(boolean enabled)
		{
			this.enabled = enabled;
		}

		public void setDirectory(String directory)
		{
			this.directory = directory;
		}

		public abstract void perform(String installDir) throws IOException;
	}

	public OSTask[] getOSTasks(Install installer)
	{
		return new OSTask[0];
	}

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

		if(System.getProperty("mrj.version") != null)
			os = new MacOS();
		else
		{
			String osName = System.getProperty("os.name");
			if(osName.indexOf("Windows") != -1)
				os = new Windows();
			else if(osName.indexOf("OS/2") != -1)
				os = new HalfAnOS();
			else if(osName.indexOf("VMS") != -1)
				os = new VMS();
			else
				os = new Unix();
		}

		return os;
	}

	public static class Unix extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			String dir = "/usr/local/share/";
			if(!new File(dir).canWrite())
				dir = System.getProperty("user.home");

			return new File(dir,name.toLowerCase() + "/" + version).getPath();
		}

		public class ScriptOSTask extends OSTask
		{
			public ScriptOSTask(Install installer)
			{
				super(installer,"unix-script");
			}

			public String getDefaultDirectory(Install installer)
			{
				String dir = "/usr/local/";
				if(!new File(dir).canWrite())
					dir = System.getProperty("user.home");

				return new File(dir,"bin").getPath();
			}

			public void perform(String installDir) throws IOException
			{
				if(!enabled)
					return;

				mkdirs(directory);

				String name = installer.getProperty("app.name");

				// create app start script
				String script = directory + File.separatorChar
					+ name.toLowerCase();

				// Delete existing copy
				new File(script).delete();

				// Write simple script
				FileWriter out = new FileWriter(script);
				out.write("#!/bin/sh\n");
				out.write("# Java heap size, in megabytes\n");
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
		}

		public class ManPageOSTask extends OSTask
		{
			public ManPageOSTask(Install installer)
			{
				super(installer,"unix-man");
			}

			public String getDefaultDirectory(Install installer)
			{
				String dir = "/usr/local/";
				if(!new File(dir).canWrite())
					dir = System.getProperty("user.home");

				return new File(dir,"man/man1").getPath();
			}

			public void perform(String installDir) throws IOException
			{
				if(!enabled)
					return;

				mkdirs(directory);

				String name = installer.getProperty("app.name");

				// install man page
				String manpage = installer.getProperty("ostask.unix-man.manpage");

				InputStream in = getClass().getResourceAsStream("/" + manpage);
				installer.copy(in,new File(directory,manpage).getPath(),
					null);
			}
		}

		public OSTask[] getOSTasks(Install installer)
		{
			return new OSTask[] { new ScriptOSTask(installer),
				new ManPageOSTask(installer) };
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

	public static class MacOS extends Unix
	{
		public String getInstallDirectory(String name, String version)
		{
			return "/Applications/" + name + " " + version;
		}
	}

	public static class Windows extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "C:\\Program Files\\" + name + " " + version;
		}

		public class JEditLauncherOSTask extends OSTask
		{
			public JEditLauncherOSTask(Install installer)
			{
				super(installer,"jedit-launcher");
			}

			public String getDefaultDirectory(Install installer)
			{
				return null;
			}

			public void perform(String installDir)
			{
				if(!enabled)
					return;

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

		public OSTask[] getOSTasks(Install installer)
		{
			return new OSTask[] { new JEditLauncherOSTask(installer) };
		}
	}

	public static class HalfAnOS extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "C:\\" + name + " " + version;
		}
	}

	public static class VMS extends OperatingSystem
	{
		public String getInstallDirectory(String name, String version)
		{
			return "./" + name.toLowerCase() + "/" + version);
		}
	}

	// private members
	private static OperatingSystem os;
}