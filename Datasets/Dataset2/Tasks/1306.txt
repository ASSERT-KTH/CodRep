return ch & 0x000000FF;

/*
 * BoyerMooreSearchMatcher.java - Literal pattern String matcher utilizing the
 *         Boyer-Moore algorithm
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999, 2000 mike dillon
 * Portions copyright (C) 2001 Tom Locke
 * Portions copyright (C) 2001, 2002 Slava Pestov
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

package org.gjt.sp.jedit.search;

//{{{ Imports

import gnu.regexp.CharIndexed;

//}}}

/**
 * Implements literal search using the Boyer-Moore algorithm.
 */
public class BoyerMooreSearchMatcher extends SearchMatcher
{
	//{{{ BoyerMooreSearchMatcher constructor
	/**
	 * Creates a new string literal matcher.
	 */
	public BoyerMooreSearchMatcher(String pattern, boolean ignoreCase)
	{
		this.pattern = pattern.toCharArray();
		if(ignoreCase)
		{
			for(int i = 0; i < this.pattern.length; i++)
			{
				this.pattern[i] = Character.toUpperCase(
					this.pattern[i]);
			}
		}

		this.ignoreCase = ignoreCase;

		pattern_end = this.pattern.length - 1;
	} //}}}

	//{{{ nextMatch() method
	/**
	 * Returns the offset of the first match of the specified text
	 * within this matcher.
	 * @param text The text to search in
	 * @param start True if the start of the segment is the beginning of the
	 * buffer
	 * @param end True if the end of the segment is the end of the buffer
	 * @param firstTime If false and the search string matched at the start
	 * offset with length zero, automatically find next match
	 * @param reverse If true, searching will be performed in a backward
	 * direction.
	 * @return an array where the first element is the start offset
	 * of the match, and the second element is the end offset of
	 * the match
	 * @since jEdit 4.2pre4
	 */
	public SearchMatcher.Match nextMatch(CharIndexed text,
		boolean start, boolean end, boolean firstTime,
		boolean reverse)
	{
		int pos = match(text,reverse);

		if (pos == -1)
		{
			return null;
		}
		else
		{
			returnValue.start = pos;
			returnValue.end = pos + pattern.length;
			return returnValue;
		}
	} //}}}

	//{{{ match() method
	/*
	 *  a good introduction to the Boyer-Moore fast string matching
	 *  algorithm may be found on Moore's website at:
	 *
	 *   http://www.cs.utexas.edu/users/moore/best-ideas/string-searching/
	 *
	 */
	public int match(CharIndexed text, boolean reverse)
	{
		//{{{
		// lazily create skip and suffix arrays for either the
		// search pattern, or the reversed search pattern
		int[] skip, suffix;
		if(reverse)
		{
			if(back_skip == null)
			{
				back_skip = generateSkipArray(true);
				back_suffix = generateSuffixArray(true);
			}
			skip = back_skip;
			suffix = back_suffix;
		}
		else
		{
			if(fwd_skip == null)
			{
				fwd_skip = generateSkipArray(false);
				fwd_suffix = generateSuffixArray(false);
			}
			skip = fwd_skip;
			suffix = fwd_suffix;
		} //}}}

		// position variable for pattern test position
		int pos;

		// position variable for pattern start
		int anchor = 0;

		// last possible start position of a match with this pattern;
		// this is negative if the pattern is longer than the text
		// causing the search loop below to immediately fail
		//int last_anchor = reverseSearch
		//	? offset + pattern.length - 1
		//	: length - pattern.length;

		char ch = 0;

		int bad_char;
		int good_suffix;

		// the search works by starting the anchor (first character
		// of the pattern) at the initial offset. as long as the
		// anchor is far enough from the enough of the text for the
		// pattern to match, and until the pattern matches, we
		// compare the pattern to the text from the last character
		// to the first character in reverse order. where a character
		// in the pattern mismatches, we use the two heuristics
		// based on the mismatch character and its position in the
		// pattern to determine the furthest we can move the anchor
		// without missing any potential pattern matches.
SEARCH:
		while (text.isValid())
		{
			for (pos = pattern_end; pos >= 0; --pos)
			{
				ch = text.charAt(pos);
				if(ignoreCase)
					ch = Character.toUpperCase(ch);

				// pattern test
				if ((reverse ? ch != pattern[pattern_end - pos]
					: ch != pattern[pos]))
				{
					// character mismatch, determine how many characters to skip

					// heuristic #1
					bad_char = pos - skip[getSkipIndex(ch)];

					// heuristic #2
					good_suffix = suffix[pos];

					// skip the greater of the two distances provided by the
					// heuristics
					int skip_index = (bad_char > good_suffix) ? bad_char : good_suffix;
					anchor += skip_index;
					text.move(skip_index);

					// go back to the while loop
					continue SEARCH;
				}
			}

			// MATCH: return the position of its first character
			return anchor;
		}

		// MISMATCH: return -1 as defined by API
		return -1;
	} //}}}

