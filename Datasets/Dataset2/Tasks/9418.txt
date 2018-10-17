if(line.substring(i,i+3).equals("{{{")) /* }}} */

/*
 * BracketIndentRule.java
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

import gnu.regexp.*;
import org.gjt.sp.jedit.search.RESearchMatcher;
import org.gjt.sp.jedit.Buffer;

public abstract class BracketIndentRule implements IndentRule
{
	//{{{ BracketIndentRule constructor
	public BracketIndentRule(char openBracket, char closeBracket)
	{
		this.openBracket = openBracket;
		this.closeBracket = closeBracket;
	} //}}}

	//{{{ Brackets class
	public static class Brackets
	{
		int openCount;
		int closeCount;
	} //}}}

	//{{{ getBrackets() method
	public Brackets getBrackets(String line)
	{
		Brackets brackets = new Brackets();

		for(int i = 0; i < line.length(); i++)
		{
			char ch = line.charAt(i);
			if(ch == openBracket)
			{
				/* Don't increase indent when we see
				an explicit fold. */
				if(line.length() - i >= 3)
				{
					if(line.substring(i,i+3).equals("{{{"))
					{
						i += 2;
						continue;
					}
				}
				brackets.openCount++;
			}
			else if(ch == closeBracket)
			{
				if(brackets.openCount != 0)
					brackets.openCount--;
				else
					brackets.closeCount++;
			}
		}

		return brackets;
	} //}}}

	//{{{ toString() method
	public String toString()
	{
		return getClass().getName() + "[" + openBracket + ","
			+ closeBracket + "]";
	} //}}}

	protected char openBracket, closeBracket;
}