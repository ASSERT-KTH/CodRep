int newSize = Math.max(1,jEdit.getIntegerProperty("history",25));

/*
 * KillRing.java - Stores deleted text
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2003 Slava Pestov
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

package org.gjt.sp.jedit.buffer;

import com.microstar.xml.*;
import javax.swing.event.ListDataListener;
import javax.swing.ListModel;
import java.io.*;
import java.util.*;
import org.gjt.sp.jedit.*;
import org.gjt.sp.util.Log;

public class KillRing
{
	//{{{ propertiesChanged() method
	public static void propertiesChanged()
	{
		int newSize = jEdit.getIntegerProperty("history",25);
		if(ring == null)
			ring = new UndoManager.Remove[newSize];
		else if(newSize != ring.length)
		{
			UndoManager.Remove[] newRing = new UndoManager.Remove[
				newSize];
			ListModel model = new RingListModel();
			int newCount = Math.min(model.getSize(),newSize);
			for(int i = 0; i < newCount; i++)
			{
				newRing[i] = (UndoManager.Remove)
					model.getElementAt(i);
			}
			ring = newRing;
			count = newCount;
			wrap = false;
		}
		else if(count == ring.length)
		{
			count = 0;
			wrap = true;
		}
	} //}}}

	//{{{ getListModel() method
	public static ListModel getListModel()
	{
		return new RingListModel();
	} //}}}

	//{{{ load() method
	public static void load()
	{
		String settingsDirectory = jEdit.getSettingsDirectory();
		if(settingsDirectory == null)
			return;

		File killRing = new File(MiscUtilities.constructPath(
			settingsDirectory,"killring.xml"));
		if(!killRing.exists())
			return;

		killRingModTime = killRing.lastModified();
		Log.log(Log.MESSAGE,KillRing.class,"Loading killring.xml");

		KillRingHandler handler = new KillRingHandler();
		XmlParser parser = new XmlParser();
		Reader in = null;
		parser.setHandler(handler);
		try
		{
			in = new BufferedReader(new FileReader(killRing));
			parser.parse(null, null, in);
		}
		catch(XmlException xe)
		{
			int line = xe.getLine();
			String message = xe.getMessage();
			Log.log(Log.ERROR,KillRing.class,killRing + ":" + line
				+ ": " + message);
		}
		catch(FileNotFoundException fnf)
		{
			//Log.log(Log.DEBUG,BufferHistory.class,fnf);
		}
		catch(Exception e)
		{
			Log.log(Log.ERROR,KillRing.class,e);
		}
		finally
		{
			try
			{
				if(in != null)
					in.close();
			}
			catch(IOException io)
			{
				Log.log(Log.ERROR,KillRing.class,io);
			}
		}

		ring = (UndoManager.Remove[])handler.list.toArray(
			new UndoManager.Remove[handler.list.size()]);
		count = ring.length;
	} //}}}

	//{{{ save() method
	public static void save()
	{
		String settingsDirectory = jEdit.getSettingsDirectory();
		if(settingsDirectory == null)
			return;

		File file1 = new File(MiscUtilities.constructPath(
			settingsDirectory, "#killring.xml#save#"));
		File file2 = new File(MiscUtilities.constructPath(
			settingsDirectory, "killring.xml"));
		if(file2.exists() && file2.lastModified() != killRingModTime)
		{
			Log.log(Log.WARNING,KillRing.class,file2
				+ " changed on disk; will not save recent"
				+ " files");
			return;
		}

		jEdit.backupSettingsFile(file2);

		Log.log(Log.MESSAGE,KillRing.class,"Saving killring.xml");

		String lineSep = System.getProperty("line.separator");

		BufferedWriter out = null;

		try
		{
			out = new BufferedWriter(new FileWriter(file1));

			out.write("<?xml version=\"1.0\"?>");
			out.write(lineSep);
			out.write("<!DOCTYPE KILLRING SYSTEM \"killring.dtd\">");
			out.write(lineSep);
			out.write("<KILLRING>");
			out.write(lineSep);

			ListModel model = getListModel();
			int size = model.getSize();
			for(int i = size - 1; i >=0; i--)
			{
				out.write("<ENTRY>");
				out.write(MiscUtilities.charsToEntities(
					model.getElementAt(i).toString()));
				out.write("</ENTRY>");
				out.write(lineSep);
			}

			out.write("</KILLRING>");
			out.write(lineSep);

			out.close();

			/* to avoid data loss, only do this if the above
			 * completed successfully */
			file2.delete();
			file1.renameTo(file2);
		}
		catch(Exception e)
		{
			Log.log(Log.ERROR,KillRing.class,e);
		}
		finally
		{
			try
			{
				if(out != null)
					out.close();
			}
			catch(IOException e)
			{
			}
		}

		killRingModTime = file2.lastModified();
	} //}}}

	//{{{ Package-private members
	static UndoManager.Remove[] ring;
	static int count;
	static boolean wrap;

	//{{{ changed() method
	static void changed(UndoManager.Remove rem)
	{
		if(rem.inKillRing)
		{
			// compare existing entries' hashcode with this
			int length = (wrap ? ring.length : count);
			int kill = -1;

			for(int i = 0; i < length; i++)
			{
				if(ring[i] != rem
					&& ring[i].hashcode == rem.hashcode
					&& ring[i].str.equals(rem.str))
				{
					// we don't want duplicate
					// entries in the kill ring
					kill = i;
					break;
				}
			}

			if(kill != -1)
				remove(kill);
		}
		else
			add(rem);
	} //}}}

	//{{{ add() method
	static void add(UndoManager.Remove rem)
	{
		// compare existing entries' hashcode with this
		int length = (wrap ? ring.length : count);
		for(int i = 0; i < length; i++)
		{
			if(ring[i].hashcode == rem.hashcode)
			{
				// strings might be equal!
				if(ring[i].str.equals(rem.str))
				{
					// we don't want duplicate entries
					// in the kill ring
					return;
				}
			}
		}

		// no duplicates, check for all-whitespace string
		boolean allWhitespace = true;
		for(int i = 0; i < rem.str.length(); i++)
		{
			if(!Character.isWhitespace(rem.str.charAt(i)))
			{
				allWhitespace = false;
				break;
			}
		}

		if(allWhitespace)
			return;

		rem.inKillRing = true;

		if(ring[count] != null)
			ring[count].inKillRing = false;

		ring[count] = rem;
		if(++count >= ring.length)
		{
			wrap = true;
			count = 0;
		}
	} //}}}

	//{{{ remove() method
	static void remove(int i)
	{
		if(wrap)
		{
			UndoManager.Remove[] newRing = new UndoManager.Remove[
				ring.length];
			int newCount = 0;
			for(int j = 0; j < ring.length; j++)
			{
				int index;
				if(j < count)
					index = count - j - 1;
				else
					index = count + ring.length - j - 1;

				if(i == index)
				{
					ring[index].inKillRing = false;
					continue;
				}

				newRing[newCount++] = ring[index];
			}
			ring = newRing;
			count = newCount;
			wrap = false;
		}
		else
		{
			System.arraycopy(ring,i + 1,ring,i,count - i - 1);
			count--;
		}
	} //}}}

	//}}}

	//{{{ Private members
	private static long killRingModTime;

	private KillRing() {}
	//}}}

	//{{{ RingListModel class
	static class RingListModel implements ListModel
	{
		public void addListDataListener(ListDataListener listener)
		{
		}

		public void removeListDataListener(ListDataListener listener)
		{
		}

		public Object getElementAt(int index)
		{
			UndoManager.Remove rem;

			if(wrap)
			{
				if(index < count)
					rem = ring[count - index - 1];
				else
					rem = ring[count + ring.length - index - 1];
			}
			else
				rem = ring[count - index - 1];

			return rem;
		}

		public int getSize()
		{
			if(wrap)
				return ring.length;
			else
				return count;
		}
	} //}}}

	//{{{ KillRingHandler class
	static class KillRingHandler extends HandlerBase
	{
		List list = new LinkedList();

		public Object resolveEntity(String publicId, String systemId)
		{
			if("killring.dtd".equals(systemId))
			{
				// this will result in a slight speed up, since we
				// don't need to read the DTD anyway, as AElfred is
				// non-validating
				return new StringReader("<!-- -->");
			}

			return null;
		}

		public void doctypeDecl(String name, String publicId,
			String systemId) throws Exception
		{
			if("KILLRING".equals(name))
				return;

			Log.log(Log.ERROR,this,"killring.xml: DOCTYPE must be KILLRING");
		}

		public void endElement(String name)
		{
			if(name.equals("ENTRY"))
			{
				list.add(new UndoManager.Remove(null,0,0,charData));
			}
		}

		public void charData(char[] ch, int start, int length)
		{
			charData = new String(ch,start,length);
		}

		private String charData;
	} //}}}
}