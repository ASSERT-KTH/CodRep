package org.eclipse.wst.xml.vex.ui.internal.action;

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
package org.eclipse.wst.xml.vex.core.internal.action;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.Node;
import org.eclipse.wst.xml.vex.core.internal.layout.BlockBox;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.ElementOrRangeCallback;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutUtils;
import org.eclipse.wst.xml.vex.core.internal.layout.TableRowBox;
import org.eclipse.wst.xml.vex.core.internal.widget.IBoxFilter;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Static helper methods used across actions.
 */
public class ActionUtils {

	public static class RowColumnInfo {
		public Object row;
		public Object cell;
		public int rowIndex;
		public int cellIndex;
		public int rowCount;
		public int columnCount;
		public int maxColumnCount;
	}

	/**
	 * Clone the table cells from the given TableRowBox to the current offset in
	 * vexWidget.
	 * 
	 * @param vexWidget
	 *            IVexWidget to modify.
	 * @param tr
	 *            TableRowBox whose cells are to be cloned.
	 * @param moveToFirstCell
	 *            TODO
	 */
	public static void cloneTableCells(final IVexWidget vexWidget,
			final TableRowBox tr, final boolean moveToFirstCell) {
		vexWidget.doWork(new Runnable() {
			public void run() {

				int offset = vexWidget.getCaretOffset();

				boolean firstCellIsAnonymous = false;
				Box[] cells = tr.getChildren();
				for (int i = 0; i < cells.length; i++) {
					if (cells[i].isAnonymous()) {
						vexWidget.insertText(" ");
						if (i == 0) {
							firstCellIsAnonymous = true;
						}
					} else {
						vexWidget.insertElement((Element) cells[i].getElement()
								.clone());
						vexWidget.moveBy(+1);
					}
				}

				if (moveToFirstCell) {
					vexWidget.moveTo(offset + 1);
					if (firstCellIsAnonymous) {
						vexWidget.moveBy(-1, true);
					}
				}
			}
		});
	}

	/**
	 * Duplicate the given table row, inserting a new empty one below it. The
	 * new row contains empty children corresponding to the given row's
	 * children.
	 * 
	 * @param vexWidget
	 *            IVexWidget with which we're working
	 * @param tr
	 *            TableRowBox to be duplicated.
	 */
	public static void duplicateTableRow(final IVexWidget vexWidget,
			final TableRowBox tr) {
		vexWidget.doWork(new Runnable() {
			public void run() {

				vexWidget.moveTo(tr.getEndOffset());

				if (!tr.isAnonymous()) {
					vexWidget.moveBy(+1); // Move past sentinel in current row
					vexWidget.insertElement((Element) tr.getElement().clone());
				}

				cloneTableCells(vexWidget, tr, true);
			}
		});
	}

	/**
	 * Returns true if the given element or range is at least partially
	 * selected.
	 * 
	 * @param vexWidget
	 *            IVexWidget being tested.
	 * @param elementOrRange
	 *            Element or IntRange being tested.
	 */
	public static boolean elementOrRangeIsPartiallySelected(
			IVexWidget vexWidget, Object elementOrRange) {
		IntRange range = getInnerRange(elementOrRange);
		return range.getEnd() >= vexWidget.getSelectionStart()
				&& range.getStart() <= vexWidget.getSelectionEnd();
	}

	/**
	 * Returns the zero-based index of the table column containing the current
	 * offset. Returns -1 if we are not inside a table.
	 */
	public static int getCurrentColumnIndex(IVexWidget vexWidget) {

		Element row = getCurrentTableRow(vexWidget);

		if (row == null) {
			return -1;
		}

		final int offset = vexWidget.getCaretOffset();
		final int[] column = new int[] { -1 };
		LayoutUtils.iterateTableCells(vexWidget.getStyleSheet(), row,
				new ElementOrRangeCallback() {
					private int i = 0;

					public void onElement(Element child, String displayStyle) {
						if (offset > child.getStartOffset()
								&& offset <= child.getEndOffset()) {
							column[0] = i;
						}
						i++;
					}

					public void onRange(Element parent, int startOffset,
							int endOffset) {
						i++;
					}
				});

		return column[0];
	}

	/**
	 * Returns the innermost Element with style table-row containing the caret,
	 * or null if no such element exists.
	 * 
	 * @param vexWidget
	 *            IVexWidget to use.
	 */
	public static Element getCurrentTableRow(IVexWidget vexWidget) {

		StyleSheet ss = vexWidget.getStyleSheet();
		Element element = vexWidget.getCurrentElement();

		while (element != null) {
			if (ss.getStyles(element).getDisplay().equals(CSS.TABLE_ROW)) {
				return element;
			}
			element = element.getParent();
		}

		return null;
	}

