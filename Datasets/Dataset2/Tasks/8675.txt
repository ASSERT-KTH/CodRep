JEditBuffer buffer = textArea.getBuffer();

/*
 * SelectionManager.java
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2004 Slava Pestov
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

package org.gjt.sp.jedit.textarea;

//{{{ Imports
import java.awt.*;
import java.awt.event.*;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.TooManyListenersException;
import java.util.TreeSet;
import javax.swing.*;
import javax.swing.border.*;
import javax.swing.event.*;
import javax.swing.plaf.metal.MetalLookAndFeel;
import javax.swing.text.Segment;
import org.gjt.sp.jedit.Buffer;
import org.gjt.sp.jedit.buffer.*;
import org.gjt.sp.jedit.syntax.*;
import org.gjt.sp.util.Log;
//}}}

class SelectionManager
{
	// this is package-private so that the painter can use it without
	// having to call getSelection() (which involves an array copy)
	List selection;

	//{{{ SelectionManager constructor
	SelectionManager(JEditTextArea textArea)
	{
		this.textArea = textArea;
		selection = new ArrayList();
	} //}}}

	//{{{ getSelectionCount() method
	/**
	 * Returns the number of selections. This can be used to test
	 * for the existence of selections.
	 */
	int getSelectionCount()
	{
		return selection.size();
	} //}}}

	//{{{ getSelection() method
	/**
	 * Returns the current selection.
	 * @since jEdit 3.2pre1
	 */
	public Selection[] getSelection()
	{
		return (Selection[])selection.toArray(
			new Selection[selection.size()]);
	} //}}}

	//{{{ setSelection() method
	/**
	 * Sets the selection. Nested and overlapping selections are merged
	 * where possible.
	 */
	void setSelection(Selection[] selection)
	{
		this.selection.clear();
		addToSelection(selection);
	} //}}}

	//{{{ addToSelection() method
	/**
	 * Adds to the selection. Nested and overlapping selections are merged
	 * where possible. Null elements of the array are ignored.
	 * @param selection The new selection
	 * since jEdit 3.2pre1
	 */
	void addToSelection(Selection[] selection)
	{
		if(selection != null)
		{
			for(int i = 0; i < selection.length; i++)
			{
				Selection s = selection[i];
				if(s != null)
					addToSelection(s);
			}
		}
	} //}}}

	//{{{ addToSelection() method
	void addToSelection(Selection addMe)
	{
		if(addMe.start > addMe.end)
		{
			throw new IllegalArgumentException(addMe.start
				+ " > " + addMe.end);
		}
		else if(addMe.start == addMe.end)
		{
			if(addMe instanceof Selection.Range)
				return;
			else if(addMe instanceof Selection.Rect)
			{
				if(((Selection.Rect)addMe).extraEndVirt == 0)
					return;
			}
		}

		Iterator iter = selection.iterator();
		while(iter.hasNext())
		{
			// try and merge existing selections one by
			// one with the new selection
			Selection s = (Selection)iter.next();
			if(s.overlaps(addMe))
			{
				addMe.start = Math.min(s.start,addMe.start);
				addMe.end = Math.max(s.end,addMe.end);
				iter.remove();
			}
		}

		addMe.startLine = textArea.getLineOfOffset(addMe.start);
		addMe.endLine = textArea.getLineOfOffset(addMe.end);

		boolean added = false;

		for(int i = 0; i < selection.size(); i++)
		{
			Selection s = (Selection)selection.get(i);
			if(addMe.start < s.start)
			{
				selection.add(i,addMe);
				added = true;
				break;
			}
		}

		if(!added)
			selection.add(addMe);

		textArea.invalidateLineRange(addMe.startLine,addMe.endLine);
	} //}}}

	//{{{ setSelection() method
	/**
	 * Sets the selection. Nested and overlapping selections are merged
	 * where possible.
	 */
	void setSelection(Selection selection)
	{
		this.selection.clear();

		if(selection != null)
			addToSelection(selection);
	} //}}}

	//{{{ getSelectionAtOffset() method
	/**
	 * Returns the selection containing the specific offset, or <code>null</code>
	 * if there is no selection at that offset.
	 * @param offset The offset
	 * @since jEdit 3.2pre1
	 */
	Selection getSelectionAtOffset(int offset)
	{
		if(selection != null)
		{
			Iterator iter = selection.iterator();
			while(iter.hasNext())
			{
				Selection s = (Selection)iter.next();
				if(offset >= s.start && offset <= s.end)
					return s;
			}
		}

		return null;
	} //}}}

	//{{{ removeFromSelection() method
	/**
	 * Deactivates the specified selection.
	 * @param sel The selection
	 */
	void removeFromSelection(Selection sel)
	{
		selection.remove(sel);
	} //}}}

	//{{{ resizeSelection() method
	/**
	 * Resizes the selection at the specified offset, or creates a new
	 * one if there is no selection at the specified offset. This is a
	 * utility method that is mainly useful in the mouse event handler
	 * because it handles the case of end being before offset gracefully
	 * (unlike the rest of the selection API).
	 * @param offset The offset
	 * @param end The new selection end
	 * @param extraEndVirt Only for rectangular selections - specifies how
	 * far it extends into virtual space.
	 * @param rect Make the selection rectangular?
	 */
	void resizeSelection(int offset, int end, int extraEndVirt,
		boolean rect)
	{
		boolean reversed = false;
		if(end < offset)
		{
			int tmp = offset;
			offset = end;
			end = tmp;
			reversed = true;
		}

		Selection newSel;
		if(rect)
		{
			Selection.Rect rectSel = new Selection.Rect(offset,end);
			if(reversed)
				rectSel.extraStartVirt = extraEndVirt;
			else
				rectSel.extraEndVirt = extraEndVirt;
			newSel = rectSel;
		}
		else
			newSel = new Selection.Range(offset,end);

		addToSelection(newSel);
	} //}}}

	//{{{ getSelectedLines() method
	/**
	 * Returns a sorted array of line numbers on which a selection or
	 * selections are present.<p>
	 *
	 * This method is the most convenient way to iterate through selected
	 * lines in a buffer. The line numbers in the array returned by this
	 * method can be passed as a parameter to such methods as
	 * {@link org.gjt.sp.jedit.Buffer#getLineText(int)}.
	 */
	int[] getSelectedLines()
	{
		Integer line;

		Set set = new TreeSet();
		Iterator iter = selection.iterator();
		while(iter.hasNext())
		{
			Selection s = (Selection)iter.next();
			int endLine =
				(s.end == textArea.getLineStartOffset(s.endLine)
				? s.endLine - 1
				: s.endLine);

			for(int j = s.startLine; j <= endLine; j++)
			{
				line = new Integer(j);
				set.add(line);
			}
		}

		int[] returnValue = new int[set.size()];
		int i = 0;

		iter = set.iterator();
		while(iter.hasNext())
		{
			line = (Integer)iter.next();
			returnValue[i++] = line.intValue();
		}

		return returnValue;
	} //}}}
	
	//{{{ invertSelection() method
	void invertSelection()
	{
		Selection[] newSelection = new Selection[selection.size() + 1];
		int lastOffset = 0;
		for(int i = 0; i < selection.size(); i++)
		{
			Selection s = (Selection)selection.get(i);
			newSelection[i] = new Selection.Range(lastOffset,
				s.getStart());
			lastOffset = s.getEnd();
		}
		newSelection[selection.size()] = new Selection.Range(
			lastOffset,textArea.getBufferLength());
		setSelection(newSelection);
	} //}}}

	//{{{ getSelectionStartEndOnLine() method
	/**
	 * Returns the x co-ordinates of the selection start and end on the
	 * given line. May return null.
	 */
	int[] getSelectionStartAndEnd(int screenLine, int physicalLine,
		Selection s)
	{
		int start = textArea.getScreenLineStartOffset(screenLine);
		int end = textArea.getScreenLineEndOffset(screenLine);

		if(end <= s.start || start > s.end)
			return null;

		int selStartScreenLine;
		if(textArea.displayManager.isLineVisible(s.startLine))
			selStartScreenLine = textArea.getScreenLineOfOffset(s.start);
		else
			selStartScreenLine = -1;

		int selEndScreenLine;
		if(textArea.displayManager.isLineVisible(s.endLine))
			selEndScreenLine = textArea.getScreenLineOfOffset(s.end);
		else
			selEndScreenLine = -1;

		Buffer buffer = textArea.getBuffer();

		int lineStart = buffer.getLineStartOffset(physicalLine);
		int x1, x2;

		if(s instanceof Selection.Rect)
		{
			start -= lineStart;
			end -= lineStart;

			Selection.Rect rect = (Selection.Rect)s;
			int _start = rect.getStartColumn(buffer);
			int _end = rect.getEndColumn(buffer);

			int lineLen = buffer.getLineLength(physicalLine);

			int[] total = new int[1];

			int rectStart = buffer.getOffsetOfVirtualColumn(
				physicalLine,_start,total);
			if(rectStart == -1)
			{
				x1 = (_start - total[0]) * textArea.charWidth;
				rectStart = lineLen;
			}
			else
				x1 = 0;

			int rectEnd = buffer.getOffsetOfVirtualColumn(
				physicalLine,_end,total);
			if(rectEnd == -1)
			{
				x2 = (_end - total[0]) * textArea.charWidth;
				rectEnd = lineLen;
			}
			else
				x2 = 0;

			if(end <= rectStart || start > rectEnd)
				return null;

			x1 = (rectStart < start ? 0
				: x1 + textArea.offsetToXY(physicalLine,
				rectStart).x);
			x2 = (rectEnd > end ? textArea.getWidth()
				: x2 + textArea.offsetToXY(physicalLine,
				rectEnd).x);
		}
		else if(selStartScreenLine == selEndScreenLine
			&& selStartScreenLine != -1)
		{
			x1 = textArea.offsetToXY(physicalLine,
				s.start - lineStart).x;
			x2 = textArea.offsetToXY(physicalLine,
				s.end - lineStart).x;
		}
		else if(screenLine == selStartScreenLine)
		{
			x1 = textArea.offsetToXY(physicalLine,
				s.start - lineStart).x;
			x2 = textArea.getWidth();
		}
		else if(screenLine == selEndScreenLine)
		{
			x1 = 0;
			x2 = textArea.offsetToXY(physicalLine,
				s.end - lineStart).x;
		}
		else
		{
			x1 = 0;
			x2 = textArea.getWidth();
		}

		if(x1 < 0)
			x1 = 0;
		if(x2 < 0)
			x2 = 0;

		if(x1 == x2)
			x2++;

		return new int[] { x1, x2 };
	} //}}}

	//{{{ insideSelection() method
	/**
	 * Returns if the given point is inside a selection.
	 * Used by drag and drop code in MouseHandler below.
	 */
	boolean insideSelection(int x, int y)
	{
		int offset = textArea.xyToOffset(x,y);

		Selection s = textArea.getSelectionAtOffset(offset);
		if(s == null)
			return false;

		int screenLine = textArea.getScreenLineOfOffset(offset);
		if(screenLine == -1)
			return false;

		int[] selectionStartAndEnd = getSelectionStartAndEnd(
			screenLine,textArea.getLineOfOffset(offset),s);
		if(selectionStartAndEnd == null)
			return false;

		return x >= selectionStartAndEnd[0]
			&& x <= selectionStartAndEnd[1];
	} //}}}

	private JEditTextArea textArea;
}