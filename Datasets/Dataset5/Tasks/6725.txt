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
import java.util.Iterator;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Inserts a single table column after the current one.
 */
public class InsertColumnAfterAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		final int indexToDup = ActionUtils.getCurrentColumnIndex(vexWidget);
		if (indexToDup == -1) {
			return;
		}

		vexWidget.doWork(new Runnable() {
			public void run() {

				final List cellsToDup = new ArrayList();
				ActionUtils.iterateTableCells(vexWidget,
						new TableCellCallback() {
							public void startRow(Object row, int rowIndex) {
							}

							public void onCell(Object row, Object cell,
									int rowIndex, int cellIndex) {
								if (cellIndex == indexToDup
										&& cell instanceof Element) {
									cellsToDup.add(cell);
								}
							}

							public void endRow(Object row, int rowIndex) {
							}
						});

				int finalOffset = -1;
				for (Iterator it = cellsToDup.iterator(); it.hasNext();) {
					Element element = (Element) it.next();
					if (finalOffset == -1) {
						finalOffset = element.getStartOffset() + 1;
					}
					vexWidget.moveTo(element.getEndOffset() + 1);
					vexWidget.insertElement((Element) element.clone());
				}

				if (finalOffset != -1) {
					vexWidget.moveTo(finalOffset);
				}
			}
		});
	}

	public boolean isEnabled(IVexWidget vexWidget) {
		return ActionUtils.getCurrentColumnIndex(vexWidget) != -1;
	}
}