	/**
	 * Returns the start offset of the next sibling of the parent element.
	 * Returns -1 if there is no previous sibling in the parent.
	 * 
	 * @param vexWidget
	 *            VexWidget to use.
	 */
	public static int getPreviousSiblingStart(IVexWidget vexWidget) {
		int startOffset;

		if (vexWidget.hasSelection()) {
			startOffset = vexWidget.getSelectionStart();
		} else {
			Box box = vexWidget.findInnermostBox(new IBoxFilter() {
				public boolean matches(Box box) {
					return box instanceof BlockBox && box.getElement() != null;
				}
			});

			if (box.getElement() == vexWidget.getDocument().getRootElement()) {
				return -1;
			}

			startOffset = box.getElement().getStartOffset();
		}

		int previousSiblingStart = -1;
		Element parent = vexWidget.getDocument().getElementAt(startOffset);
		Node[] children = parent.getChildNodes();
		for (int i = 0; i < children.length; i++) {
			Node child = children[i];
			if (startOffset == child.getStartOffset()) {
				break;
			}
			previousSiblingStart = child.getStartOffset();
		}
		return previousSiblingStart;
	}

	/**
	 * Returns an array of the selected block boxes. Text nodes between boxes
	 * are not returned. If the selection does not enclose any block boxes,
	 * returns an empty array.
	 * 
	 * @param vexWidget
	 *            VexWidget to use.
	 */
	public static BlockBox[] getSelectedBlockBoxes(final IVexWidget vexWidget) {

		if (!vexWidget.hasSelection()) {
			return new BlockBox[0];
		}

		Box parent = vexWidget.findInnermostBox(new IBoxFilter() {
			public boolean matches(Box box) {
				System.out.println("Matching " + box);
				return box instanceof BlockBox
						&& box.getStartOffset() <= vexWidget
								.getSelectionStart()
						&& box.getEndOffset() >= vexWidget.getSelectionEnd();
			}
		});

		System.out.println("Matched " + parent);

		List blockList = new ArrayList();

		Box[] children = parent.getChildren();
		System.out.println("Parent has " + children.length + " children");
		for (int i = 0; i < children.length; i++) {
			Box child = children[i];
			if (child instanceof BlockBox
					&& child.getStartOffset() >= vexWidget.getSelectionStart()
					&& child.getEndOffset() <= vexWidget.getSelectionEnd()) {
				System.out.println("  adding " + child);
				blockList.add(child);
			} else {
				System.out.println("  skipping " + child);
			}

		}

		return (BlockBox[]) blockList.toArray(new BlockBox[blockList.size()]);
	}

	/**
	 * Returns the currently selected table rows, or the current row if ther is
	 * no selection. If no row can be found, returns an empty array.
	 * 
	 * @param vexWidget
	 *            IVexWidget to use.
	 */
	public static SelectedRows getSelectedTableRows(final IVexWidget vexWidget) {

		final SelectedRows selected = new SelectedRows();

		ActionUtils.iterateTableCells(vexWidget, new TableCellCallback() {
			public void startRow(Object row, int rowIndex) {
				if (ActionUtils.elementOrRangeIsPartiallySelected(vexWidget,
						row)) {
					if (selected.rows == null) {
						selected.rows = new ArrayList();
					}
					selected.rows.add(row);
				} else {
					if (selected.rows == null) {
						selected.rowBefore = row;
					} else {
						if (selected.rowAfter == null) {
							selected.rowAfter = row;
						}
					}
				}
			}

			public void onCell(Object row, Object cell, int rowIndex,
					int cellIndex) {
			}

			public void endRow(Object row, int rowIndex) {
			}
		});

		return selected;
	}

	public static void iterateTableCells(IVexWidget vexWidget,
			final TableCellCallback callback) {

		final StyleSheet ss = vexWidget.getStyleSheet();

		iterateTableRows(vexWidget, new ElementOrRangeCallback() {

			final private int[] rowIndex = { 0 };

			public void onElement(final Element row, String displayStyle) {

				callback.startRow(row, rowIndex[0]);

				LayoutUtils.iterateTableCells(ss, row,
						new ElementOrRangeCallback() {
							private int cellIndex = 0;

							public void onElement(Element cell,
									String displayStyle) {
								callback.onCell(row, cell, rowIndex[0],
										cellIndex);
								cellIndex++;
							}

							public void onRange(Element parent,
									int startOffset, int endOffset) {
								callback.onCell(row, new IntRange(startOffset,
										endOffset), rowIndex[0], cellIndex);
								cellIndex++;
							}
						});

				callback.endRow(row, rowIndex[0]);

				rowIndex[0]++;
			}

			public void onRange(Element parent, final int startOffset,
					final int endOffset) {

				final IntRange row = new IntRange(startOffset, endOffset);
				callback.startRow(row, rowIndex[0]);

				LayoutUtils.iterateTableCells(ss, parent, startOffset,
						endOffset, new ElementOrRangeCallback() {
							private int cellIndex = 0;

							public void onElement(Element cell,
									String displayStyle) {
								callback.onCell(row, cell, rowIndex[0],
										cellIndex);
								cellIndex++;
							}

							public void onRange(Element parent,
									int startOffset, int endOffset) {
								callback.onCell(row, new IntRange(startOffset,
										endOffset), rowIndex[0], cellIndex);
								cellIndex++;
							}
						});

				callback.endRow(row, rowIndex[0]);

				rowIndex[0]++;
			}
		});
	}

