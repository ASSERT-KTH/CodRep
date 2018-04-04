public String lastNoWordSep = "_";

/*
 * XModeHandler.java - XML handler for mode files
 * :tabSize=8:indentSize=8:noTabs=false:
 * :folding=explicit:collapseFolds=1:
 *
 * Copyright (C) 1999 mike dillon
 * Portions copyright (C) 2000, 2001 Slava Pestov
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

package org.gjt.sp.jedit.syntax;

//{{{ Imports
import java.io.*;
import java.util.*;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

import org.xml.sax.Attributes;
import org.xml.sax.InputSource;
import org.xml.sax.helpers.DefaultHandler;

import org.gjt.sp.jedit.MiscUtilities;
import org.gjt.sp.util.Log;
//}}}

/**
 * XML handler for mode definition files.
 */
public abstract class XModeHandler extends DefaultHandler
{
	//{{{ XModeHandler constructor
	public XModeHandler (String modeName)
	{
		this.modeName = modeName;
		marker = new TokenMarker();
		marker.addRuleSet(new ParserRuleSet(modeName,"MAIN"));
		stateStack = new Stack();
	} //}}}

	//{{{ resolveEntity() method
	public InputSource resolveEntity(String publicId, String systemId)
	{
		return MiscUtilities.findEntity(systemId, "xmode.dtd", XModeHandler.class);
	} //}}}

	//{{{ characters() method
	public void characters(char[] c, int off, int len)
	{
		peekElement().setText(c, off, len);
	} //}}}

	//{{{ startElement() method
	public void startElement(String uri, String localName,
				 String qName, Attributes attrs)
	{
		TagDecl tag = pushElement(qName, attrs);

		if (qName.equals("WHITESPACE"))
		{
			Log.log(Log.WARNING,this,modeName + ": WHITESPACE rule "
				+ "no longer needed");
		}
		else if (qName.equals("KEYWORDS"))
		{
			keywords = new KeywordMap(rules.getIgnoreCase());
		}
		else if (qName.equals("RULES"))
		{
			if(tag.lastSetName == null)
				tag.lastSetName = "MAIN";
			rules = marker.getRuleSet(tag.lastSetName);
			if(rules == null)
			{
				rules = new ParserRuleSet(modeName,tag.lastSetName);
				marker.addRuleSet(rules);
			}
			rules.setIgnoreCase(tag.lastIgnoreCase);
			rules.setHighlightDigits(tag.lastHighlightDigits);
			if(tag.lastDigitRE != null)
			{
				try
				{
					rules.setDigitRegexp(Pattern.compile(tag.lastDigitRE,
						tag.lastIgnoreCase
						? Pattern.CASE_INSENSITIVE : 0));
				}
				catch(PatternSyntaxException e)
				{
					error("regexp",e);
				}
			}

			if(tag.lastEscape != null)
				rules.setEscapeRule(ParserRule.createEscapeRule(tag.lastEscape));
			rules.setDefault(tag.lastDefaultID);
			rules.setNoWordSep(tag.lastNoWordSep);
		}
	} //}}}

