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
 * Delete the table column containing the caret.
 */
public class DeleteColumnAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		vexWidget.doWork(new Runnable() {
			public void run() {

				final ActionUtils.RowColumnInfo rcInfo = ActionUtils
						.getRowColumnInfo(vexWidget);

				if (rcInfo == null) {
					return;
				}

				final List cellsToDelete = new ArrayList();
				ActionUtils.iterateTableCells(vexWidget,
						new TableCellCallback() {
							public void startRow(Object row, int rowIndex) {
							}

							public void onCell(Object row, Object cell,
									int rowIndex, int cellIndex) {
								if (cellIndex == rcInfo.cellIndex) {
									cellsToDelete.add(cell);
								}
							}

							public void endRow(Object row, int rowIndex) {
							}
						});

				// Iterate the deletions in reverse, so that we don't mess up
				// offsets that are in anonymous cells, which are not stored
				// as Positions.
				for (int i = cellsToDelete.size() - 1; i >= 0; i--) {
					Object cell = cellsToDelete.get(i);
					IntRange range = ActionUtils.getOuterRange(cell);
					vexWidget.moveTo(range.getStart());
					vexWidget.moveTo(range.getEnd(), true);
					vexWidget.deleteSelection();
				}
			}
		});

	}

	public boolean isEnabled(IVexWidget vexWidget) {
		return ActionUtils.getCurrentColumnIndex(vexWidget) != -1;
	}

}