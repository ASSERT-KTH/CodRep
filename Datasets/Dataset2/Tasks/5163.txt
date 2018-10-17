String gunk = "/#~:;.?+=&@!\\-%";

/*
 * Created on 23-06-2003
 */
//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.

package org.columba.mail.parser.text;

import java.io.BufferedReader;
import java.io.StringReader;

import org.apache.oro.text.regex.MalformedPatternException;
import org.apache.oro.text.regex.Pattern;
import org.apache.oro.text.regex.PatternCompiler;
import org.apache.oro.text.regex.PatternMatcher;
import org.apache.oro.text.regex.Perl5Compiler;
import org.apache.oro.text.regex.Perl5Matcher;
import org.apache.oro.text.regex.Perl5Substitution;
import org.apache.oro.text.regex.Util;
import org.columba.core.logging.ColumbaLogger;

/**
 * Contains different utility functions for manipulating Html based
 * text. This includes functionality for removing and restoring
 * special entities (such as &, <, >, ...) and functionality for
 * removing html tags from the text.
 * 
 * @author Karl Peder Olesen (karlpeder), 20030623
 *
 */
public class HtmlParser {

	/**
	 * Strips html tags. The method used is very simple:
	 * Everything between tag-start (&lt) and tag-end (&gt) is removed.
	 * Optionaly br tags are replaced by newline and ending p tags with
	 * double newline.
	 * 
	 * @param	s			input string
	 * @param	breakToNl	if true, newlines are inserted for br and p tags
	 * @return	output without html tags (null on error)
	 * @author	karlpeder, 20030623
	 * 			(moved from org.columba.mail.gui.message.util.DocumentParser) 
	 */
	public static String stripHtmlTags(String s, boolean breakToNl) {
		// initial check of input:
		if (s == null)
			return null;
		
		PatternMatcher matcher   = new Perl5Matcher();
		PatternCompiler compiler = new Perl5Compiler();
		Pattern pattern;
		String pat;
		
		try {
			if (breakToNl) {
				// replace <br> and </br> with newline
				pat = "\\<[/]?br\\>";
				pattern = compiler.compile(
						pat,
						Perl5Compiler.CASE_INSENSITIVE_MASK);
				s = Util.substitute(matcher, pattern,
						new Perl5Substitution("\n"), s, 
						Util.SUBSTITUTE_ALL);
				// replace </p> with double newline
				pat = "\\</p\\>";
				pattern = compiler.compile(
						pat,
						Perl5Compiler.CASE_INSENSITIVE_MASK);
				s = Util.substitute(matcher, pattern,
						new Perl5Substitution("\n\n"), s, 
						Util.SUBSTITUTE_ALL);
			}
			
			// strip tags
			pat = "\\<(.|\\n)*?\\>";
			pattern = compiler.compile(
					pat,
					Perl5Compiler.CASE_INSENSITIVE_MASK);
			s = Util.substitute(matcher, pattern,
					new Perl5Substitution(""), s, 
					Util.SUBSTITUTE_ALL);

		} catch (MalformedPatternException e) {
			ColumbaLogger.log.error("Error stripping html tags", e);
			return null;	// error
		}

		return s;

	}

	/**
	 * Performs in large terms the reverse of
	 * substituteSpecialCharacters (though br tags are not 
	 * converted to newlines, this should be handled separately).
	 * More preciesly it changes special entities like
	 * amp, nbsp etc. to their real counter parts: &, space etc. 
	 * 	 
	 * @param	s	input string
	 * @return	output with special entities replaced with their
	 * 			"real" counter parts (null on error)
	 * @author  karlpeder, 20030623
	 * 			(moved from org.columba.mail.gui.message.util.DocumentParser)
	 */
	public static String restoreSpecialCharacters(String s) {
		// initial check of input:
		if (s == null)
			return null;
		
		StringBuffer sb = new StringBuffer(s.length());
		StringReader sr = new StringReader(s);
		BufferedReader br = new BufferedReader(sr);
		String ss = null;

		try {

			while ((ss = br.readLine()) != null) {
				int pos = 0;
				while (pos < ss.length()) {
					char c = ss.charAt(pos);
					if (c == '&') {
						if 		  (ss.substring(pos).startsWith("&lt;")) {
							sb.append('<');
							pos = pos + 4;
						} else if (ss.substring(pos).startsWith("&gt;")) {
							sb.append('>');
							pos = pos + 4;
						} else if (ss.substring(pos).startsWith("&amp;")) {
							sb.append('&');
							pos = pos + 5;
						} else if (ss.substring(pos).startsWith("&quot;")) {
							sb.append('"');
							pos = pos + 6;
						} else if (ss.substring(pos).startsWith(
									"&nbsp;&nbsp;&nbsp;&nbsp;")) {
							sb.append('\t');
							pos = pos + 24;
						} else if (ss.substring(pos).startsWith("&nbsp;")) {
							sb.append(' ');
							pos = pos + 6;
						} else {
							// unknown special entity - just keep it as-is
							sb.append(c);
							pos++;
						}
					} else {
						sb.append(c);
						pos++;
					}
				}
				sb.append('\n');
			}

		} catch (Exception e) {
			ColumbaLogger.log.error("Error restoring special characters", e);
			return null;	// error
		}

		return sb.toString();
	}

