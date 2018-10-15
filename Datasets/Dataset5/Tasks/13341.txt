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
import org.eclipse.wst.xml.vex.core.internal.core.Insets;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * Represents a rectangular area in the layout. The height and width of the box
 * are measured from the inner edges of the box's padding, as in CSS. Similarly,
 * the (x, y) position of the box are with respect to the inner top-left corner
 * of the box's padding, and are relative to the parent's (x, y) position.
 */
public interface Box {

	/**
	 * Returns true if this box contains the given offset.
	 * 
	 * @param offset
	 *            the offset to test
	 */
	public boolean containsOffset(int offset);

	/**
	 * Returns a Caret object representing the given offset.
	 * 
	 * @param context
	 *            LayoutContext to be used
	 * @param offset
	 *            offset for which to retrieve the caret
	 */
	public Caret getCaret(LayoutContext context, int offset);

	/**
	 * Returns an array of this box's children.
	 */
	public Box[] getChildren();

	/**
	 * Returns the Element with which this box is associated, or null if there
	 * is no such box. The box may directly represent the Element, or simply use
	 * it for formatting information.
	 */
	public IVEXElement getElement();

	/**
	 * Returns the offset of the end of the content that the box covers.
	 */
	public int getEndOffset();

	/**
	 * Returns the height of the box. For boxes subject to the CSS box model,
	 * this is the inner height, exclusive of margins, borders, and padding.
	 */
	public int getHeight();

	/**
	 * Return an Insets object representing the total width of margins, borders,
	 * and padding for this box.
	 * 
	 * @param context
	 *            LayoutContext being used for this layout.
	 * @param containerWidth
	 *            Width of the containing box.
	 */
	public Insets getInsets(LayoutContext context, int containerWidth);

	/**
	 * Returns the offset of the start of the content that the box covers.
	 */
	public int getStartOffset();

	/**
	 * Returns the width of the box. For boxes subject to the CSS box model,
	 * this is the inner width, exclusive of margins, borders, and padding.
	 */
	public int getWidth();

	/**
	 * Returns the x-coordinate of the box, relative to its parent. For boxes
	 * subject to the CSS box model, this is the left edge of the box's content
	 * area.
	 */
	public int getX();

	/**
	 * Returns the y-coordinate of the box, relative to its parent. For boxes
	 * subject to the CSS box model, this is the top edge of the box's content
	 * area.
	 */
	public int getY();

	/**
	 * Returns true if this box represents a portion of the XML document's
	 * content. If false is returned, the following methods are not supported by
	 * this box.
	 * 
	 * <ul>
	 * <li>getCaretShapes()</li>
	 * <li>getEndOffset()</li>
	 * <li>getStartOffset()</li>
	 * <li>viewToModel()</li>
	 * </ul>
	 */
	public boolean hasContent();

	/**
	 * Returns true if the box is anonymous, that is, it is not directly
	 * associated with an element.
	 */
	public boolean isAnonymous();

	/**
	 * Draws the box's content in the given Graphics context.
	 * 
	 * @param context
	 *            <code>LayoutContext</code> containing the
	 *            <code>Graphics</code> object into which the box should be
	 *            painted
	 * @param x
	 *            the x-offset at which the box should be painted
	 * @param y
	 *            the y-offset at which the box should be painted
	 */
	public void paint(LayoutContext context, int x, int y);

	/**
	 * Sets the height of this box.
	 * 
	 * @param height
	 *            new height of the box
	 */
	public void setHeight(int height);

	/**
	 * Sets the width of this box.
	 * 
	 * @param width
	 *            new width of the box
	 */
	public void setWidth(int width);

	/**
	 * Sets the x-coordinate of the top-left corner of the box.
	 * 
	 * @param x
	 *            the new x-coordinate
	 */
	public void setX(int x);

	/**
	 * Sets the y-coordinate of the top-left corner of the box.
	 * 
	 * @param y
	 *            the new y-coordinate
	 */
	public void setY(int y);

	/**
	 * Returns the offset in the content closest to the given view position.
	 * 
	 * @param context
	 *            <code>LayoutContext</code> for this box tree
	 * @param x
	 *            x offset of the view position for which the model offset is to
	 *            be determined.
	 * @param y
	 *            y offset of the view position for which the model offset is to
	 *            be determined.
	 */
	public int viewToModel(LayoutContext context, int x, int y);

}