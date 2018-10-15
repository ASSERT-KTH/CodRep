public Text(IContent content, int startOffset, int endOffset) {

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
package org.eclipse.wst.xml.vex.core.internal.dom;

/**
 * <code>Text</code> represents a run of text in a document. Text objects are
 * not used in the internal document structure; they are only returned as needed
 * by the <code>Element.getContent</code> method.
 */
public class Text extends Node {

	/**
	 * Class constructor.
	 * 
	 * @param content
	 *            Content object containing the text
	 * @param startOffset
	 *            character offset of the start of the run
	 * @param endOffset
	 *            character offset of the end of the run
	 */
	public Text(Content content, int startOffset, int endOffset) {
		this.setContent(content, startOffset, endOffset);
	}

}