	/**
	 * Strips html tags. and replaces special entities with their
	 * "normal" counter parts, e.g. &gt; => >.<br>
	 * Calling this method is the same as calling first stripHtmlTags
	 * and then restoreSpecialCharacters.
	 * 
	 * @param	html	input string
	 * @return	output without html tags and special entities
	 * 			(null on error)
	 * @author	karlpeder, 20030623
	 * 			(moved from org.columba.mail.parser.text.BodyTextParser)
	 */
	public static String htmlToText(String html) {
		// stripHtmlTags called with true ~ p & br => newlines
		String text = stripHtmlTags(html, true);
		return restoreSpecialCharacters(text);
	}

	/**	
	 * Substitute special characters like:
	 * <,>,&,\t,\n,"
	 * with special entities used in html (amp, nbsp, ...)
	 * 
	 * @param	s	input string containing special characters
	 * @return	output with special characters substituted
	 * 			(null on error)
	 */
	public static String substituteSpecialCharacters(String s) {

		StringBuffer sb = new StringBuffer(s.length());
		StringReader sr = new StringReader(s);
		BufferedReader br = new BufferedReader(sr);
		String ss = null;

		/*
		 * *20030618, karlpeder* Changed the way multiple spaces are 
		 * replaced with &nbsp; to give better word wrap
		 * *20030623, karlpeder* Added " => &quot;
		 */

		try {

			while ((ss = br.readLine()) != null) {
				int i = 0;
				while (i < ss.length()) {
					switch (ss.charAt(i)) {
						case '<' :
							sb.append("&lt;");
							i++;
							break;
						case '>' :
							sb.append("&gt;");
							i++;
							break;
						case '&' :
							sb.append("&amp;");
							i++;
							break;
						case '"' :
							sb.append("&quot;");
							i++;
							break;
						case ' ' :
							//sb.append("&nbsp;");
							if        (ss.substring(i).startsWith("    ")) {
								sb.append("&nbsp; ");
								i = i + 2;
							} else if (ss.substring(i).startsWith("   ")) {
								sb.append("&nbsp;&nbsp; ");
								i = i + 3;
							} else if (ss.substring(i).startsWith("  ")) {
								sb.append("&nbsp; ");
								i = i + 2;
							} else {
								sb.append(' ');
								i++;
							}
							break;
						case '\t' :
							sb.append("&nbsp;&nbsp;&nbsp;&nbsp;");
							i++;
							break;
						case '\n' :
							sb.append("<br>");
							i++;
							break;
						default :
							sb.append(ss.charAt(i));
							i++;
							break;
					}
				}
				sb.append("<br>\n");
			}

		} catch (Exception e) {
			ColumbaLogger.log.error(
					"Error substituting special characters", e);
			return null;	// error
		}

		return sb.toString();

	}
	
	/**	
	 * 
	 * substitute special characters like:
	 * <,>,&,\t,\n
	 * with special entities used in html<br>
	 * This is the same as substituteSpecialCharacters, but
	 * here an extra newline character is not inserted.
	 * 
	 * @param	s	input string containing special characters
	 * @return	output with special characters substituted
	 * 			(null on error)
	 */
	public static String substituteSpecialCharactersInHeaderfields(String s) {
		StringBuffer sb = new StringBuffer(s.length());
		StringReader sr = new StringReader(s);
		BufferedReader br = new BufferedReader(sr);
		String ss = null;

		/*
		 * *20030623, karlpeder* " and space handled also
		 */

		try {

			while ((ss = br.readLine()) != null) {
				int i = 0;
				while (i < ss.length()) {
					switch (ss.charAt(i)) {
						case '<' :
							sb.append("&lt;");
							i++;
							break;
						case '>' :
							sb.append("&gt;");
							i++;
							break;
						case '&' :
							sb.append("&amp;");
							i++;
							break;
						case '"' :
							sb.append("&quot;");
							i++;
							break;
						case ' ' :
							if        (ss.substring(i).startsWith("    ")) {
								sb.append("&nbsp; ");
								i = i + 2;
							} else if (ss.substring(i).startsWith("   ")) {
								sb.append("&nbsp;&nbsp; ");
								i = i + 3;
							} else if (ss.substring(i).startsWith("  ")) {
								sb.append("&nbsp; ");
								i = i + 2;
							} else {
								sb.append(' ');
								i++;
							}
							break;
						case '\t' :
							sb.append("&nbsp;&nbsp;&nbsp;&nbsp;");
							i++;
							break;
						case '\n' :
							sb.append("<br>");
							i++;
							break;
						default :
							sb.append(ss.charAt(i));
							i++;
							break;
					}
				}

			}

		} catch (Exception e) {
			ColumbaLogger.log.error(
					"Error substituting special characters", e);
			return null;	// error
		}

		return sb.toString();

	}

