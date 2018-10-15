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

import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.Color;
import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;
import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.core.Insets;
import org.eclipse.wst.xml.vex.core.internal.core.Rectangle;
import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * Base implementation of the <code>Box</code> interface, implementing some
 * common methods.
 */
public abstract class AbstractBox implements Box {

	private static final Box[] EMPTY_BOX_ARRAY = new Box[0];

	private int x;
	private int y;
	private int width = -1;
	private int height = -1;

	/**
	 * Class constructor.
	 */
	public AbstractBox() {
	}

	/**
	 * Returns true if the given offset is between startOffset and endOffset,
	 * inclusive.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#containsOffset(int)
	 */
	public boolean containsOffset(int offset) {
		return offset >= this.getStartOffset() && offset <= this.getEndOffset();
	}

	/**
	 * Throws <code>IllegalStateException</code>. Boxes with content must
	 * provide an implementation of this method.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getCaret(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int)
	 */
	public Caret getCaret(LayoutContext context, int offset) {
		throw new IllegalStateException();
	}

	/**
	 * Returns an empty array of children.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getChildren()
	 */
	public Box[] getChildren() {
		return EMPTY_BOX_ARRAY;
	}

	/**
	 * Returns null. Boxes associated with elements must provide an
	 * implementation of this method.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getElement()
	 */
	public IVEXElement getElement() {
		return null;
	}

	/**
	 * Throws <code>IllegalStateException</code>. Boxes with content must
	 * provide an implementation of this method.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getEndOffset()
	 */
	public int getEndOffset() {
		throw new IllegalStateException();
	}

	/**
	 * Returns the height set with <code>setHeight</code>.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getHeight()
	 */
	public int getHeight() {
		return this.height;
	}

	/**
	 * Throws <code>IllegalStateException</code>. Boxes with content must
	 * provide an implementation of this method.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getStartOffset()
	 */
	public int getStartOffset() {
		throw new IllegalStateException();
	}

	/**
	 * Returns the insets of this box, which is the sum of the margin, border,
	 * and padding on each side. If no element is associated with this box
	 * returns all zeros.
	 */
	public Insets getInsets(LayoutContext context, int containerWidth) {
		IVEXElement element = this.getElement();
		if (element == null) {
			return Insets.ZERO_INSETS;
		} else {
			return getInsets(context.getStyleSheet().getStyles(element),
					containerWidth);
		}
	}

	/**
	 * Returns false. Boxes with content must override this method and return
	 * true, and must provide implementations for the following methods.
	 * 
	 * <ul>
	 * <li>{@link Box#getCaretShapes}</li>
	 * <li>{@link Box#getStartOffset}</li>
	 * <li>{@link Box#getEndOffset}</li>
	 * <li>{@link Box#viewToModel}</li>
	 * </ul>
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#hasContent()
	 */
	public boolean hasContent() {
		return false;
	}

	public boolean isAnonymous() {
		return true;
	}

	/**
	 * Returns the width set with <code>setWidth</code>.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getWidth()
	 */
	public int getWidth() {
		return this.width;
	}

	/**
	 * Returns the value set with <code>setX</code>.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getX()
	 */
	public int getX() {
		return this.x;
	}

	/**
	 * Returns the value set with <code>setY</code>.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getY()
	 */
	public int getY() {
		return this.y;
	}

	/**
	 * Paint all children of this box.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#paint(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, int)
	 */
	public void paint(LayoutContext context, int x, int y) {

		if (this.skipPaint(context, x, y)) {
			return;
		}

		this.paintChildren(context, x, y);
	}

	/**
	 * Paint the children of this box.
	 * 
	 * @param context
	 *            LayoutContext to use.
	 * @param x
	 *            x-coordinate at which to paint
	 * @param y
	 *            y-coordinate at which to paint
	 */
	protected void paintChildren(LayoutContext context, int x, int y) {
		Box[] children = this.getChildren();
		for (int i = 0; children != null && i < children.length; i++) {
			Box child = children[i];
			child.paint(context, x + child.getX(), y + child.getY());
		}
	}

	public void setHeight(int height) {
		this.height = height;
	}

	public void setWidth(int width) {
		this.width = width;
	}

	public void setX(int x) {
		this.x = x;
	}

