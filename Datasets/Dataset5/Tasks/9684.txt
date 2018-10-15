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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.core.Caret;
import org.eclipse.wst.xml.vex.core.internal.core.Insets;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;

/**
 * Box representing a row in a table.
 */
public class TableRowBox extends AbstractBlockBox {

	public TableRowBox(LayoutContext context, TableRowGroupBox parent,
			Element element) {
		super(context, parent, element);
	}

	public TableRowBox(LayoutContext context, BlockBox parent, int startOffset,
			int endOffset) {
		super(context, parent, startOffset, endOffset);
	}

	protected List createChildren(final LayoutContext context) {

		final List children = new ArrayList();

		VEXElement element = this.findContainingElement();
		final int[] widths = this.getTableBox().getColumnWidths();

		LayoutUtils.iterateTableCells(context.getStyleSheet(), element, this
				.getStartOffset(), this.getEndOffset(),
				new ElementOrRangeCallback() {
					private int column = 0;

					public void onElement(Element child, String displayStyle) {
						children.add(new TableCellBox(context,
								TableRowBox.this, child, widths[column++]));
					}

					public void onRange(VEXElement parent, int startOffset,
							int endOffset) {
						children.add(new TableCellBox(context,
								TableRowBox.this, startOffset, endOffset,
								widths[column++]));
					}
				});

		return children;
	}

	/**
	 * Override drawBox to do nothing. Table rows have no borders in
	 * border-collapse:separate mode.
	 */
	public void drawBox(LayoutContext context, int x, int y,
			int containerWidth, boolean drawBorders) {
	}

	public Caret getCaret(LayoutContext context, int offset) {

		int hSpacing = this.getTableBox().getHorizonalSpacing();

		Box[] children = this.getChildren();

		// If we haven't yet laid out this block, estimate the caret.
		if (children == null) {
			int relative = offset - this.getStartOffset();
			int size = this.getEndOffset() - this.getStartOffset();
			int y = 0;
			if (size > 0) {
				y = this.getHeight() * relative / size;
			}
			return new HCaret(0, y, this.getWidth());
		}

		int x = hSpacing / 2;

		int[] widths = this.getTableBox().getColumnWidths();

		for (int i = 0; i < children.length; i++) {

			Box child = children[i];

			if (!child.hasContent()) {
				continue; // TODO can we really have generated table cells?
			}

			if (offset < child.getStartOffset()) {
				return new TextCaret(x, 0, this.getHeight());
			}

			if (offset >= child.getStartOffset()
					&& offset <= child.getEndOffset()) {

				Caret caret = child.getCaret(context, offset);
				caret.translate(child.getX(), child.getY());
				return caret;
			}

			x += widths[i] + hSpacing;
		}

		return new TextCaret(x, 0, this.getHeight());
	}

	/**
	 * Override to return zero insets. Table rows have no insets in
	 * border-collapse:separate mode.
	 */
	public Insets getInsets(LayoutContext context, int containerWidth) {
		return Insets.ZERO_INSETS;
	}

	public int getMarginBottom() {
		return 0;
	}

	public int getMarginTop() {
		return 0;
	}

	public int getNextLineOffset(LayoutContext context, int offset, int x) {

		BlockBox[] children = this.getContentChildren();
		int[] widths = this.getTableBox().getColumnWidths();
		int leftEdge = 0;

		for (int i = 0; i < children.length; i++) {
			if (leftEdge + widths[i] > x) {
				int newOffset = children[i].getNextLineOffset(context, offset,
						x - leftEdge);
				if (newOffset == children[i].getEndOffset() + 1) {
					return -1;
				} else {
					return newOffset;
				}
			}
			leftEdge += widths[i];
		}

		return -1;
	}

	public int getPreviousLineOffset(LayoutContext context, int offset, int x) {

		BlockBox[] children = this.getContentChildren();
		int[] widths = this.getTableBox().getColumnWidths();
		int leftEdge = 0;

		for (int i = 0; i < children.length; i++) {
			if (leftEdge + widths[i] > x) {
				int newOffset = children[i].getPreviousLineOffset(context,
						offset, x - leftEdge);
				if (newOffset == children[i].getStartOffset() - 1) {
					return -1;
				} else {
					return newOffset;
				}
			}
			leftEdge += widths[i];
		}

		return -1;
	}

	/**
	 * Returns the TableBox associated with this row.
	 */
	public TableBox getTableBox() {
		return (TableBox) this.getParent().getParent().getParent();
	}

	protected int positionChildren(LayoutContext context) {

		int hSpacing = this.getTableBox().getHorizonalSpacing();

		int childX = hSpacing;
		int topInset = 0;
		int height = 0;
		int bottomInset = 0;
		for (int i = 0; i < this.getChildren().length; i++) {
			Box child = this.getChildren()[i];
			Insets insets = child.getInsets(context, this.getWidth());

			childX += insets.getLeft();

			child.setX(childX);

			childX += child.getWidth() + insets.getRight() + hSpacing;

			topInset = Math.max(topInset, insets.getTop());
			height = Math.max(height, child.getHeight());
			bottomInset = Math.max(bottomInset, insets.getBottom());
		}

		this.setHeight(topInset + height + bottomInset);

		for (int i = 0; i < this.getChildren().length; i++) {
			Box child = this.getChildren()[i];
			child.setY(topInset);
			child.setHeight(height);
		}

		return -1; // TODO revisit
	}

	public int viewToModel(LayoutContext context, int x, int y) {

		Box[] children = this.getChildren();

		if (children == null) {
			int charCount = this.getEndOffset() - this.getStartOffset() - 1;
			if (charCount == 0 || this.getHeight() == 0) {
				return this.getEndOffset();
			} else {
				return this.getStartOffset() + charCount * y / this.getHeight();
			}
		} else {
			for (int i = 0; i < children.length; i++) {
				Box child = children[i];
				if (!child.hasContent()) {
					continue;
				}
				if (x < child.getX()) {
					return child.getStartOffset() - 1;
				} else if (x < child.getX() + child.getWidth()) {
					return child.viewToModel(context, x - child.getX(), y
							- child.getY());
				}
			}
		}

		return this.getEndOffset();
	}

}