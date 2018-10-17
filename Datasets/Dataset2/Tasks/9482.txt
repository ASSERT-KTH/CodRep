for(int i = startLine + 1; i <= end; i++)

/*
 * Anchor.java - A base point for physical line <-> screen line conversion
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 2005 Slava Pestov
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

/**
 * A base point for physical line/screen line conversion.
 */
abstract class Anchor
{
	DisplayManager displayManager;
	JEditTextArea textArea;

	int physicalLine;
	int scrollLine;
	boolean callChanged;
	boolean callReset;

	//{{{ Anchor constructor
	Anchor(DisplayManager displayManager,
		JEditTextArea textArea)
	{
		this.displayManager = displayManager;
		this.textArea = textArea;
	} //}}}

	abstract void reset();
	abstract void changed();

	//{{{ toString() method
	public String toString()
	{
		return getClass().getName() + "[" + physicalLine + ","
			+ scrollLine + "]";
	} //}}}

	//{{{ contentInserted() method
	void contentInserted(int startLine, int numLines)
	{
		if(this.physicalLine >= startLine)
		{
			if(this.physicalLine != startLine)
				this.physicalLine += numLines;
			this.callChanged = true;
		}
	} //}}}

	//{{{ preContentRemoved() method
	void preContentRemoved(int startLine, int numLines)
	{
		if(this.physicalLine >= startLine)
		{
			if(this.physicalLine == startLine)
				this.callChanged = true;
			else
			{
				int end = Math.min(startLine + numLines,
					this.physicalLine);
				for(int i = startLine; i < end; i++)
				{
					//XXX
					if(displayManager.isLineVisible(i))
					{
						this.scrollLine -=
							displayManager
							.screenLineMgr
							.getScreenLineCount(i);
					}
				}
				this.physicalLine -= (end - startLine);
				this.callChanged = true;
			}
		}
	} //}}}
}