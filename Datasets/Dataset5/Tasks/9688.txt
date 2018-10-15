import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;

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
package org.eclipse.wst.xml.vex.ui.internal.action;

import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Duplicates current selection or element.
 */
public class DuplicateSelectionAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		vexWidget.doWork(new Runnable() {
			public void run() {
				if (!vexWidget.hasSelection()) {
					VEXElement element = vexWidget.getCurrentElement();
					if (element.getParent() == null) {
						// Can't dup the root element
						return;
					}
					vexWidget.moveTo(element.getStartOffset());
					vexWidget.moveTo(element.getEndOffset() + 1, true);
				}

				vexWidget.copySelection();
				int startOffset = vexWidget.getSelectionEnd();
				vexWidget.moveTo(startOffset);
				vexWidget.paste();
				int endOffset = vexWidget.getCaretOffset();
				vexWidget.moveTo(startOffset);
				vexWidget.moveTo(endOffset, true);
			}
		});
	}

}