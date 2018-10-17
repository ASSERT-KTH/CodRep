return false;

/*
 * IndentAction.java
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

package org.gjt.sp.jedit.indent;

import org.gjt.sp.jedit.buffer.JEditBuffer;
import org.gjt.sp.jedit.MiscUtilities;
import org.gjt.sp.jedit.TextUtilities;

public interface IndentAction
{
	/**
	 * @param buffer The buffer
	 * @param line The line number that matched the rule; not necessarily
	 * the line being indented.
	 * @param oldIndent Original indent.
	 * @param newIndent The new indent -- ie, indent returned by previous
	 * indent action.
	 */
	public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
		int newIndent);

	/**
	 * @return true if the indent engine should keep processing after
	 * this rule.
	 */
	public boolean keepChecking();

	/**
	 * This handles the following Java code:
	 * if(something)
	 * { // no indentation on this line, even though previous matches a rule
	 */
	public class Collapse implements IndentAction
	{
		/**
		 * This does nothing; it is merely a sentinel for the
		 * <code>OpenBracketIndentRule</code>.
		 */
		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
			int newIndent)
		{
			return newIndent;
		}
		
		public boolean keepChecking()
		{
			return true;
		}
		
		public boolean equals(Object o)
		{
			return (o instanceof Collapse);
		}
	}

	public class Reset implements IndentAction
	{
		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
			int newIndent)
		{
			return oldIndent;
		}
		
		public boolean keepChecking()
		{
			return true;
		}
	}

	public class Increase implements IndentAction
	{
		private int amount;
		
		public Increase()
		{
			amount = 1;
		}
		
		public Increase(int amount)
		{
			this.amount = amount;
		}
		
		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
			int newIndent)
		{
			return newIndent + buffer.getIndentSize() * amount;
		}
		
		public boolean keepChecking()
		{
			return true;
		}
		
		public boolean equals(Object o)
		{
			if(o instanceof Increase)
				return ((Increase)o).amount == amount;
			else
				return false;
		}
	}

	public class Decrease implements IndentAction
	{
		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
			int newIndent)
		{
			return newIndent - buffer.getIndentSize();
		}
		
		public boolean keepChecking()
		{
			return true;
		}
	}

	public class AlignBracket implements IndentAction
	{
		private int line, offset;
		private int openBracketLine;
		private int openBracketColumn;
		private String openBracketLineText;
		private int extraIndent;

		public AlignBracket(JEditBuffer buffer, int line, int offset)
		{
			this.line = line;
			this.offset = offset;
			
			int openBracketIndex = TextUtilities.findMatchingBracket(
				buffer,this.line,this.offset);
			if(openBracketIndex == -1)
				openBracketLine = -1;
			else
			{
				openBracketLine = buffer.getLineOfOffset(openBracketIndex);
				openBracketColumn = openBracketIndex -
					buffer.getLineStartOffset(openBracketLine);
				openBracketLineText = buffer.getLineText(openBracketLine);
			}
		}

		public int getExtraIndent()
		{
			return extraIndent;
		}
		
		public void setExtraIndent(int extraIndent)
		{
			this.extraIndent = extraIndent;
		}
		
		public int getOpenBracketColumn()
		{
			return openBracketColumn;
		}
		
		public String getOpenBracketLine()
		{
			return openBracketLineText;
		}

		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
			int newIndent)
		{
			if(openBracketLineText == null)
				return newIndent;
			else
			{
				return MiscUtilities.getLeadingWhiteSpaceWidth(
					openBracketLineText,buffer.getTabSize())
					+ (extraIndent * buffer.getIndentSize());
			}
		}
		
		public boolean keepChecking()
		{
			return false;
		}
	}

	/**
	* @author Matthieu Casanova
	*/
	public class AlignOffset implements IndentAction
	{
		private int offset;
		
		public AlignOffset(int offset)
		{
			this.offset = offset;
		}

		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
			int newIndent)
		{
			return offset;
		}

		public boolean keepChecking()
		{
			return false;
		}
	}

	/**
	* Indent action used for deep indent.
	* @author Matthieu Casanova
	*/
	public class AlignParameter implements IndentAction
	{
		private int openParensColumn;
		private String openParensLineText;

		public AlignParameter(int openParensColumn, String openParensLineText)
		{
			this.openParensLineText = openParensLineText;
			this.openParensColumn = openParensColumn;
		}

		public int calculateIndent(JEditBuffer buffer, int line, int oldIndent,
				     int newIndent)
		{
			return openParensLineText == null ? newIndent : openParensColumn + 1;
		}

		public boolean keepChecking()
		{
			return true;
		}
	}
}