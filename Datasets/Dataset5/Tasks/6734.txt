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

import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.layout.BlockBox;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.widget.IBoxFilter;
import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Moves the current selection or block element above the previous sibling. WORK
 * IN PROGRESS.
 */
public class MoveSelectionUpAction extends AbstractVexAction {

	public void run(final IVexWidget vexWidget) {

		// First we determine whether we should expand the selection
		// to contain an entire block box.

		// Find the lowest block box that completely contains the
		// selection
		Box box = vexWidget.findInnermostBox(new IBoxFilter() {
			public boolean matches(Box box) {
				return box instanceof BlockBox
						&& box.getElement() != null
						&& box.getStartOffset() <= vexWidget
								.getSelectionStart()
						&& box.getEndOffset() >= vexWidget.getSelectionEnd();
			}
		});

		Box[] children = box.getChildren();
		if (children.length > 0 && children[0] instanceof BlockBox) {
			// The found box contains other block children, so we
			// do NOT have to expand the selection
		} else {
			// Expand selection to the containing box

			// (Note: This "if" is caused by the fact that getStartOffset is
			// treated
			// differently between elements and boxes. Boxes own their
			// startOffset,
			// while elements don't own theirs. Perhaps we should fix this by
			// having
			// box.getStartOffset() return box.getStartPosition() + 1, but this
			// would
			// be a VERY large change.)
			System.out.println("Box is " + box);
			Element element = box.getElement();
			if (element != null) {
				vexWidget.moveTo(element.getEndOffset());
				vexWidget.moveTo(element.getStartOffset(), true);

			} else {
				vexWidget.moveTo(box.getEndOffset());
				vexWidget.moveTo(box.getStartOffset(), true);
			}
		}

		// final int previousSiblingStart =
		// ActionUtils.getPreviousSiblingStart(vexWidget);
		//        
		// vexWidget.doWork(new IRunnable() {
		// public void run() throws Exception {
		// vexWidget.cutSelection();
		// vexWidget.moveTo(previousSiblingStart);
		// vexWidget.paste();
		// vexWidget.moveTo(previousSiblingStart, true);
		// }
		// });

	}

}