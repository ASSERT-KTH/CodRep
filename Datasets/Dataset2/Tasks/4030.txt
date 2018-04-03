textArea.updateScrollBar();

/*
 * FirstLine.java
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

import org.gjt.sp.jedit.Debug;
import org.gjt.sp.util.Log;

class FirstLine extends Anchor
{
	int skew;

	//{{{ FirstLine constructor
	FirstLine(DisplayManager displayManager,
		JEditTextArea textArea)
	{
		super(displayManager,textArea);
	} //}}}

	//{{{ changed() method
	public void changed()
	{
		//{{{ Debug code
		if(Debug.SCROLL_DEBUG)
		{
			Log.log(Log.DEBUG,this,"changed() before: "
				+ physicalLine + ":" + scrollLine
				+ ":" + skew);
		} //}}}

		ensurePhysicalLineIsVisible();

		int screenLines = displayManager
			.getScreenLineCount(physicalLine);
		if(skew >= screenLines)
			skew = screenLines - 1;

		//{{{ Debug code
		if(Debug.SCROLL_VERIFY)
		{
			System.err.println("SCROLL_VERIFY");
			int verifyScrollLine = 0;

			for(int i = 0; i < displayManager.getBuffer()
				.getLineCount(); i++)
			{
				if(!displayManager.isLineVisible(i))
					continue;

				if(i >= physicalLine)
					break;

				verifyScrollLine += displayManager
					.getScreenLineCount(i);
			}

			if(verifyScrollLine != scrollLine)
			{
				Exception ex = new Exception(scrollLine + ":" + verifyScrollLine);
				Log.log(Log.ERROR,this,ex);
			}
		}

		if(Debug.SCROLL_DEBUG)
		{
			Log.log(Log.DEBUG,this,"changed() after: "
				+ physicalLine + ":" + scrollLine
				+ ":" + skew);
		} //}}}
	} //}}}

	//{{{ reset() method
	public void reset()
	{
		if(Debug.SCROLL_DEBUG)
			Log.log(Log.DEBUG,this,"reset()");

		int oldPhysicalLine = physicalLine;
		physicalLine = 0;
		scrollLine = 0;

		int i = displayManager.getFirstVisibleLine();

		for(;;)
		{
			if(i >= oldPhysicalLine)
				break;

			int before = scrollLine;
			displayManager.updateScreenLineCount(i);
			if(before != scrollLine)
				throw new RuntimeException(this + " nudged");
			scrollLine += displayManager.getScreenLineCount(i);

			int nextLine = displayManager.getNextVisibleLine(i);
			if(nextLine == -1)
				break;
			else
				i = nextLine;
		}

		physicalLine = i;

		displayManager.updateScreenLineCount(i);
		int screenLines = displayManager.getScreenLineCount(physicalLine);
		if(skew >= screenLines)
			skew = screenLines - 1;

		textArea.updateScrollBars();
	} //}}}

	//{{{ physDown() method
	// scroll down by physical line amount
	void physDown(int amount, int screenAmount)
	{
		if(Debug.SCROLL_DEBUG)
		{
			Log.log(Log.DEBUG,this,"physDown() start: "
				+ physicalLine + ":" + scrollLine);
		}

		skew = 0;

		if(!displayManager.isLineVisible(physicalLine))
		{
			int lastVisibleLine = displayManager.getLastVisibleLine();
			if(physicalLine > lastVisibleLine)
				physicalLine = lastVisibleLine;
			else
			{
				int nextPhysicalLine = displayManager.getNextVisibleLine(physicalLine);
				amount -= (nextPhysicalLine - physicalLine);
				scrollLine += displayManager.getScreenLineCount(physicalLine);
				physicalLine = nextPhysicalLine;
			}
		}

		for(;;)
		{
			int nextPhysicalLine = displayManager.getNextVisibleLine(
				physicalLine);
			if(nextPhysicalLine == -1)
				break;
			else if(nextPhysicalLine > physicalLine + amount)
				break;
			else
			{
				scrollLine += displayManager.getScreenLineCount(physicalLine);
				amount -= (nextPhysicalLine - physicalLine);
				physicalLine = nextPhysicalLine;
			}
		}

		if(Debug.SCROLL_DEBUG)
		{
			Log.log(Log.DEBUG,this,"physDown() end: "
				+ physicalLine + ":" + scrollLine);
		}

		callChanged = true;

		// JEditTextArea.scrollTo() needs this to simplify
		// its code
		if(screenAmount < 0)
			scrollUp(-screenAmount);
		else if(screenAmount > 0)
			scrollDown(screenAmount);
	} //}}}

	//{{{ physUp() method
	// scroll up by physical line amount
	void physUp(int amount, int screenAmount)
	{
		if(Debug.SCROLL_DEBUG)
		{
			Log.log(Log.DEBUG,this,"physUp() start: "
				+ physicalLine + ":" + scrollLine);
		}

		skew = 0;

		if(!displayManager.isLineVisible(physicalLine))
		{
			int firstVisibleLine = displayManager.getFirstVisibleLine();
			if(physicalLine < firstVisibleLine)
				physicalLine = firstVisibleLine;
			else
			{
				int prevPhysicalLine = displayManager.getPrevVisibleLine(physicalLine);
				amount -= (physicalLine - prevPhysicalLine);
			}
		}

		for(;;)
		{
			int prevPhysicalLine = displayManager.getPrevVisibleLine(
				physicalLine);
			if(prevPhysicalLine == -1)
				break;
			else if(prevPhysicalLine < physicalLine - amount)
				break;
			else
			{
				amount -= (physicalLine - prevPhysicalLine);
				physicalLine = prevPhysicalLine;
				scrollLine -= displayManager.getScreenLineCount(
					prevPhysicalLine);
			}
		}

		if(Debug.SCROLL_DEBUG)
		{
			Log.log(Log.DEBUG,this,"physUp() end: "
				+ physicalLine + ":" + scrollLine);
		}

		callChanged = true;

		// JEditTextArea.scrollTo() needs this to simplify
		// its code
		if(screenAmount < 0)
			scrollUp(-screenAmount);
		else if(screenAmount > 0)
			scrollDown(screenAmount);
	} //}}}

	//{{{ scrollDown() method
	// scroll down by screen line amount
	void scrollDown(int amount)
	{
		if(Debug.SCROLL_DEBUG)
			Log.log(Log.DEBUG,this,"scrollDown()");

		ensurePhysicalLineIsVisible();

		amount += skew;

		skew = 0;

		while(amount > 0)
		{
			int screenLines = displayManager.getScreenLineCount(physicalLine);
			if(amount < screenLines)
			{
				skew = amount;
				break;
			}
			else
			{
				int nextLine = displayManager.getNextVisibleLine(physicalLine);
				if(nextLine == -1)
					break;
				boolean visible = displayManager.isLineVisible(physicalLine);
				physicalLine = nextLine;
				if(visible)
				{
					amount -= screenLines;
					scrollLine += screenLines;
				}
			}
		}

		callChanged = true;
	} //}}}

	//{{{ scrollUp() method
	// scroll up by screen line amount
	void scrollUp(int amount)
	{
		if(Debug.SCROLL_DEBUG)
			Log.log(Log.DEBUG,this,"scrollUp()");

		ensurePhysicalLineIsVisible();

		if(amount <= skew)
		{
			skew -= amount;
		}
		else
		{
			amount -= skew;
			skew = 0;

			while(amount > 0)
			{
				int prevLine = displayManager.getPrevVisibleLine(physicalLine);
				if(prevLine == -1)
					break;
				physicalLine = prevLine;

				int screenLines = displayManager.getScreenLineCount(physicalLine);
				scrollLine -= screenLines;
				if(amount < screenLines)
				{
					skew = screenLines - amount;
					break;
				}
				else
					amount -= screenLines;
			}
		}

		callChanged = true;
	} //}}}

	//{{{ ensurePhysicalLineIsVisible() method
	void ensurePhysicalLineIsVisible()
	{
		if(!displayManager.isLineVisible(physicalLine))
		{
			if(physicalLine > displayManager.getLastVisibleLine())
			{
				physicalLine = displayManager.getLastVisibleLine();
				scrollLine = displayManager.getScrollLineCount() - 1;
			}
			else if(physicalLine < displayManager.getFirstVisibleLine())
			{
				physicalLine = displayManager.getFirstVisibleLine();
				scrollLine = 0;
			}
			else
			{
				physicalLine = displayManager.getNextVisibleLine(physicalLine);
				scrollLine += displayManager.getScreenLineCount(physicalLine);
			}
		}
	} //}}}
}