array = new int[1000];

/*
 * IntegerArray.java - Automatically growing array of ints
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
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

package org.gjt.sp.util;

/**
 * A simple collection that stores integers and grows automatically.
 */
public class IntegerArray
{
	//{{{ IntegerArray constructor
	public IntegerArray()
	{
		array = new int[100];
	} //}}}

	//{{{ add() method
	public void add(int num)
	{
		if(len >= array.length)
		{
			int[] arrayN = new int[len * 2];
			System.arraycopy(array,0,arrayN,0,len);
			array = arrayN;
		}

		array[len++] = num;
	} //}}}

	//{{{ get() method
	public final int get(int index)
	{
		return array[index];
	} //}}}

	//{{{ getSize() method
	public final int getSize()
	{
		return len;
	} //}}}

	//{{{ setSize() method
	public final void setSize(int len)
	{
		this.len = len;
	} //}}}

	//{{{ clear() method
	public final void clear()
	{
		len = 0;
	} //}}}

	//{{{ Private members
	private int[] array;
	private int len;
	//}}}
}