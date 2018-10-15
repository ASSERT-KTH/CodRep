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

import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.TableRowBox;
import org.eclipse.wst.xml.vex.core.internal.widget.IBoxFilter;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Moves the caret to the next table cell. The contents of the cell are
 * selected. If the current cell is the last cell in the table, the current row
 * is duplicated.
 */
public class NextTableCellAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		final TableRowBox tr = (TableRowBox) vexWidget
				.findInnermostBox(new IBoxFilter() {
					public boolean matches(Box box) {
						return box instanceof TableRowBox;
					}
				});

		if (tr == null) {
			// not in a table row
			return;
		}

		int offset = vexWidget.getCaretOffset();

		Box[] cells = tr.getChildren();
		for (int i = 0; i < cells.length; i++) {
			if (cells[i].getStartOffset() > offset) {
				vexWidget.moveTo(cells[i].getStartOffset());
				vexWidget.moveTo(cells[i].getEndOffset(), true);
				return;
			}
		}

		// No next cell found in this row
		// Find the next row
		Box[] rows = tr.getParent().getChildren();
		for (int i = 0; i < rows.length; i++) {
			if (rows[i].getStartOffset() > offset) {
				cells = rows[i].getChildren();
				if (cells.length > 0) {
					Box cell = cells[0];
					vexWidget.moveTo(cell.getStartOffset());
					vexWidget.moveTo(cell.getEndOffset(), true);
				} else {
					System.out.println("TODO - dup row into new empty row");
				}
				return;
			}
		}

		// We didn't find a "next row", so let's dup the current one
		ActionUtils.duplicateTableRow(vexWidget, tr);

	}
}