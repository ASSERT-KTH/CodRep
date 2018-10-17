rem = ring[ring.length + index - count];

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

import javax.swing.event.ListDataListener;
import javax.swing.ListModel;
import org.gjt.sp.jedit.jEdit;

public class KillRing
{
	//{{{ propertiesChanged() method
	public static void propertiesChanged()
	{
		UndoManager.Remove[] newRing = new UndoManager.Remove[
			jEdit.getIntegerProperty("history",25)];
		if(ring != null)
		{
			/* System.arraycopy(ring,0,newRing,0,
				Math.min(ring.length */
		}
		ring = newRing;
		//XXX
		count = 0;
		wrap = false;
	} //}}}

	//{{{ getListModel() method
	public static ListModel getListModel()
	{
		return new RingListModel();
	} //}}}

	//{{{ Package-private members
	static UndoManager.Remove[] ring;
	static int count;
	static boolean wrap;

	//{{{ add() method
	static void add(UndoManager.Remove rem)
	{
		ring[count] = rem;
		if(++count >= ring.length)
		{
			wrap = true;
			count = 0;
		}
	} //}}}

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
				if(index < ring.length - count)
					rem = ring[ring.length - index + count];
				else
					rem = ring[index + count];
			}
			else
				rem = ring[count - index];

			return rem.str;
		}

		public int getSize()
		{
			if(wrap)
				return ring.length;
			else
				return count;
		}
	} //}}}

	//}}}
}