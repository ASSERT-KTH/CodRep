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

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * A box that wraps inline content into a paragraph.
 */
public class ParagraphBox extends AbstractBox implements BlockBox {

	private LineBox[] children;
	private LineBox firstContentLine;
	private LineBox lastContentLine;

	/**
	 * Class constructor.
	 * 
	 * @param children
	 *            Line boxes that comprise the paragraph.
	 */
	private ParagraphBox(LineBox[] children) {
		this.children = children;
		for (int i = 0; i < children.length; i++) {
			if (children[i].hasContent()) {
				if (this.firstContentLine == null) {
					this.firstContentLine = children[i];
				}
				this.lastContentLine = children[i];
			}
		}
	}

	/**
	 * Create a paragraph by word-wrapping a list of inline boxes.
	 * 
	 * @param context
	 *            LayoutContext used for this layout.
	 * @param element
	 *            Element that controls the styling for this paragraph.
	 * @param inlines
	 *            List of InlineBox objects to be wrapped
	 * @param width
	 *            width to which the paragraph is to be wrapped
	 * @return
	 */
	public static ParagraphBox create(LayoutContext context, IVEXElement element,
			List inlines, int width) {
		InlineBox[] array = (InlineBox[]) inlines.toArray(new InlineBox[inlines
				.size()]);
		return create(context, element, array, width);
	}

	/**
	 * Create a paragraph by word-wrapping a list of inline boxes.
	 * 
	 * @param context
	 *            LayoutContext used for this layout
	 * @param element
	 *            IVEXElement that controls the styling of this paragraph, in
	 *            particular text alignment.
	 * @param inlines
	 *            Array of InlineBox objects to be wrapped.
	 * @param width
	 *            width to which the paragraph is to be wrapped.
	 */
	public static ParagraphBox create(LayoutContext context, IVEXElement element,
			InlineBox[] inlines, int width) {

		// lines is the list of LineBoxes we are creating
		List lines = new ArrayList();

		InlineBox right = new LineBox(context, element, inlines);

		while (right != null) {
			InlineBox.Pair pair = right.split(context, width, true);
			lines.add(pair.getLeft());
			right = pair.getRight();
		}

		Styles styles = context.getStyleSheet().getStyles(element);
		String textAlign = styles.getTextAlign();

		// y-offset of the next line
		int y = 0;

		int actualWidth = 0;

		for (Iterator it = lines.iterator(); it.hasNext();) {

			LineBox lineBox = (LineBox) it.next();

			int x;
			if (textAlign.equals(CSS.RIGHT)) {
				x = width - lineBox.getWidth();
			} else if (textAlign.equals(CSS.CENTER)) {
				x = (width - lineBox.getWidth()) / 2;
			} else {
				x = 0;
			}

			lineBox.setX(x);
			lineBox.setY(y);

			y += lineBox.getHeight();
			actualWidth = Math.max(actualWidth, lineBox.getWidth());
		}

		LineBox[] children = (LineBox[]) lines
				.toArray(new LineBox[lines.size()]);

		ParagraphBox para = new ParagraphBox(children);
		para.setWidth(actualWidth);
		para.setHeight(y);

		// BlockElementBox uses a scaling factor to estimate box height based
		// on font size, layout width, and character count, as follows.
		//
		// estHeight = factor * fontSize * fontSize * charCount / width
		//
		// This bit reports the actual factor that would correctly estimate
		// the height of a BlockElementBox containing only this paragraph.
		//
		// factor = estHeight * width / (fontSize * fontSize * charCount)
		//
		/*
		 * Box firstContentBox = null; for (int i = 0; i < inlines.length; i++)
		 * { Box box = inlines[i]; if (box.hasContent()) { firstContentBox =
		 * box; break; } }
		 * 
		 * if (firstContentBox != null) { float fontSize = styles.getFontSize();
		 * int charCount = lastContentBox.getEndOffset() -
		 * firstContentBox.getStartOffset(); float factor = para.getHeight()
		 * para.getWidth() / (fontSize fontSize charCount);
		 * System.out.println("Actual factor is " + factor); }
		 */

		return para;
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.Box#getCaret(org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext,
	 *      int)
	 */
	public Caret getCaret(LayoutContext context, int offset) {

		LineBox line = this.getLineAt(offset);
		Caret caret = line.getCaret(context, offset);
		caret.translate(line.getX(), line.getY());
		return caret;

	}

