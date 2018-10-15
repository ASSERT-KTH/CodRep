package org.eclipse.wst.xml.vex.ui.internal.swt;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.swt;

import org.eclipse.swt.events.KeyEvent;

/**
 * Represents a keystroke and a certain set of modifiers.
 */
public class KeyStroke {

	private char character;
	private int keyCode;
	private int stateMask;

	/**
	 * Class constructor.
	 * 
	 * @param character
	 *            the key character
	 * @param keyCode
	 *            the key code
	 * @param stateMask
	 *            the set of modifiers
	 */
	public KeyStroke(char character, int keyCode, int stateMask) {
		this.character = character;
		this.keyCode = keyCode;
		this.stateMask = stateMask;
	}

	/**
	 * Class constructor.
	 * 
	 * @param e
	 *            a KeyEvent representing the key stroke
	 */
	public KeyStroke(KeyEvent e) {
		this.character = e.character;
		this.keyCode = e.keyCode;
		this.stateMask = e.stateMask;
	}

	public boolean equals(Object o) {
		if (o == null || !(o instanceof KeyStroke)) {
			return false;
		}
		KeyStroke other = (KeyStroke) o;
		return this.character == other.character
				&& this.keyCode == other.keyCode
				&& this.stateMask == other.stateMask;
	}

	public int hashCode() {
		return this.character + this.keyCode + this.stateMask;
	}

}