	//{{{ Private members
	private char[] pattern;
	private int pattern_end;
	private boolean ignoreCase;

	// Boyer-Moore member fields
	private int[] fwd_skip;
	private int[] fwd_suffix;
	private int[] back_skip;
	private int[] back_suffix;
	//}}}

	// Boyer-Moore helper methods

	//{{{ generateSkipArray() method
	/*
	 *  the 'skip' array is used to determine for each index in the
	 *  hashed alphabet how many characters can be skipped if
	 *  a mismatch occurs on a characater hashing to that index.
	 */
	private int[] generateSkipArray(boolean reverse)
	{
		// initialize the skip array to all zeros
		int[] skip = new int[256];

		// leave the table cleanly-initialized for an empty pattern
		if (pattern.length == 0)
			return skip;

		int pos = 0;

		do
		{
			skip[getSkipIndex(pattern[reverse ? pattern_end - pos : pos])] = pos;
		}
		while (++pos < pattern.length);

		return skip;
	} //}}}

	//{{{ getSkipIndex() method
	/*
	 *  to avoid our skip table having a length of 2 ^ 16, we hash each
	 *  character of the input into a character in the alphabet [\x00-\xFF]
	 *  using the lower 8 bits of the character's value (resulting in
	 *  a more reasonable skip table of length 2 ^ 8).
	 *
	 *  the result of this is that more than one character can hash to the
	 *  same index, but since the skip table encodes the position of
	 *  occurence of the character furthest into the string with a particular
	 *  index (whether or not it is the only character with that index), an
	 *  index collision only means that that this heuristic will give a
	 *  sub-optimal skip (i.e. a complete skip table could use the differences
	 *  between colliding characters to maximal effect, at the expense of
	 *  building a table that is over 2 orders of magnitude larger and very
	 *  sparse).
	 */
	private static final int getSkipIndex(char ch)
	{
		return ((int) ch) & 0x000000FF;
	} //}}}

	//{{{ generateSuffixArray() method
	/*
	 *  XXX: hairy code that is basically just a functional(?) port of some
	 *  other code i barely understood
	 */
	private int[] generateSuffixArray(boolean reverse)
	{
		int m = pattern.length;

		int j = m + 1;

		int[] suffix = new int[j];
		int[] tmp = new int[j];
		tmp[m] = j;

		for (int i = m; i > 0; --i)
		{
			while (j <= m && pattern[reverse ? pattern_end - i + 1 : i - 1]
				!= pattern[reverse ? pattern_end - j + 1 : j - 1])
			{
				if (suffix[j] == 0)
				{
					suffix[j] = j - i;
				}

				j = tmp[j];
			}

			tmp[i - 1] = --j;
		}

		int k = tmp[0];

		for (j = 0; j <= m; j++)
		{
			// the code above builds a 1-indexed suffix array,
			// but we shift it to be 0-indexed, ignoring the
			// original 0-th element
			if (j > 0)
			{
				suffix[j - 1] = (suffix[j] == 0) ? k : suffix[j];
			}

			if (j == k)
			{
				k = tmp[k];
			}
		}

		return suffix;
	} //}}}

	//}}}
}