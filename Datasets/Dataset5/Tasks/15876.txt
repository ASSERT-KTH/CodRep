return string.substring(0, index) + replace + replaceAll(string.substring(index + target.length()), target, replace);

/*******************************************************************************
 * Copyright (c) 2005, 2007 Remy Suen
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.util;

import java.util.ArrayList;

/**
 * <p>
 * The StringUtils class provides static methods that helps make string
 * manipulation easy. The primary functionality it is meant to provide is the
 * ability to split a string into a string array based on a given delimiter.
 * This functionality is meant to take the place of the split(String) and
 * split(String, int) method that was introduced in J2SE-1.4. Please note,
 * however, that the splitting performed by this class simply splits the string
 * based on the delimiter and does not perform any regular expression matching
 * like the split methods provided in J2SE-1.4.
 * </p>
 * 
 */
public final class StringUtils {

	public static final String[] splitOnSpace(String string) {
		int index = string.indexOf(' ');
		if (index == -1) {
			return new String[] {string};
		}

		ArrayList split = new ArrayList();
		while (index != -1) {
			split.add(string.substring(0, index));
			string = string.substring(index + 1);
			index = string.indexOf(' ');
		}

		if (!string.equals("")) { //$NON-NLS-1$
			split.add(string);
		}

		return (String[]) split.toArray(new String[split.size()]);
	}

	public static final String[] split(String string, char character) {
		int index = string.indexOf(character);
		if (index == -1) {
			return new String[] {string};
		}

		ArrayList split = new ArrayList();
		while (index != -1) {
			split.add(string.substring(0, index));
			string = string.substring(index + 1);
			index = string.indexOf(character);
		}

		if (!string.equals("")) { //$NON-NLS-1$
			split.add(string);
		}

		return (String[]) split.toArray(new String[split.size()]);
	}

	public static final String[] split(String string, String delimiter) {
		int index = string.indexOf(delimiter);
		if (index == -1) {
			return new String[] {string};
		}

		int length = delimiter.length();
		ArrayList split = new ArrayList();
		while (index != -1) {
			split.add(string.substring(0, index));
			string = string.substring(index + length);
			index = string.indexOf(delimiter);
		}

		if (!string.equals("")) { //$NON-NLS-1$
			split.add(string);
		}

		return (String[]) split.toArray(new String[split.size()]);
	}

	public static final String[] split(String string, String delimiter, int limit) {
		int index = string.indexOf(delimiter);
		if (index == -1) {
			return new String[] {string};
		}

		int count = 0;
		int length = delimiter.length();
		ArrayList split = new ArrayList(limit);
		while (index != -1 && count < limit - 1) {
			split.add(string.substring(0, index));
			string = string.substring(index + length);
			index = string.indexOf(delimiter);
			count++;
		}

		if (!string.equals("")) { //$NON-NLS-1$
			split.add(string);
		}

		return (String[]) split.toArray(new String[split.size()]);
	}

	public static final String splitSubstring(String string, String delimiter, int pos) {
		int index = string.indexOf(delimiter);
		if (index == -1) {
			return string;
		}

		int count = 0;
		int length = delimiter.length();
		while (count < pos) {
			string = string.substring(index + length);
			index = string.indexOf(delimiter);
			count++;
		}

		return index == -1 ? string : string.substring(0, index);
	}

	public static final String xmlDecode(String string) {
		if (string.equals("")) { //$NON-NLS-1$
			return string;
		}

		int index = string.indexOf("&amp;"); //$NON-NLS-1$
		while (index != -1) {
			string = string.substring(0, index) + '&' + string.substring(index + 5);
			index = string.indexOf("&amp;", index + 1); //$NON-NLS-1$
		}

		index = string.indexOf("&quot;"); //$NON-NLS-1$
		while (index != -1) {
			string = string.substring(0, index) + '"' + string.substring(index + 6);
			index = string.indexOf("&quot;", index + 1); //$NON-NLS-1$
		}

		index = string.indexOf("&apos;"); //$NON-NLS-1$
		while (index != -1) {
			string = string.substring(0, index) + '\'' + string.substring(index + 6);
			index = string.indexOf("&apos;", index + 1); //$NON-NLS-1$
		}

		index = string.indexOf("&lt;"); //$NON-NLS-1$
		while (index != -1) {
			string = string.substring(0, index) + '<' + string.substring(index + 4);
			index = string.indexOf("&lt;", index + 1); //$NON-NLS-1$
		}

		index = string.indexOf("&gt;"); //$NON-NLS-1$
		while (index != -1) {
			string = string.substring(0, index) + '>' + string.substring(index + 4);
			index = string.indexOf("&gt;", index + 1); //$NON-NLS-1$
		}
		return string;
	}

	public static final String xmlEncode(String string) {
		if (string.equals("")) { //$NON-NLS-1$
			return string;
		}

		int index = string.indexOf('&');
		while (index != -1) {
			string = string.substring(0, index) + "&amp;" //$NON-NLS-1$
					+ string.substring(index + 1);
			index = string.indexOf('&', index + 1);
		}

		index = string.indexOf('"');
		while (index != -1) {
			string = string.substring(0, index) + "&quot;" //$NON-NLS-1$
					+ string.substring(index + 1);
			index = string.indexOf('"', index + 1);
		}

		index = string.indexOf('\'');
		while (index != -1) {
			string = string.substring(0, index) + "&apos;" //$NON-NLS-1$
					+ string.substring(index + 1);
			index = string.indexOf('\'', index + 1);
		}

		index = string.indexOf('<');
		while (index != -1) {
			string = string.substring(0, index) + "&lt;" //$NON-NLS-1$
					+ string.substring(index + 1);
			index = string.indexOf('<', index + 1);
		}

		index = string.indexOf('>');
		while (index != -1) {
			string = string.substring(0, index) + "&gt;" //$NON-NLS-1$
					+ string.substring(index + 1);
			index = string.indexOf('>', index + 1);
		}
		return string;
	}

	/**
	 * Returns whether the first parameter contains the second parameter.
	 * @param string must not be <code>.
	 * @param target must not be <code> null.
	 * @return true if the target is contained within the string. 
	 */
	public static boolean contains(String string, String target) {
		return (string.indexOf(target) != -1);
	}

	/**
	 * Returns the string resulting from replacing all occurrences of the target with the replace
	 * string.  Note that the target matches literally, and this is not the same behavior as the 
	 * String.replaceAll, which uses regular expressions for doing the matching.  
	 * @param string the start string.  Must not be <code>null</code>.
	 * @param target the target to search for in the start string.  Must not be <code>null</code>.
	 * @param replace the replacement string to substitute when the target is found.  Must not be <code>null</code>.
	 * @return String result.  Will not be <code>null</code>.   If target is not found in the given string,
	 * then the result will be the entire input string.  
	 */
	public static String replaceAll(String string, String target, String replace) {
		final int index = string.indexOf(target);
		if (index == -1)
			return string;
		return string.substring(0, index) + replace + replaceAll(string.substring(index + replace.length()), target, replace);
	}
}