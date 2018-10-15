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
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.wst.xml.vex.core.internal.core.Insets;
import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * Box that lays out a table.
 */
public class TableBox extends AbstractBlockBox {

	/**
	 * Class constructor.
	 * 
	 * @param element
	 *            Element represented by this box.
	 */
	public TableBox(LayoutContext context, BlockBox parent, Element element) {
		super(context, parent, element);
	}

	public TableBox(LayoutContext context, BlockBox parent, int startOffset,
			int endOffset) {
		super(context, parent, startOffset, endOffset);
	}

	protected List createChildren(final LayoutContext context) {

		// Walk children:
		// each table-caption gets a BEB
		// each table-column gets a TableColumnBox
		// each table-column-group gets a TableColumnGroupBox
		// runs of others get TableBodyBox

		final List children = new ArrayList();

		this.iterateChildrenByDisplayStyle(context.getStyleSheet(),
				captionOrColumnStyles, new ElementOrRangeCallback() {
					public void onElement(Element child, String displayStyle) {
						children.add(new BlockElementBox(context,
								TableBox.this, child));
					}

					public void onRange(IVEXElement parent, int startOffset,
							int endOffset) {
						children.add(new TableBodyBox(context, TableBox.this,
								startOffset, endOffset));
					}
				});

		return children;
	}

	/**
	 * Returns an array of widths of the table columns. These widths do not
	 * include column spacing.
	 */
	public int[] getColumnWidths() {
		return this.columnWidths;
	}

	public int getHorizonalSpacing() {
		return this.horizonalSpacing;
	}

	public Insets getInsets(LayoutContext context, int containerWidth) {
		return new Insets(this.getMarginTop(), 0, this.getMarginBottom(), 0);
	}

	public int getVerticalSpacing() {
		return this.verticalSpacing;
	}

	public IntRange layout(LayoutContext context, int top, int bottom) {

		// TODO Only compute columns widths (a) if re-laying out the whole box
		// or (b) if the invalid child row now has more columns than us
		// or (c) if the invalid child row has < current column count and it
		// used to be the only one with a valid child row.

		int newColCount = this.computeColumnCount(context);
		if (this.columnWidths == null
				|| newColCount != this.columnWidths.length) {
			this.setLayoutState(LAYOUT_REDO);
		}

		if (this.getLayoutState() == LAYOUT_REDO) {
			this.computeColumnWidths(context, newColCount);
		}

		return super.layout(context, top, bottom);
	}

	public void paint(LayoutContext context, int x, int y) {

		if (this.skipPaint(context, x, y)) {
			return;
		}

		this.paintChildren(context, x, y);

		this.paintSelectionFrame(context, x, y, true);
	}

	// ============================================================ PRIVATE

	private static Set captionOrColumnStyles = new HashSet();

	static {
		captionOrColumnStyles.add(CSS.TABLE_CAPTION);
		captionOrColumnStyles.add(CSS.TABLE_COLUMN);
		captionOrColumnStyles.add(CSS.TABLE_COLUMN_GROUP);
	}

	private int[] columnWidths;
	private int horizonalSpacing;
	private int verticalSpacing;

	private static class CountingCallback implements ElementOrRangeCallback {

		public int getCount() {
			return this.count;
		}

		public void reset() {
			this.count = 0;
		}

		public void onElement(Element child, String displayStyle) {
			this.count++;
		}

		public void onRange(IVEXElement parent, int startOffset, int endOffset) {
			this.count++;
		}

		private int count;
	}

	/**
	 * Performs a quick count of this table's columns. If the count has changed,
	 * we must re-layout the entire table.
	 */
	private int computeColumnCount(LayoutContext context) {

		IVEXElement tableElement = this.findContainingElement();
		final int[] columnCounts = new int[1]; // work around Java's insistence
												// on final
		columnCounts[0] = 0;
		final StyleSheet styleSheet = context.getStyleSheet();
		final CountingCallback callback = new CountingCallback();
		LayoutUtils.iterateTableRows(styleSheet, tableElement, this
				.getStartOffset(), this.getEndOffset(),
				new ElementOrRangeCallback() {
					public void onElement(Element child, String displayStyle) {
						LayoutUtils.iterateTableCells(styleSheet, child,
								callback);
						columnCounts[0] = Math.max(columnCounts[0], callback
								.getCount());
						callback.reset();
					}

					public void onRange(IVEXElement parent, int startOffset,
							int endOffset) {
						LayoutUtils.iterateTableCells(styleSheet, parent,
								startOffset, endOffset, callback);
						columnCounts[0] = Math.max(columnCounts[0], callback
								.getCount());
						callback.reset();
					}

				});

		return columnCounts[0];
	}

	private void computeColumnWidths(final LayoutContext context,
			int columnCount) {

		this.columnWidths = new int[columnCount];

		if (columnCount == 0) {
			return;
		}

		this.horizonalSpacing = 0;
		this.verticalSpacing = 0;
		int myWidth = this.getWidth();
		int availableWidth = myWidth;

		if (!this.isAnonymous()) {
			Styles styles = context.getStyleSheet()
					.getStyles(this.getElement());
			this.horizonalSpacing = styles.getBorderSpacing().getHorizontal();
			this.verticalSpacing = styles.getBorderSpacing().getVertical();

			// width available for columns
			// Since we apply margins/borders/padding to the TableBodyBox,
			// they're
			// not reflected in the width of this box. Thus, we subtract them
			// here
			availableWidth -= +styles.getMarginLeft().get(myWidth)
					+ styles.getBorderLeftWidth()
					+ styles.getPaddingLeft().get(myWidth)
					+ styles.getPaddingRight().get(myWidth)
					+ styles.getBorderRightWidth()
					+ styles.getMarginRight().get(myWidth);
		}

		int totalColumnWidth = this.horizonalSpacing;
		int columnWidth = (availableWidth - this.horizonalSpacing
				* (columnCount + 1))
				/ columnCount;
		for (int i = 0; i < this.columnWidths.length - 1; i++) {
			System.err.print(" " + columnWidth);
			this.columnWidths[i] = columnWidth;
			totalColumnWidth += columnWidth + this.horizonalSpacing;
		}

		// Due to rounding errors in the expression above, we calculate the
		// width of the last column separately, to make it exact.
		this.columnWidths[this.columnWidths.length - 1] = availableWidth
				- totalColumnWidth - this.horizonalSpacing;

	}
}