	public void setY(int y) {
		this.y = y;
	}

	/**
	 * Returns true if this box is outside the clip region. Implementations of
	 * <code>paint</code> should use this to avoid unnecessary painting.
	 * 
	 * @param context
	 *            <code>LayoutContext</code> in effect.
	 * @param x
	 *            the x-coordinate at which the box is being painted
	 * @param y
	 *            the y-coordinate at which the box is being painted
	 */
	protected boolean skipPaint(LayoutContext context, int x, int y) {
		Rectangle clipBounds = context.getGraphics().getClipBounds();

		return clipBounds.getY() + clipBounds.getHeight() <= y
				|| clipBounds.getY() >= y + this.getHeight();

	}

	/**
	 * Throws <code>IllegalStateException</code>. Boxes with content must
	 * provide an implementation of this method.
	 * 
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#viewToModel(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int, int)
	 */
	public int viewToModel(LayoutContext context, int x, int y) {
		throw new IllegalStateException();
	}

	/**
	 * Draws the background and borders of a CSS-styled box.
	 * 
	 * @param context
	 *            LayoutContext used for drawing.
	 * @param x
	 *            x-coordinate of the left side of the box
	 * @param y
	 *            y-coordinate of the top of the box
	 * @param containerWidth
	 *            width of the containing client area. Used for calculating
	 *            padding expressed as a percentage.
	 * @param drawBorders
	 *            If true, the background is filled and the borders are drawn;
	 *            otherwise, just the background is filled. This is handy when
	 *            removing the borders when drawing the selection frame.
	 */
	protected void drawBox(LayoutContext context, int x, int y,
			int containerWidth, boolean drawBorders) {
		this.drawBox(context, this.getElement(), x, y, containerWidth,
				drawBorders);
	}

