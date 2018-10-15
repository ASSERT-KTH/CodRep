import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IVEXElement;

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

import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.Drawable;
import org.eclipse.wst.xml.vex.core.internal.core.FontMetrics;
import org.eclipse.wst.xml.vex.core.internal.core.FontResource;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.core.Rectangle;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * An inline box that draws a Drawable object. The drawable is drawn relative to
 * the text baseline, therefore it should draw using mostly negative
 * y-coordinates.
 */
public class DrawableBox extends AbstractBox implements InlineBox {

	public static final byte NO_MARKER = 0;
	public static final byte START_MARKER = 1;
	public static final byte END_MARKER = 2;

	private Drawable drawable;
	private IVEXElement element;
	private byte marker;

	/**
	 * Class constructor.
	 * 
	 * @param drawable
	 *            Drawable to draw.
	 * @param element2
	 *            Element whose styles determine the color of the drawable.
	 */
	public DrawableBox(Drawable drawable, IVEXElement element2) {
		this(drawable, element2, NO_MARKER);
	}

	/**
	 * Class constructor. This constructor is called when creating a DrawableBox
	 * that represents the start or end marker of an inline element.
	 * 
	 * @param drawable
	 *            Drawable to draw.
	 * @param element2
	 *            Element whose styles determine the color of the drawable.
	 * @param marker
	 *            which marker should be drawn. Must be one of NO_MARKER,
	 *            START_MARKER, or END_MARKER.
	 */
	public DrawableBox(Drawable drawable, IVEXElement element2, byte marker) {
		this.drawable = drawable;
		this.element = element2;
		this.marker = marker;
		Rectangle bounds = drawable.getBounds();
		this.setWidth(bounds.getWidth());
		this.setHeight(bounds.getHeight());
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.InlineBox#getBaseline()
	 */
	public int getBaseline() {
		return 0;
	}

	/**
	 * Returns the element that controls the styling for this text element.
	 */
	public IVEXElement getElement() {
		return this.element;
	}

	public boolean isEOL() {
		return false;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.InlineBox#split(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, boolean)
	 */
	public Pair split(LayoutContext context, int maxWidth, boolean force) {
		return new Pair(null, this);
	}

	/**
	 * Draw the drawable. The foreground color of the context's Graphics is set
	 * before calling the drawable's draw method.
	 */
	public void paint(LayoutContext context, int x, int y) {

		Graphics g = context.getGraphics();
		Styles styles = context.getStyleSheet().getStyles(this.element);

		boolean drawSelected = false;
		if (this.marker == START_MARKER) {
			drawSelected = this.getElement().getStartOffset() >= context
					.getSelectionStart()
					&& this.getElement().getStartOffset() + 1 <= context
							.getSelectionEnd();
		} else if (this.marker == END_MARKER) {
			drawSelected = this.getElement().getEndOffset() >= context
					.getSelectionStart()
					&& this.getElement().getEndOffset() + 1 <= context
							.getSelectionEnd();
		}

		FontResource font = g.createFont(styles.getFont());
		ColorResource color = g.createColor(styles.getColor());

		FontResource oldFont = g.setFont(font);
		ColorResource oldColor = g.setColor(color);

		FontMetrics fm = g.getFontMetrics();

		if (drawSelected) {
			Rectangle bounds = this.drawable.getBounds();
			g.setColor(g.getSystemColor(ColorResource.SELECTION_BACKGROUND));
			g.fillRect(x + bounds.getX(), y - fm.getAscent(),
					bounds.getWidth(), styles.getLineHeight());
			g.setColor(g.getSystemColor(ColorResource.SELECTION_FOREGROUND));
		}

		this.drawable.draw(g, x, y);

		g.setFont(oldFont);
		g.setColor(oldColor);
		font.dispose();
		color.dispose();
	}

	/**
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		return "[shape]";
	}

}