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

import org.eclipse.wst.xml.vex.core.internal.VEXCorePlugin;
import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.Insets;
import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.core.Rectangle;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * A wrapper for the top level <code>BlockElementBox</code> that applies its
 * margins.
 */
public class RootBox extends AbstractBox implements BlockBox {

	private IVEXElement element;
	private BlockElementBox childBox;
	private Box[] children = new Box[1];

	/**
	 * Class constructor.
	 * 
	 * @param context
	 *            LayoutContext used to create children.
	 * @param element
	 *            Element associated with this box.
	 * @param width
	 *            width of this box
	 */
	public RootBox(LayoutContext context, IVEXElement element, int width) {
		this.element = element;
		this.setWidth(width);

		this.childBox = new BlockElementBox(context, this, this.element);

		Insets insets = this.getInsets(context, this.getWidth());
		this.childBox.setX(insets.getLeft());
		this.childBox.setY(insets.getTop());
		this.childBox.setInitialSize(context);
		this.children[0] = this.childBox;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getCaret(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int)
	 */
	public Caret getCaret(LayoutContext context, int offset) {
		Caret caret = this.childBox.getCaret(context, offset);
		caret.translate(this.childBox.getX(), this.childBox.getY());
		return caret;
	}

	public Box[] getChildren() {
		return this.children;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getElement()
	 */
	public IVEXElement getElement() {
		return this.element;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getEndOffset()
	 */
	public int getEndOffset() {
		return this.childBox.getEndOffset();
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.BlockBox#getFirstLine()
	 */
	public LineBox getFirstLine() {
		return this.childBox.getFirstLine();
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.BlockBox#getLastLine()
	 */
	public LineBox getLastLine() {
		return this.childBox.getLastLine();
	}

	public int getLineEndOffset(int offset) {
		return this.childBox.getLineEndOffset(offset);
	}

	public int getLineStartOffset(int offset) {
		return this.childBox.getLineStartOffset(offset);
	}

	public int getMarginBottom() {
		return 0;
	}

	public int getMarginTop() {
		return 0;
	}

	public int getNextLineOffset(LayoutContext context, int offset, int x) {
		return childBox.getNextLineOffset(context, offset, x - childBox.getX());
	}

	public BlockBox getParent() {
		throw new IllegalStateException("RootBox does not have a parent");
	}

	public int getPreviousLineOffset(LayoutContext context, int offset, int x) {
		return childBox.getPreviousLineOffset(context, offset, x
				- childBox.getX());
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getStartOffset()
	 */
	public int getStartOffset() {
		return this.childBox.getStartOffset();
	}

	public void invalidate(boolean direct) {
		// do nothing. layout is always propagated to our child box.
	}

	public IntRange layout(LayoutContext context, int top, int bottom) {

		Insets insets = this.getInsets(context, this.getWidth());

		long start = 0;
		if (VEXCorePlugin.getInstance().isDebugging()) {
			start = System.currentTimeMillis();
		}

		IntRange repaintRange = this.childBox.layout(context, top
				- insets.getTop(), bottom - insets.getBottom());

		if (VEXCorePlugin.getInstance().isDebugging()) {
			long end = System.currentTimeMillis();
			if (end - start > 50) {
				System.out.println("RootBox.layout took " + (end - start)
						+ "ms");
			}
		}

		this.setHeight(this.childBox.getHeight() + insets.getTop()
				+ insets.getBottom());

		if (repaintRange != null) {
			return new IntRange(repaintRange.getStart() + this.childBox.getY(),
					repaintRange.getEnd() + this.childBox.getY());
		} else {
			return null;
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.wst.xml.vex.core.internal.layout.AbstractBox#viewToModel(
	 * org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext, int, int)
	 */
	public int viewToModel(LayoutContext context, int x, int y) {
		return this.childBox.viewToModel(context, x - this.childBox.getX(), y
				- this.childBox.getY());
	}

	public void paint(LayoutContext context, int x, int y) {
		Rectangle r = context.getGraphics().getClipBounds();
		long start = System.currentTimeMillis();
		super.paint(context, x, y);
		long end = System.currentTimeMillis();
		if (end - start > 50) {
			System.out.println("RootBox.paint " + r.getHeight()
					+ " pixel rows in " + (end - start) + "ms");
		}
	}

	public void setInitialSize(LayoutContext context) {
		throw new IllegalStateException();
	}

}