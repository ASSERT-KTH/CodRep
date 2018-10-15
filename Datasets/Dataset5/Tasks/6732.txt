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

import org.eclipse.wst.xml.vex.core.internal.core.IntRange;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Moves the current table row down below its next sibling.
 */
public class MoveRowDownAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		final ActionUtils.SelectedRows selected = ActionUtils
				.getSelectedTableRows(vexWidget);

		if (selected.getRows() == null || selected.getRowAfter() == null) {
			return;
		}

		vexWidget.doWork(true, new Runnable() {
			public void run() {
				IntRange range = ActionUtils.getOuterRange(selected
						.getRowAfter());
				vexWidget.moveTo(range.getStart());
				vexWidget.moveTo(range.getEnd(), true);
				vexWidget.cutSelection();

				Object firstRow = selected.getRows().get(0);
				vexWidget
						.moveTo(ActionUtils.getOuterRange(firstRow).getStart());
				vexWidget.paste();
			}
		});
	}

	public boolean isEnabled(IVexWidget vexWidget) {
		ActionUtils.SelectedRows selected = ActionUtils
				.getSelectedTableRows(vexWidget);
		return selected.getRows() != null && selected.getRowAfter() != null;
	}
}