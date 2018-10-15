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
public class PreviousTableCellAction extends AbstractVexAction {

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
		for (int i = cells.length - 1; i >= 0; i--) {
			if (cells[i].getEndOffset() < offset) {
				vexWidget.moveTo(cells[i].getStartOffset());
				vexWidget.moveTo(cells[i].getEndOffset(), true);
				return;
			}
		}

		// No next cell found in this row
		// Find the previous row
		Box[] rows = tr.getParent().getChildren();
		for (int i = rows.length - 1; i >= 0; i--) {
			if (rows[i].getEndOffset() < offset) {
				cells = rows[i].getChildren();
				if (cells.length > 0) {
					Box cell = cells[cells.length - 1];
					vexWidget.moveTo(cell.getStartOffset());
					vexWidget.moveTo(cell.getEndOffset(), true);
				}
				return;
			}
		}

	}
}