	/**
	 * Returns a RowColumnInfo structure containing information about the table
	 * containing the caret. Returns null if the caret is not currently inside a
	 * table.
	 * 
	 * @param vexWidget
	 *            IVexWidget to inspect.
	 */
	public static RowColumnInfo getRowColumnInfo(IVexWidget vexWidget) {

		final boolean[] found = new boolean[1];
		final RowColumnInfo[] rcInfo = new RowColumnInfo[] { new RowColumnInfo() };
		final int offset = vexWidget.getCaretOffset();

		rcInfo[0].cellIndex = -1;
		rcInfo[0].rowIndex = -1;

		iterateTableCells(vexWidget, new TableCellCallback() {

			int rowColumnCount;

			public void startRow(Object row, int rowIndex) {
				rowColumnCount = 0;
			}

			public void onCell(Object row, Object cell, int rowIndex,
					int cellIndex) {
				found[0] = true;
				if (LayoutUtils.elementOrRangeContains(row, offset)) {
					rcInfo[0].row = row;
					rcInfo[0].rowIndex = rowIndex;
					rcInfo[0].columnCount++;

					if (LayoutUtils.elementOrRangeContains(cell, offset)) {
						rcInfo[0].cell = cell;
						rcInfo[0].cellIndex = cellIndex;
					}
				}

				rowColumnCount++;
			}

			public void endRow(Object row, int rowIndex) {
				rcInfo[0].rowCount++;
				rcInfo[0].maxColumnCount = Math.max(rcInfo[0].maxColumnCount,
						rowColumnCount);
			}
		});

		if (found[0]) {
			return rcInfo[0];
		} else {
			return null;
		}
	}

	/**
	 * Iterate over all rows in the table containing the caret.
	 * 
	 * @param vexWidget
	 *            IVexWidget to iterate over.
	 * @param callback
	 *            Caller-provided callback that this method calls for each row
	 *            in the current table.
	 */
	public static void iterateTableRows(IVexWidget vexWidget,
			ElementOrRangeCallback callback) {

		final StyleSheet ss = vexWidget.getStyleSheet();
		final Document doc = vexWidget.getDocument();
		final int offset = vexWidget.getCaretOffset();

		// This may or may not be a table
		// In any case, it's the element that contains the top-level table
		// children
		Element table = doc.getElementAt(offset);

		while (table != null && !LayoutUtils.isTableChild(ss, table)) {
			table = table.getParent();
		}

		while (table != null && LayoutUtils.isTableChild(ss, table)) {
			table = table.getParent();
		}

		if (table == null || table.getParent() == null) {
			return;
		}

		final List tableChildren = new ArrayList();
		final boolean[] found = new boolean[] { false };
		LayoutUtils.iterateChildrenByDisplayStyle(ss,
				LayoutUtils.TABLE_CHILD_STYLES, table,
				new ElementOrRangeCallback() {
					public void onElement(Element child, String displayStyle) {
						if (offset >= child.getStartOffset()
								&& offset <= child.getEndOffset()) {
							found[0] = true;
						}
						tableChildren.add(child);
					}

					public void onRange(Element parent, int startOffset,
							int endOffset) {
						if (!found[0]) {
							tableChildren.clear();
						}
					}
				});

		if (!found[0]) {
			return;
		}

		int startOffset = ((Element) tableChildren.get(0)).getStartOffset();
		int endOffset = ((Element) tableChildren.get(tableChildren.size() - 1))
				.getEndOffset() + 1;
		LayoutUtils.iterateTableRows(ss, table, startOffset, endOffset,
				callback);
	}

	/**
	 * Returns an IntRange representing the offsets inside the given Element or
	 * IntRange. If an Element is passed, returns the offsets inside the
	 * sentinels. If an IntRange is passed it is returned directly.
	 * 
	 * @param elementOrRange
	 *            Element or IntRange to be inspected.
	 */
	public static IntRange getInnerRange(Object elementOrRange) {
		if (elementOrRange instanceof Element) {
			Element element = (Element) elementOrRange;
			return new IntRange(element.getStartOffset() + 1, element
					.getEndOffset());
		} else {
			return (IntRange) elementOrRange;
		}
	}

	/**
	 * Returns an IntRange representing the offsets outside the given Element or
	 * IntRange. If an Element is passed, returns the offsets outside the
	 * sentinels. If an IntRange is passed it is returned directly.
	 * 
	 * @param elementOrRange
	 *            Element or IntRange to be inspected.
	 */
	public static IntRange getOuterRange(Object elementOrRange) {
		if (elementOrRange instanceof Element) {
			Element element = (Element) elementOrRange;
			return new IntRange(element.getStartOffset(), element
					.getEndOffset() + 1);
		} else {
			return (IntRange) elementOrRange;
		}
	}

	public static class SelectedRows {

		private SelectedRows() {
		}

		public List getRows() {
			return this.rows;
		}

		public Object getRowBefore() {
			return this.rowBefore;
		}

		public Object getRowAfter() {
			return this.rowAfter;
		}

		private List rows;
		private Object rowBefore;
		private Object rowAfter;
	}
}