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

import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.TableRowBox;
import org.eclipse.wst.xml.vex.core.internal.widget.IBoxFilter;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Splits the nearest enclosing table row or list item. If a table row is being
 * split, empty versions of the current row's cells are created.
 */
public class SplitItemAction extends AbstractVexAction {

	public void run(IVexWidget vexWidget) {

		final StyleSheet ss = vexWidget.getStyleSheet();

		// Item is either a TableRowBox or a BlockElementBox representing
		// a list item
		Box item = vexWidget.findInnermostBox(new IBoxFilter() {
			public boolean matches(Box box) {
				if (box instanceof TableRowBox) {
					return true;
				} else {
					Element element = box.getElement();
					return element != null
							&& ss.getStyles(element).getDisplay().equals(
									CSS.LIST_ITEM);
				}
			}
		});

		if (item instanceof TableRowBox) {
			insertRowBelowAction.run(vexWidget);
			// ActionUtils.duplicateTableRow(vexWidget, (TableRowBox) item);
		} else if (item != null) {
			SplitAction.splitElement(vexWidget, item.getElement());
		}
	}

	private static InsertRowBelowAction insertRowBelowAction = new InsertRowBelowAction();

}