	/**
	 * Tries to fix broken html-strings by inserting 
	 * html start- and end tags if missing, and by
	 * removing content after the html end tag.
	 * 
	 * @param	input	html content to be validated
	 * @return	content with extra tags inserted if necessary
	 */
	public static String validateHTMLString(String input) {
		StringBuffer output = new StringBuffer(input);
		int index = 0;

		String lowerCaseInput = input.toLowerCase();

		// Check for missing  <html> tag
		if (lowerCaseInput.indexOf("<html>") == -1) {
			if (lowerCaseInput.indexOf("<!doctype") != -1)
				index =
					lowerCaseInput.indexOf(
						"\n",
						lowerCaseInput.indexOf("<!doctype"))
						+ 1;
			output.insert(index, "<html>");
		}

		// Check for missing  </html> tag
		if (lowerCaseInput.indexOf("</html>") == -1) {
			output.append("</html>");
		}

		// remove characters after </html> tag
		index = lowerCaseInput.indexOf("</html>");
		if (lowerCaseInput.length() >= index + 7) {
			lowerCaseInput = lowerCaseInput.substring(0, index + 7);
		}

		return output.toString();
	}

	/**
	 * parse text and transform every email-address
	 * in a HTML-conform address
	 * 
	 * @param	s	input text
	 * @return	text with email-adresses transformed to links
	 * 			(null on error)
	 */
	public static String substituteEmailAddress(String s) {

		PatternMatcher addressMatcher   = new Perl5Matcher();
		PatternCompiler addressCompiler = new Perl5Compiler();
		Pattern addressPattern;

		//String pattern = "\\b(([\\w|.|\\-|_]*)@([\\w|.|\\-|_]*)(.)([a-zA-Z]{2,}))";

		// contributed by Paul Nicholls
		//  -> corrects inclusion of trailing full-stops
		//  -> works for numerical ip addresses, too
		String pattern = "([\\w.\\-]*\\@([\\w\\-]+\\.*)+[a-zA-Z0-9]{2,})";

		try {
			addressCompiler = new Perl5Compiler();
			addressPattern =
				addressCompiler.compile(
					pattern,
					Perl5Compiler.CASE_INSENSITIVE_MASK);
	
			addressMatcher = new Perl5Matcher();
	
			String result =
				Util.substitute(
					addressMatcher,
					addressPattern,
					new Perl5Substitution("<A HREF=mailto:$1>$1</A>"),
					s,
					Util.SUBSTITUTE_ALL);
	
			return result;
		} catch (MalformedPatternException e) {
			ColumbaLogger.log.error(
					"Error transforming email-adresses to links", e);
			return null;	// error
		}

	}

	/**
	 * parse text and transform every url
	 * in a HTML-conform url
	 * 
	 * @param	s	input text
	 * @return	text with urls transformed to links
	 * 			(null on error)
	 */
	public static String substituteURL(String s) {

		PatternMatcher urlMatcher   = new Perl5Matcher();
		PatternCompiler urlCompiler = new Perl5Compiler();
		Pattern urlPattern;

		String urls = "(http|https|ftp)";
		String letters = "\\w";
		String gunk = "/#~:.?+=&@!\\-%";
		String punc = ".:?\\-";
		String any = "${" + letters + "}${" + gunk + "}${" + punc + "}";

		/**
		 *
		 *  
		 * \\b  				start at word boundary
		 * (					begin $1
		 * urls:				url can be (http:, https:, ftp:) 
		 * [any]+?				followed by one or more of any valid character
		 * 						(be conservative - take only what you need)
		 * )					end of $1
		 * (?=					look-ahead non-consumptive assertion
		 * [punc]*				either 0 or more punctuation
		 * [^any]				  followed by a non-url char
		 * |					or else
		 * $					  then end of the string
		 * )
		 */
		String pattern =
			"\\b"
				+ "("
				+ urls
				+ ":["
				+ any
				+ "]+?)(?=["
				+ punc
				+ "]*[^"
				+ any
				+ "]|$)";
		
		try {
			urlCompiler = new Perl5Compiler();
			urlPattern =
				urlCompiler.compile(pattern, Perl5Compiler.CASE_INSENSITIVE_MASK);
	
			urlMatcher = new Perl5Matcher();
	
			String result =
				Util.substitute(
					urlMatcher,
					urlPattern,
					new Perl5Substitution("<A HREF=$1>$1</A>"),
					s,
					Util.SUBSTITUTE_ALL);
	
			return result;
		} catch (MalformedPatternException e) {
			ColumbaLogger.log.error(
					"Error transforming urls to links", e);
			return null;	// error
		}
	}

}