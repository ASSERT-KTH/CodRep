package org.jhotdraw.util;

/*
 * @(#)Clipboard.java
 *
 * Project:		JHotdraw - a GUI framework for technical drawings
 *				http://www.jhotdraw.org
 *				http://jhotdraw.sourceforge.net
 * Copyright:	© by the original author(s) and all contributors
 * License:		Lesser GNU Public License (LGPL)
 *				http://www.opensource.org/licenses/lgpl-license.html
 */

package CH.ifa.draw.util;

/**
 * A temporary replacement for a global clipboard.
 * It is a singleton that can be used to store and
 * get the contents of the clipboard.
 *
 * @version <$CURRENT_VERSION$>
 */
public class Clipboard {
	static Clipboard fgClipboard = new Clipboard();

	/**
	 * Gets the clipboard.
	 */
	static public Clipboard getClipboard() {
		return fgClipboard;
	}

	private Object fContents;

	private Clipboard() {
	}

	/**
	 * Sets the contents of the clipboard.
	 */
	public void setContents(Object contents) {
		fContents = contents;
	}

	/**
	 * Gets the contents of the clipboard.
	 */
	public Object getContents() {
		return fContents;
	}
}