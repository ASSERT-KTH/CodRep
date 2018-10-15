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

import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Moves the current table row up above its previous sibling.
 */
public class MoveRowUpAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		final ActionUtils.SelectedRows selected = ActionUtils
				.getSelectedTableRows(vexWidget);

		if (selected.getRows() == null || selected.getRowBefore() == null) {
			return;
		}

		vexWidget.doWork(true, new Runnable() {
			public void run() {
				IntRange range = ActionUtils.getOuterRange(selected
						.getRowBefore());
				vexWidget.moveTo(range.getStart());
				vexWidget.moveTo(range.getEnd(), true);
				vexWidget.cutSelection();

				List rows = selected.getRows();
				Object lastRow = rows.get(rows.size() - 1);
				vexWidget.moveTo(ActionUtils.getOuterRange(lastRow).getEnd());
				vexWidget.paste();
			}
		});
	}

	public boolean isEnabled(IVexWidget vexWidget) {
		ActionUtils.SelectedRows selected = ActionUtils
				.getSelectedTableRows(vexWidget);
		return selected.getRows() != null && selected.getRowBefore() != null;
	}

}