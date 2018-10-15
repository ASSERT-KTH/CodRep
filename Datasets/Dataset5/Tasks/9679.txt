import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;

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
package org.eclipse.wst.xml.vex.core.internal.layout;

import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.FontMetrics;
import org.eclipse.wst.xml.vex.core.internal.core.FontResource;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;

/**
 * A zero-width box that represents a single offset in the document.
 */
public class PlaceholderBox extends AbstractBox implements InlineBox {

	private VEXElement element;
	private int relOffset;
	private int textTop;
	private int baseline;

	/**
	 * Class constructor.
	 * 
	 * @param context
	 *            LayoutContext in effect.
	 * @param element2
	 *            Element containing this placeholder. the element is used both
	 *            to determine the size of the box and its caret, but also as a
	 *            base point for relOffset.
	 * @param relOffset
	 *            Offset of the placeholder, relative to the start of the
	 *            element.
	 */
	public PlaceholderBox(LayoutContext context, VEXElement element2, int relOffset) {

		this.element = element2;
		this.relOffset = relOffset;

		this.setWidth(0);

		Graphics g = context.getGraphics();
		Styles styles = context.getStyleSheet().getStyles(element2);
		FontResource font = g.createFont(styles.getFont());
		FontResource oldFont = g.setFont(font);
		FontMetrics fm = g.getFontMetrics();
		int height = fm.getAscent() + fm.getDescent();

		int lineHeight = styles.getLineHeight();
		this.textTop = (lineHeight - height) / 2;

		this.baseline = this.textTop + fm.getAscent();
		this.setHeight(lineHeight);
		g.setFont(oldFont);
		font.dispose();
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.InlineBox#getBaseline()
	 */
	public int getBaseline() {
		return this.baseline;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.InlineBox#split(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, boolean)
	 */
	public Pair split(LayoutContext context, int maxWidth, boolean force) {
		return new Pair(null, this);
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getCaret(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int)
	 */
	public Caret getCaret(LayoutContext context, int offset) {
		return new TextCaret(0, this.textTop, this.baseline - this.textTop);
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getElement()
	 */
	public VEXElement getElement() {
		return this.element;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getEndOffset()
	 */
	public int getEndOffset() {
		return this.element.getStartOffset() + this.relOffset;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getStartOffset()
	 */
	public int getStartOffset() {
		return this.element.getStartOffset() + this.relOffset;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#hasContent()
	 */
	public boolean hasContent() {
		return true;
	}

	public boolean isEOL() {
		return false;
	}

	/**
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		return "[placeholder(" + this.getStartOffset() + ")]";
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#viewToModel(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, int)
	 */
	public int viewToModel(LayoutContext context, int x, int y) {
		return this.getStartOffset();
	}

}