	/**
	 * Draws the background and borders of a CSS-styled box.
	 * 
	 * @param context
	 *            LayoutContext used for drawing.
	 * @param element
	 *            Element to use when determining styles. This is used by
	 *            TableBodyBox to specify the corresponding table element.
	 * @param x
	 *            x-coordinate of the left side of the box
	 * @param y
	 *            y-coordinate of the top of the box
	 * @param containerWidth
	 *            width of the containing client area. Used for calculating
	 *            padding expressed as a percentage.
	 * @param drawBorders
	 *            If true, the background is filled and the borders are drawn;
	 *            otherwise, just the background is filled. This is handy when
	 *            removing the borders when drawing the selection frame.
	 */
	protected void drawBox(LayoutContext context, IVEXElement element, int x,
			int y, int containerWidth, boolean drawBorders) {

		if (element == null) {
			return;
		}

		Graphics g = context.getGraphics();
		Styles styles = context.getStyleSheet().getStyles(element);

		boolean hasLeft = true;
		boolean hasRight = true;
		int left = x - styles.getPaddingLeft().get(containerWidth)
				- styles.getBorderLeftWidth();
		int top = y - styles.getPaddingTop().get(containerWidth)
				- styles.getBorderTopWidth();
		int right = x + this.getWidth()
				+ styles.getPaddingRight().get(containerWidth)
				+ styles.getBorderRightWidth();
		int bottom = y + this.getHeight()
				+ styles.getPaddingBottom().get(containerWidth)
				+ styles.getBorderBottomWidth();

		if (this instanceof InlineElementBox) {
			// TODO fix boxes for inline elements
			hasLeft = this.getStartOffset() == element.getStartOffset() + 1;
			hasRight = this.getEndOffset() == element.getEndOffset();
			if (hasLeft) {
				// left += styles.getMarginLeft().get(0);
			}
			if (hasRight) {
				// right -= styles.getMarginRight().get(0);
			}
			// top = y - styles.getPaddingTop().get(0) -
			// styles.getBorderTopWidth();
			// bottom = y + box.getHeight() + styles.getPaddingBottom().get(0) +
			// styles.getBorderBottomWidth();
		}

		Color backgroundColor = styles.getBackgroundColor();

		if (backgroundColor != null) {
			ColorResource color = g.createColor(backgroundColor);
			ColorResource oldColor = g.setColor(color);
			g.fillRect(left, top, right - left, bottom - top);
			g.setColor(oldColor);
			color.dispose();
		}

		if (drawBorders) {
			// Object oldAntiAlias =
			// g.getRenderingHint(RenderingHints.KEY_ANTIALIASING);
			//
			// g.setRenderingHint(
			// RenderingHints.KEY_ANTIALIASING,
			// RenderingHints.VALUE_ANTIALIAS_OFF);
			boolean oldAntiAlias = g.isAntiAliased();
			g.setAntiAliased(false);

			int bw2 = styles.getBorderBottomWidth() / 2;
			int lw2 = styles.getBorderLeftWidth() / 2;
			int rw2 = styles.getBorderRightWidth() / 2;
			int tw2 = styles.getBorderTopWidth() / 2;

			// Bottom border
			if (styles.getBorderBottomWidth() > 0) {
				ColorResource color = g.createColor(styles
						.getBorderBottomColor());
				ColorResource oldColor = g.setColor(color);
				g.setLineStyle(lineStyle(styles.getBorderBottomStyle()));
				g.setLineWidth(styles.getBorderBottomWidth());
				g.drawLine(left + bw2, bottom - bw2 - 1, right - bw2, bottom
						- bw2 - 1);
				g.setColor(oldColor);
				color.dispose();
			}

			// Left border
			if (hasLeft && styles.getBorderLeftWidth() > 0) {
				ColorResource color = g
						.createColor(styles.getBorderLeftColor());
				ColorResource oldColor = g.setColor(color);
				g.setLineStyle(lineStyle(styles.getBorderLeftStyle()));
				g.setLineWidth(styles.getBorderLeftWidth());
				g.drawLine(left + lw2, top + lw2, left + lw2, bottom - lw2 - 1);
				g.setColor(oldColor);
				color.dispose();
			}

			// Right border
			if (hasRight && styles.getBorderRightWidth() > 0) {
				ColorResource color = g.createColor(styles
						.getBorderRightColor());
				ColorResource oldColor = g.setColor(color);
				g.setLineStyle(lineStyle(styles.getBorderRightStyle()));
				g.setLineWidth(styles.getBorderRightWidth());
				g.drawLine(right - rw2 - 1, top + rw2, right - rw2 - 1, bottom
						- rw2 - 1);
				g.setColor(oldColor);
				color.dispose();
			}

			// Top border
			if (styles.getBorderTopWidth() > 0) {
				ColorResource color = g.createColor(styles.getBorderTopColor());
				ColorResource oldColor = g.setColor(color);
				g.setLineStyle(lineStyle(styles.getBorderTopStyle()));
				g.setLineWidth(styles.getBorderTopWidth());
				g.drawLine(left + tw2, top + tw2, right - tw2, top + tw2);
				g.setColor(oldColor);
				color.dispose();
			}

			// g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,
			// oldAntiAlias);
			g.setAntiAliased(oldAntiAlias);

		}
	}

	/**
	 * Convert a CSS line style string (e.g. "dotted") to the corresponding
	 * Graphics.LINE_XXX style.
	 */
	private static int lineStyle(String style) {
		if (style.equals(CSS.DOTTED)) {
			return Graphics.LINE_DOT;
		} else if (style.equals(CSS.DASHED)) {
			return Graphics.LINE_DASH;
		} else {
			return Graphics.LINE_SOLID;
		}

	}

	/**
	 * Returns the insets for a CSS box with the given styles.
	 * 
	 * @param styles
	 *            Styles for the box.
	 * @param containerWidth
	 *            Content area of the containing box.
	 */
	public static Insets getInsets(Styles styles, int containerWidth) {

		int top = styles.getMarginTop().get(containerWidth)
				+ styles.getBorderTopWidth()
				+ styles.getPaddingTop().get(containerWidth);

		int left = styles.getMarginLeft().get(containerWidth)
				+ styles.getBorderLeftWidth()
				+ styles.getPaddingLeft().get(containerWidth);

		int bottom = styles.getMarginBottom().get(containerWidth)
				+ styles.getBorderBottomWidth()
				+ styles.getPaddingBottom().get(containerWidth);

		int right = styles.getMarginRight().get(containerWidth)
				+ styles.getBorderRightWidth()
				+ styles.getPaddingRight().get(containerWidth);

		return new Insets(top, left, bottom, right);
	}

}