	//{{{ endElement() method
	public void endElement(String uri, String localName, String name)
	{
		TagDecl tag = popElement();
		if (name.equals(tag.tagName))
		{
			//{{{ PROPERTY
			if (tag.tagName.equals("PROPERTY"))
			{
				props.put(propName,propValue);
			} //}}}
			//{{{ PROPS
			else if (tag.tagName.equals("PROPS"))
			{
				if(peekElement().tagName.equals("RULES"))
					rules.setProperties(props);
				else
					modeProps = props;

				props = new Hashtable();
			} //}}}
			//{{{ RULES
			else if (tag.tagName.equals("RULES"))
			{
				rules.setKeywords(keywords);
				keywords = null;
				rules = null;
			} //}}}
			//{{{ IMPORT
			else if (tag.tagName.equals("IMPORT"))
			{
				rules.addRuleSet(tag.lastDelegateSet);
			} //}}}
			//{{{ TERMINATE
			else if (tag.tagName.equals("TERMINATE"))
			{
				rules.setTerminateChar(tag.termChar);
			} //}}}
			//{{{ SEQ
			else if (tag.tagName.equals("SEQ"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","SEQ");
					return;
				}

				rules.addRule(ParserRule.createSequenceRule(
					tag.lastStartPosMatch,tag.lastStart,
					tag.lastDelegateSet,tag.lastTokenID));
			} //}}}
			//{{{ SEQ_REGEXP
			else if (tag.tagName.equals("SEQ_REGEXP"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","SEQ_REGEXP");
					return;
				}

				try
				{
					rules.addRule(ParserRule.createRegexpSequenceRule(
						tag.lastHashChar,tag.lastStartPosMatch,
						tag.lastStart,tag.lastDelegateSet,
						tag.lastTokenID,tag.lastIgnoreCase));
				}
				catch(PatternSyntaxException re)
				{
					error("regexp",re);
				}
			} //}}}
			//{{{ SPAN
			else if (tag.tagName.equals("SPAN"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","BEGIN");
					return;
				}

				if(tag.lastEnd == null)
				{
					error("empty-tag","END");
					return;
				}

				rules.addRule(ParserRule
					.createSpanRule(
					tag.lastStartPosMatch,tag.lastStart,
					tag.lastEndPosMatch,tag.lastEnd,
					tag.lastDelegateSet,
					tag.lastTokenID,tag.lastExcludeMatch,
					tag.lastNoLineBreak,
					tag.lastNoWordBreak,
					tag.lastNoEscape));
			} //}}}
			//{{{ SPAN_REGEXP
			else if (tag.tagName.equals("SPAN_REGEXP"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","BEGIN");
					return;
				}

				if(tag.lastEnd == null)
				{
					error("empty-tag","END");
					return;
				}

				try
				{
					rules.addRule(ParserRule
						.createRegexpSpanRule(
						tag.lastHashChar,
						tag.lastStartPosMatch,tag.lastStart,
						tag.lastEndPosMatch,tag.lastEnd,
						tag.lastDelegateSet,
						tag.lastTokenID,
						tag.lastExcludeMatch,
						tag.lastNoLineBreak,
						tag.lastNoWordBreak,
						tag.lastIgnoreCase,
						tag.lastNoEscape));
				}
				catch(PatternSyntaxException re)
				{
					error("regexp",re);
				}
			} //}}}
			//{{{ EOL_SPAN
			else if (tag.tagName.equals("EOL_SPAN"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","EOL_SPAN");
					return;
				}

				rules.addRule(ParserRule.createEOLSpanRule(
					tag.lastStartPosMatch,tag.lastStart,
					tag.lastDelegateSet,tag.lastTokenID,
					tag.lastExcludeMatch));
			} //}}}
			//{{{ EOL_SPAN_REGEXP
			else if (tag.tagName.equals("EOL_SPAN_REGEXP"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","EOL_SPAN_REGEXP");
					return;
				}

				try
				{
					rules.addRule(ParserRule.createRegexpEOLSpanRule(
						tag.lastHashChar,tag.lastStartPosMatch,
						tag.lastStart,tag.lastDelegateSet,
						tag.lastTokenID,tag.lastExcludeMatch,
						tag.lastIgnoreCase));
				}
				catch(PatternSyntaxException re)
				{
					error("regexp",re);
				}
			} //}}}
			//{{{ MARK_FOLLOWING
			else if (tag.tagName.equals("MARK_FOLLOWING"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","MARK_FOLLOWING");
					return;
				}

				rules.addRule(ParserRule
					.createMarkFollowingRule(
					tag.lastStartPosMatch,tag.lastStart,
					tag.lastTokenID,tag.lastExcludeMatch));
			} //}}}
			//{{{ MARK_PREVIOUS
			else if (tag.tagName.equals("MARK_PREVIOUS"))
			{
				if(tag.lastStart == null)
				{
					error("empty-tag","MARK_PREVIOUS");
					return;
				}

				rules.addRule(ParserRule
					.createMarkPreviousRule(
					tag.lastStartPosMatch,tag.lastStart,
					tag.lastTokenID,tag.lastExcludeMatch));
			} //}}}
			//{{{ Keywords
			else if (
				!tag.tagName.equals("END")
				&& !tag.tagName.equals("BEGIN")
				&& !tag.tagName.equals("KEYWORDS")
				&& !tag.tagName.equals("MODE")
			) {
				byte token = Token.stringToToken(tag.tagName);
				if(token != -1)
					addKeyword(tag.lastKeyword,token);
			} //}}}
		}
		else
		{
			// can't happen
			throw new InternalError();
		}
	} //}}}

	//{{{ startDocument() method
	public void startDocument()
	{
		props = new Hashtable();
		pushElement(null, null);
	} //}}}

	//{{{ endDocument() method
	public void endDocument()
	{
		ParserRuleSet[] rulesets = marker.getRuleSets();
		for(int i = 0; i < rulesets.length; i++)
		{
			rulesets[i].resolveImports();
		}
	} //}}}

