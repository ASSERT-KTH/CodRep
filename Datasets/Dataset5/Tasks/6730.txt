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
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Moves the current table column to the left.
 */
public class MoveColumnLeftAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		final ActionUtils.RowColumnInfo rcInfo = ActionUtils
				.getRowColumnInfo(vexWidget);

		if (rcInfo == null || rcInfo.cellIndex < 1) {
			return;
		}

		vexWidget.doWork(true, new Runnable() {
			public void run() {

				// Cells to the left of the current column
				final List sourceCells = new ArrayList();

				// Cells in the current column
				final List destCells = new ArrayList();

				ActionUtils.iterateTableCells(vexWidget,
						new TableCellCallback() {
							Object prevCell = null;

							public void startRow(Object row, int rowIndex) {
							}

							public void onCell(Object row, Object cell,
									int rowIndex, int cellIndex) {
								if (cellIndex == rcInfo.cellIndex) {
									sourceCells.add(this.prevCell);
									destCells.add(cell);
								} else if (cellIndex == rcInfo.cellIndex - 1) {
									this.prevCell = cell;
								}
							}

							public void endRow(Object row, int rowIndex) {
							}
						});

				// Iterate the deletions in reverse, so that we don't mess up
				// offsets that are in anonymous cells, which are not stored
				// as Positions.
				//
				// Also, to preserve the current caret position, we don't cut
				// and paste the current column. Instead, we cut the column
				// to the left of the current column and paste it on the right.
				for (int i = sourceCells.size() - 1; i >= 0; i--) {

					Object source = sourceCells.get(i);
					final IntRange sourceRange = ActionUtils
							.getOuterRange(source);

					Object dest = destCells.get(i);
					vexWidget.moveTo(ActionUtils.getOuterRange(dest).getEnd());

					vexWidget.savePosition(new Runnable() {
						public void run() {
							vexWidget.moveTo(sourceRange.getStart());
							vexWidget.moveTo(sourceRange.getEnd(), true);
							vexWidget.cutSelection();
						}
					});

					vexWidget.paste();
				}
			}
		});
	}

	public boolean isEnabled(IVexWidget vexWidget) {
		ActionUtils.RowColumnInfo rcInfo = ActionUtils
				.getRowColumnInfo(vexWidget);
		return rcInfo != null && rcInfo.cellIndex > 0;
	}
}