	public Box[] getChildren() {
		return this.children;
	}

	public int getEndOffset() {
		return this.lastContentLine.getEndOffset();
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.BlockBox#getFirstLine()
	 */
	public LineBox getFirstLine() {
		if (this.children.length == 0) {
			return null;
		} else {
			return this.children[0];
		}
	}

	/**
	 * @see org.eclipse.wst.xml.vex.core.internal.layout.BlockBox#getLastLine()
	 */
	public LineBox getLastLine() {
		if (this.children.length == 0) {
			return null;
		} else {
			return this.children[this.children.length - 1];
		}
	}

	/**
	 * Returns the LineBox at the given offset.
	 * 
	 * @param offset
	 *            the offset to check.
	 */
	public LineBox getLineAt(int offset) {
		LineBox[] children = this.children;
		for (int i = 0; i < children.length; i++) {
			if (children[i].hasContent()
					&& offset <= children[i].getEndOffset()) {
				return children[i];
			}
		}
		return this.lastContentLine;
	}

	public int getLineEndOffset(int offset) {
		return this.getLineAt(offset).getEndOffset();
	}

	public int getLineStartOffset(int offset) {
		return this.getLineAt(offset).getStartOffset();
	}

	public int getMarginBottom() {
		return 0;
	}

	public int getMarginTop() {
		return 0;
	}

	public int getNextLineOffset(LayoutContext context, int offset, int x) {
		LineBox nextLine = null;
		LineBox[] children = this.children;
		for (int i = 0; i < children.length; i++) {
			if (children[i].hasContent()
					&& children[i].getStartOffset() > offset) {
				nextLine = children[i];
				break;
			}
		}
		if (nextLine == null) {
			// return this.getEndOffset() + 1;
			return -1;
		} else {
			return nextLine.viewToModel(context, x - nextLine.getX(), 0);
		}
	}

	public BlockBox getParent() {
		throw new IllegalStateException(
				"ParagraphBox does not currently track parent");
	}

	public int getPreviousLineOffset(LayoutContext context, int offset, int x) {
		LineBox prevLine = null;
		LineBox[] children = this.children;
		for (int i = children.length - 1; i >= 0; i--) {
			if (children[i].hasContent() && children[i].getEndOffset() < offset) {
				prevLine = children[i];
				break;
			}
		}
		if (prevLine == null) {
			// return this.getStartOffset() - 1;
			return -1;
		} else {
			return prevLine.viewToModel(context, x - prevLine.getX(), 0);
		}
	}

	public int getStartOffset() {
		return this.firstContentLine.getStartOffset();
	}

	public boolean hasContent() {
		return this.firstContentLine != null;
	}

	public IntRange layout(LayoutContext context, int top, int bottom) {
		return null;
	}

	public void invalidate(boolean direct) {
		throw new IllegalStateException(
				"invalidate called on a non-element BlockBox");
	}

	public void setInitialSize(LayoutContext context) {
		// NOP - size calculated in factory method
	}

	public String toString() {
		return "ParagraphBox";
	}

	public int viewToModel(LayoutContext context, int x, int y) {

		LineBox[] children = this.children;
		for (int i = 0; i < children.length; i++) {
			Box child = children[i];
			if (child.hasContent() && y <= child.getY() + child.getHeight()) {
				return child.viewToModel(context, x - child.getX(), y
						- child.getY());
			}
		}
		throw new RuntimeException("No line at (" + x + ", " + y + ")");
	}

	// ===================================================== PRIVATE

}