	//{{{ getTokenMarker() method
	public TokenMarker getTokenMarker()
	{
		return marker;
	} //}}}

	//{{{ getModeProperties() method
	public Hashtable getModeProperties()
	{
		return modeProps;
	} //}}}

	//{{{ Protected members

	//{{{ error() method
	/**
	 * Reports an error.
	 * You must override this method so that the mode loader can do error
	 * reporting.
	 * @param msg The error type
	 * @param subst A <code>String</code> or a <code>Throwable</code>
	 * containing specific information
	 * @since jEdit 4.2pre1
	 */
	protected abstract void error(String msg, Object subst);
	//}}}

	//{{{ getTokenMarker() method
	/**
	 * Returns the token marker for the given mode.
	 * You must override this method so that the mode loader can resolve
	 * delegate targets.
	 * @param mode The mode name
	 * @since jEdit 4.2pre1
	 */
	protected abstract TokenMarker getTokenMarker(String mode);
	//}}}

	//}}}

	//{{{ Private members

	//{{{ Instance variables
	private String modeName;
	private TokenMarker marker;
	private KeywordMap keywords;
	private Stack stateStack;
	private String propName;
	private String propValue;
	private Hashtable props;
	private Hashtable modeProps;
	private ParserRuleSet rules;
	//}}}

	//{{{ addKeyword() method
	private void addKeyword(String k, byte id)
	{
		if(k == null)
		{
			error("empty-keyword",null);
			return;
		}

		if (keywords == null) return;
		keywords.add(k,id);
	} //}}}

	//{{{ pushElement() method
	private TagDecl pushElement(String name, Attributes attrs)
	{
		if (name != null)
		{
			TagDecl tag = new TagDecl(name, attrs);
			stateStack.push(tag);
			return tag;
		}
		else
		{
			stateStack.push(null);
			return null;
		}
	} //}}}

	//{{{ peekElement() method
	private TagDecl peekElement()
	{
		return (TagDecl) stateStack.peek();
	} //}}}

	//{{{ popElement() method
	private TagDecl popElement()
	{
		return (TagDecl) stateStack.pop();
	} //}}}

	//}}}

	/**
	 * Hold info about what tag was read and what attributes were
	 * set in the XML file, to be kept by the handler in a stack
	 * (similar to the way tag names were kept in a stack before).
	 */
	private class TagDecl
	{

		public TagDecl(String tagName, Attributes attrs)
		{
			this.tagName = tagName;

			String tmp;

			propName = attrs.getValue("NAME");
			propValue = attrs.getValue("VALUE");

			tmp = attrs.getValue("TYPE");
			if (tmp != null)
			{
				lastTokenID = Token.stringToToken(tmp);
				if(lastTokenID == -1)
					error("token-invalid",tmp);
			}

			lastAtLineStart = "TRUE".equals(attrs.getValue("AT_LINE_START"));
			lastAtWhitespaceEnd = "TRUE".equals(attrs.getValue("AT_WHITESPACE_END"));
			lastAtWordStart = "TRUE".equals(attrs.getValue("AT_WORD_START"));
			lastNoLineBreak = "TRUE".equals(attrs.getValue("NO_LINE_BREAK"));
			lastNoWordBreak = "TRUE".equals(attrs.getValue("NO_WORD_BREAK"));
			lastNoEscape = "TRUE".equals(attrs.getValue("NO_ESCAPE"));
			lastExcludeMatch = "TRUE".equals(attrs.getValue("EXCLUDE_MATCH"));
			lastIgnoreCase = (attrs.getValue("IGNORE_CASE") == null ||
					"TRUE".equals(attrs.getValue("IGNORE_CASE")));
			lastHighlightDigits = "TRUE".equals(attrs.getValue("HIGHLIGHT_DIGITS"));;
			lastDigitRE = attrs.getValue("DIGIT_RE");

			tmp = attrs.getValue("NO_WORD_SEP");
			if (tmp != null)
				lastNoWordSep = tmp;

			tmp = attrs.getValue("AT_CHAR");
			if (tmp != null)
			{
				try
				{
					termChar = Integer.parseInt(tmp);
				}
				catch (NumberFormatException e)
				{
					error("termchar-invalid",tmp);
					termChar = -1;
				}
			}

			lastEscape = attrs.getValue("ESCAPE");;
			lastSetName = attrs.getValue("SET");;

			tmp = attrs.getValue("DELEGATE");
			if (tmp != null)
			{
				String delegateMode, delegateSetName;

				int index = tmp.indexOf("::");

				if(index != -1)
				{
					delegateMode = tmp.substring(0,index);
					delegateSetName = tmp.substring(index + 2);
				}
				else
				{
					delegateMode = modeName;
					delegateSetName = tmp;
				}

				TokenMarker delegateMarker = getTokenMarker(delegateMode);
				if(delegateMarker == null)
					error("delegate-invalid",tmp);
				else
				{
					lastDelegateSet = delegateMarker
						.getRuleSet(delegateSetName);
					if(delegateMarker == marker
						&& lastDelegateSet == null)
					{
						// stupid hack to handle referencing
						// a rule set that is defined later!
						lastDelegateSet = new ParserRuleSet(
							delegateMode,
							delegateSetName);
						lastDelegateSet.setDefault(Token.INVALID);
						marker.addRuleSet(lastDelegateSet);
					}
					else if(lastDelegateSet == null)
						error("delegate-invalid",tmp);
				}
			}

			tmp = attrs.getValue("DEFAULT");
			if (tmp != null)
			{
				lastDefaultID = Token.stringToToken(tmp);
				if(lastDefaultID == -1)
				{
					error("token-invalid",tmp);
					lastDefaultID = Token.NULL;
				}
			}

			tmp = attrs.getValue("HASH_CHAR");
			if (tmp != null)
			{
				if(tmp.length() != 1)
				{
					error("hash-char-invalid",tmp);
					lastDefaultID = Token.NULL;
				}
				else
					lastHashChar = tmp.charAt(0);
			}
		}

