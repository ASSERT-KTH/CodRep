catch(Exception e)

/*
 * Roster.java - A list of things to do, used in various places
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

package org.gjt.sp.jedit.pluginmgr;

//{{{ Imports
import javax.swing.SwingUtilities;
import java.io.*;
import java.net.*;
import java.util.zip.*;
import java.util.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;
//}}}

class Roster
{
	//{{{ Roster constructor
	Roster()
	{
		operations = new ArrayList();
		toLoad = new ArrayList();
	} //}}}

	//{{{ addRemove() method
	void addRemove(String plugin)
	{
		addOperation(new Remove(plugin));
	} //}}}

	//{{{ addInstall() method
	void addInstall(String url, String installDirectory, int size)
	{
		addOperation(new Install(url,installDirectory,size));
	} //}}}

	//{{{ getOperation() method
	public Operation getOperation(int i)
	{
		return (Operation)operations.get(i);
	} //}}}

	//{{{ getOperationCount() method
	int getOperationCount()
	{
		return operations.size();
	} //}}}

	//{{{ isEmpty() method
	boolean isEmpty()
	{
		return operations.size() == 0;
	} //}}}

	//{{{ performOperations() method
	boolean performOperations(final PluginManagerProgress progress)
	{
		for(int i = 0; i < operations.size(); i++)
		{
			Operation op = (Operation)operations.get(i);
			if(op.runInWorkThread(progress))
				progress.done(true);
			else
			{
				progress.done(false);
				return false;
			}

			if(Thread.interrupted())
				return false;
		}

		try
		{
			SwingUtilities.invokeAndWait(new Runnable()
			{
				public void run()
				{
					for(int i = 0; i < operations.size(); i++)
					{
						Operation op = (Operation)
							operations.get(i);
						if(op.runInAWTThread(progress))
							progress.done(true);
						else
						{
							progress.done(false);
							return;
						}
					}

					finishOperations();
				}
			});
		}
		catch(InterruptedException e)
		{
			Log.log(Log.ERROR,this,e);
		}

		return true;
	} //}}}

	//{{{ Private members
	private static File downloadDir;

	private List operations;
	private List toLoad;

	//{{{ addOperation() method
	private void addOperation(Operation op)
	{
		for(int i = 0; i < operations.size(); i++)
		{
			if(operations.get(i).equals(op))
				return;
		}

		operations.add(op);
	} //}}}

	//{{{ getDownloadDir() method
	private static String getDownloadDir()
	{
		if(downloadDir == null)
		{
			String settings = jEdit.getSettingsDirectory();
			if(settings == null)
				settings = System.getProperty("user.home");
			downloadDir = new File(MiscUtilities.constructPath(
				settings,"PluginManager.download"));
			downloadDir.mkdirs();
		}

		return downloadDir.getPath();
	} //}}}

	//{{{ finishOperations() method
	private void finishOperations()
	{
		// add the JARs before checking deps since dep check might
		// require all JARs to be present
		for(int i = 0; i < toLoad.size(); i++)
		{
			String pluginName = (String)toLoad.get(i);
			if(jEdit.getPluginJAR(pluginName) != null)
			{
				Log.log(Log.WARNING,this,"Already loaded: "
					+ pluginName);
			}
			else
				jEdit.addPluginJAR(pluginName);
		}

		for(int i = 0; i < toLoad.size(); i++)
		{
			String pluginName = (String)toLoad.get(i);
			PluginJAR plugin = jEdit.getPluginJAR(pluginName);
			if(plugin != null)
				plugin.checkDependencies();
		}

		// now activate the plugins
		for(int i = 0; i < toLoad.size(); i++)
		{
			String pluginName = (String)toLoad.get(i);
			PluginJAR plugin = jEdit.getPluginJAR(pluginName);
			if(plugin != null)
				plugin.activatePluginIfNecessary();
		}
	} //}}}

	//}}}

	//{{{ Operation interface
	static abstract class Operation
	{
		public boolean runInWorkThread(PluginManagerProgress progress)
		{
			return true;
		}

		public boolean runInAWTThread(PluginManagerProgress progress)
		{
			return true;
		}

		public abstract int getMaximum();
	} //}}}

	//{{{ Remove class
	class Remove extends Operation
	{
		//{{{ Remove constructor
		Remove(String plugin)
		{
			this.plugin = plugin;
		} //}}}

		//{{{ getMaximum() method
		public int getMaximum()
		{
			return 1;
		} //}}}

		//{{{ runInAWTThread() method
		public boolean runInAWTThread(PluginManagerProgress progress)
		{
			// close JAR file and all JARs that depend on this
			PluginJAR jar = jEdit.getPluginJAR(plugin);
			if(jar != null)
			{
				unloadPluginJAR(jar);
				String cachePath = jar.getCachePath();
				if(cachePath != null)
					new File(cachePath).delete();
			}

			toLoad.remove(plugin);

			// remove cache file

			// move JAR first
			File jarFile = new File(plugin);
			File srcFile = new File(plugin.substring(0,plugin.length() - 4));

			boolean ok = true;
			Log.log(Log.NOTICE,this,"Deleting " + jarFile + " recursively");

			ok &= jarFile.delete();

			if(srcFile.exists())
				ok &= deleteRecursively(srcFile);

			String[] args = { plugin };
			if(!ok)
				GUIUtilities.error(progress,"plugin-manager.remove-failed",args);
			return ok;
		} //}}}

		//{{{ unloadPluginJAR() method
		/**
		 * This should go into a public method somewhere.
		 */
		private void unloadPluginJAR(PluginJAR jar)
		{
			String[] dependents = jar.getDependentPlugins();
			for(int i = 0; i < dependents.length; i++)
			{
				PluginJAR _jar = jEdit.getPluginJAR(
					dependents[i]);
				if(_jar != null)
				{
					toLoad.add(dependents[i]);
					unloadPluginJAR(_jar);
				}
			}

			jEdit.removePluginJAR(jar,false);
		} //}}}

		//{{{ equals() method
		public boolean equals(Object o)
		{
			if(o instanceof Remove
				&& ((Remove)o).plugin.equals(plugin))
				return true;
			else
				return false;
		} //}}}

		//{{{ Private members
		private String plugin;

		private boolean deleteRecursively(File file)
		{
			Log.log(Log.NOTICE,this,"Deleting " + file + " recursively");

			boolean ok = true;

			if(file.isDirectory())
			{
				String path = file.getPath();
				String[] children = file.list();
				for(int i = 0; i < children.length; i++)
				{
					ok &= deleteRecursively(new File(path,children[i]));
				}
			}

			ok &= file.delete();

			return ok;
		} //}}}
	} //}}}

	//{{{ Install class
	class Install extends Operation
	{
		int size;

		//{{{ Install constructor
		Install(String url, String installDirectory, int size)
		{
			// catch those hooligans passing null urls
			if(url == null)
				throw new NullPointerException();

			this.url = url;
			this.installDirectory = installDirectory;
			this.size = size;
		} //}}}

		//{{{ getMaximum() method
		public int getMaximum()
		{
			return size;
		} //}}}

		//{{{ runInWorkThread() method
		public boolean runInWorkThread(PluginManagerProgress progress)
		{
			String fileName = MiscUtilities.getFileName(url);
			progress.downloading(fileName);

			path = download(progress,fileName,url);
			if(path == null)
			{
				// interrupted download
				return false;
			}
			else
				return true;
		} //}}}

		//{{{ runInAWTThread() method
		public boolean runInAWTThread(PluginManagerProgress progress)
		{
			progress.installing(MiscUtilities.getFileName(path));

			ZipFile zipFile = null;

			try
			{
				zipFile = new ZipFile(path);

				Enumeration enum = zipFile.entries();
				while(enum.hasMoreElements())
				{
					ZipEntry entry = (ZipEntry)enum.nextElement();
					String name = entry.getName().replace('/',File.separatorChar);
					File file = new File(installDirectory,name);
					if(entry.isDirectory())
						file.mkdirs();
					else
					{
						new File(file.getParent()).mkdirs();
						copy(progress,zipFile.getInputStream(entry),
							new FileOutputStream(file),false,false);
						if(file.getName().toLowerCase().endsWith(".jar"))
							toLoad.add(file.getPath());
					}
				}
			}
			catch(InterruptedIOException iio)
			{
				// do nothing, user clicked 'Stop'
				return false;
			}
			catch(final IOException io)
			{
				Log.log(Log.ERROR,this,io);

				SwingUtilities.invokeLater(new Runnable()
				{
					public void run()
					{
						String[] args = { io.getMessage() };
						GUIUtilities.error(null,"ioerror",args);
					}
				});

				return false;
			}
			catch(Exception e)
			{
				Log.log(Log.ERROR,this,e);

				return false;
			}
			finally
			{
				try
				{
					if(zipFile != null)
						zipFile.close();
				}
				catch(IOException io)
				{
					Log.log(Log.ERROR,this,io);
				}

				if(jEdit.getBooleanProperty(
					"plugin-manager.deleteDownloads"))
				{
					new File(path).delete();
				}
			}

			progress.setValue(1);

			return true;
		} //}}}

		//{{{ equals() method
		public boolean equals(Object o)
		{
			if(o instanceof Install
				&& ((Install)o).url.equals(url))
			{
				/* even if installDirectory is different */
				return true;
			}
			else
				return false;
		} //}}}

		//{{{ Private members
		private String url;
		private String installDirectory;
		private String path;

		//{{{ download() method
		private String download(PluginManagerProgress progress,
			String fileName, String url)
		{
			try
			{
				URLConnection conn = new URL(url).openConnection();

				String path = MiscUtilities.constructPath(getDownloadDir(),fileName);

				if(!copy(progress,conn.getInputStream(),
					new FileOutputStream(path),true,true))
					return null;

				return path;
			}
			catch(InterruptedIOException iio)
			{
				// do nothing, user clicked 'Stop'
				return null;
			}
			catch(final IOException io)
			{
				Log.log(Log.ERROR,this,io);

				SwingUtilities.invokeLater(new Runnable()
				{
					public void run()
					{
						String[] args = { io.getMessage() };
						GUIUtilities.error(null,"ioerror",args);
					}
				});

				return null;
			}
			catch(Exception e)
			{
				Log.log(Log.ERROR,this,e);

				return null;
			}
		} //}}}

		//{{{ copy() method
		private boolean copy(PluginManagerProgress progress,
			InputStream in, OutputStream out, boolean canStop,
			boolean doProgress) throws Exception
		{
			in = new BufferedInputStream(in);
			out = new BufferedOutputStream(out);

			byte[] buf = new byte[4096];
			int copied = 0;
loop:			for(;;)
			{
				int count = in.read(buf,0,buf.length);
				if(count == -1)
					break loop;

				if(doProgress)
				{
					copied += count;
					progress.setValue(copied);
				}

				out.write(buf,0,count);
				if(canStop && Thread.interrupted())
				{
					in.close();
					out.close();
					return false;
				}
			}

			in.close();
			out.close();
			return true;
		} //}}}

		//}}}
	} //}}}
}