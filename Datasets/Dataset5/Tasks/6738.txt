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

import org.eclipse.wst.xml.vex.core.internal.dom.DocumentFragment;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Removes the current element, adding its content to the parent element.
 */
public class RemoveElementAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {
		vexWidget.doWork(new Runnable() {
			public void run() {
				Element element = vexWidget.getDocument().getElementAt(
						vexWidget.getCaretOffset());
				vexWidget.moveTo(element.getStartOffset() + 1, false);
				vexWidget.moveTo(element.getEndOffset(), true);
				DocumentFragment frag = vexWidget.getSelectedFragment();
				vexWidget.deleteSelection();
				vexWidget.moveBy(-1, false);
				vexWidget.moveBy(2, true);
				vexWidget.deleteSelection();
				vexWidget.insertFragment(frag);
			}
		});
	}

}