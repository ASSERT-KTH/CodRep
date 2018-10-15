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

import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Inserts one or more table rows either above or below the currently selected
 * one(s). This class is meant as a base class for InsertRowAboveAction and
 * InsertRowBelowAction.
 */
public class InsertRowAction extends AbstractVexAction {

	/**
	 * Class constructor.
	 * 
	 * @param above
	 *            If true, the new rows are inserted above the currently
	 *            selected ones, else they are inserted below.
	 */
	public InsertRowAction(boolean above) {
		this.above = above;
	}

	public void run(final IVexWidget vexWidget) {

		vexWidget.doWork(new Runnable() {
			public void run() {

				final List rowsToInsert = new ArrayList();
				final List rowCellsToInsert = new ArrayList();

				ActionUtils.iterateTableCells(vexWidget,
						new TableCellCallback() {

							boolean rowSelected;
							List cellsToInsert;

							public void startRow(Object row, int rowIndex) {
								rowSelected = ActionUtils
										.elementOrRangeIsPartiallySelected(
												vexWidget, row);

								if (rowSelected) {
									cellsToInsert = new ArrayList();
								}
							}

							public void onCell(Object row, Object cell,
									int rowIndex, int cellIndex) {
								if (rowSelected) {
									cellsToInsert.add(cell);
								}
							}

							public void endRow(Object row, int rowIndex) {
								if (rowSelected) {
									rowsToInsert.add(row);
									rowCellsToInsert.add(cellsToInsert);
								}
							}

						});

				if (rowsToInsert.size() == 0) {
					return;
				}

				//
				// save the caret offset so that we return just inside the first
				// table cell
				//
				// (innerOffset - outerOffset) represents the final offset of
				// the caret, relative to the insertion point of the new rows
				//
				int outerOffset = ActionUtils
						.getOuterRange(rowsToInsert.get(0)).getStart();
				int innerOffset;
				List firstCells = (List) rowCellsToInsert.get(0);
				if (firstCells.size() == 0) {
					innerOffset = ActionUtils
							.getInnerRange(rowsToInsert.get(0)).getStart();
				} else {
					innerOffset = ActionUtils.getInnerRange(firstCells.get(0))
							.getStart();
				}

				int insertOffset;
				if (above) {
					insertOffset = ActionUtils.getOuterRange(
							rowsToInsert.get(0)).getStart();
				} else {
					Object lastRow = rowsToInsert.get(rowsToInsert.size() - 1);
					insertOffset = ActionUtils.getOuterRange(lastRow).getEnd();
				}

				int finalOffset = insertOffset + (innerOffset - outerOffset);

				vexWidget.moveTo(insertOffset);

				for (int i = 0; i < rowsToInsert.size(); i++) {

					Object row = rowsToInsert.get(i);

					if (row instanceof Element) {
						vexWidget.insertElement((Element) ((Element) row)
								.clone());
					}

					List cellsToInsert = (List) rowCellsToInsert.get(i);

					for (int j = 0; j < cellsToInsert.size(); j++) {
						Object cell = cellsToInsert.get(j);
						if (cell instanceof Element) {
							vexWidget.insertElement((Element) ((Element) cell)
									.clone());
							vexWidget.moveBy(+1);
						} else {
							vexWidget.insertText(" ");
						}
					}

					if (row instanceof Element) {
						vexWidget.moveBy(+1);
					}

				}

				vexWidget.moveTo(finalOffset);
			}
		});

	}

	public boolean isEnabled(IVexWidget vexWidget) {
		// TODO only enable (a) if rows are selected, and (b) if not inserting
		// adjacent anonymous rows
		return true;
	}

	private boolean above;
}