		public void setText(char[] c, int off, int len)
		{
			String text = new String(c, off, len);
			if (tagName.equals("EOL_SPAN") ||
				tagName.equals("EOL_SPAN_REGEXP") ||
				tagName.equals("MARK_PREVIOUS") ||
				tagName.equals("MARK_FOLLOWING") ||
				tagName.equals("SEQ") ||
				tagName.equals("SEQ_REGEXP") ||
				tagName.equals("BEGIN")
			)
			{
				TagDecl target = this;
				if (tagName.equals("BEGIN"))
					target = (TagDecl) stateStack.get(stateStack.size() - 2);

				if (target.lastStart == null)
					target.lastStart = text;
				else
					target.lastStart += text;
				target.lastStartPosMatch = ((target.lastAtLineStart ? ParserRule.AT_LINE_START : 0)
					| (target.lastAtWhitespaceEnd ? ParserRule.AT_WHITESPACE_END : 0)
					| (target.lastAtWordStart ? ParserRule.AT_WORD_START : 0));
				target.lastAtLineStart = false;
				target.lastAtWordStart = false;
				target.lastAtWhitespaceEnd = false;
			}
			else if (tagName.equals("END"))
			{
				TagDecl target = (TagDecl) stateStack.get(stateStack.size() - 2);
				if (target.lastEnd == null)
					target.lastEnd = text;
				else
					target.lastEnd += text;
				target.lastEndPosMatch = ((target.lastAtLineStart ? ParserRule.AT_LINE_START : 0)
					| (target.lastAtWhitespaceEnd ? ParserRule.AT_WHITESPACE_END : 0)
					| (target.lastAtWordStart ? ParserRule.AT_WORD_START : 0));
				target.lastAtLineStart = false;
				target.lastAtWordStart = false;
				target.lastAtWhitespaceEnd = false;
			}
			else
			{
				if (lastKeyword == null)
					lastKeyword = text;
				else
					lastKeyword += text;
			}
		}

		public String tagName;
		public String lastStart;
		public String lastEnd;
		public String lastKeyword;
		public String lastSetName;
		public String lastEscape;
		public ParserRuleSet lastDelegateSet;
		public String lastNoWordSep;
		public ParserRuleSet rules;
		public byte lastDefaultID = Token.NULL;
		public byte lastTokenID;
		public int termChar = -1;
		public boolean lastNoLineBreak;
		public boolean lastNoWordBreak;
		public boolean lastExcludeMatch;
		public boolean lastIgnoreCase = true;
		public boolean lastHighlightDigits;
		public boolean lastAtLineStart;
		public boolean lastAtWhitespaceEnd;
		public boolean lastAtWordStart;
		public boolean lastNoEscape;
		public int lastStartPosMatch;
		public int lastEndPosMatch;
		public String lastDigitRE;
		public char lastHashChar;

	}

}