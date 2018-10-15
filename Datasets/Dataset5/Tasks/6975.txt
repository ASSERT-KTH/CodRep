package org.eclipse.ecf.docshare.messages;

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.provisional.docshare.messages;

/**
 *
 */
public class SelectionMessage extends Message {

	private static final long serialVersionUID = 6451633617366707234L;

	int offset;
	int length;
	int startLine;
	int endLine;

	public SelectionMessage(int offset, int length, int startLine, int endLine) {
		super();
		this.offset = offset;
		this.length = length;
		this.startLine = startLine;
		this.endLine = endLine;
	}

	public SelectionMessage(int offset, int length) {
		this(offset, length, -1, -1);
	}

	/**
	 * @return the offset
	 */
	public int getOffset() {
		return offset;
	}

	/**
	 * @return the length
	 */
	public int getLength() {
		return length;
	}

	/**
	 * @return the startLine
	 */
	public int getStartLine() {
		return startLine;
	}

	/**
	 * @return the endLine
	 */
	public int getEndLine() {
		return endLine;
	}

}