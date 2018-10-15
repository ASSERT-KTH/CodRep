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

import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Delete selected table rows.
 */
public class DeleteRowAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		final List rows = ActionUtils.getSelectedTableRows(vexWidget).getRows();

		if (rows == null) {
			return;
		}

		vexWidget.doWork(new Runnable() {
			public void run() {
				int startOffset = ActionUtils.getOuterRange(rows.get(0))
						.getStart();
				int endOffset = ActionUtils.getOuterRange(
						rows.get(rows.size() - 1)).getEnd();

				vexWidget.moveTo(startOffset);
				vexWidget.moveTo(endOffset, true);
				vexWidget.deleteSelection();
			}
		});

	}

	public boolean isEnabled(IVexWidget vexWidget) {
		return ActionUtils.getSelectedTableRows(vexWidget).getRows() != null;
	}

}