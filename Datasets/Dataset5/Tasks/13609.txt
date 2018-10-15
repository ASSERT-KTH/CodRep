public int getLengthOfReplacedText() {

/****************************************************************************
 * Copyright (c) 2007, 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *    Mustafa K. Isik
 *****************************************************************************/

package org.eclipse.ecf.docshare.messages;

/**
 * 
 */
public class UpdateMessage extends Message {

	private static final long serialVersionUID = -3195542805471664496L;

	final String text;
	int offset;
	int length;

	public UpdateMessage(int offset, int length, String text) {
		this.offset = offset;
		this.length = length;
		this.text = text;
	}

	/**
	 * Returns the modification index of the operation resembled by this
	 * message.
	 * 
	 * @return modification index
	 */
	public int getOffset() {
		return offset;
	}

	public void setOffset(int updatedOffset) {
		this.offset = updatedOffset;
	}

	/**
	 * Returns the length of replaced text.
	 * 
	 * @return length of replaced text
	 */
	public int getLength() {
		return length;
	}

	public void setLength(int length) {
		this.length = length;
	}

	public String getText() {
		return text;
	}

	public String toString() {
		StringBuffer buf = new StringBuffer("UpdateMessage["); //$NON-NLS-1$
		buf.append("text=").append(text).append(";offset=").append(offset); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append(";length=").append(length).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
		return buf.toString();
	}

}