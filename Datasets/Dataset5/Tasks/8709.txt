package org.eclipse.ecf.internal.example.collab.ui;

/****************************************************************************
* Copyright (c) 2004 Composent, Inc. and others.
* All rights reserved. This program and the accompanying materials
* are made available under the terms of the Eclipse Public License v1.0
* which accompanies this distribution, and is available at
* http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*    Composent, Inc. - initial API and implementation
*****************************************************************************/

package org.eclipse.ecf.example.collab.ui;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Layout;


class ChatLayout extends Layout {
    protected static final int TEXT_HEIGHT_FUDGE = 8;
    Point iExtent, tExtent;
    int inputSize = 15;
    int separatorSize = 5;
    int textHeight = -1;
    ChatLayout(int defaultInputSize, int sepSize) {
        this.inputSize = defaultInputSize;
        this.separatorSize = sepSize;
    }
    protected Point computeSize(Composite composite, int wHint, int hHint,
            boolean changed) {
        Control[] children = composite.getChildren();
        if (changed || iExtent == null || tExtent == null) {
            iExtent = children[0].computeSize(SWT.DEFAULT, SWT.DEFAULT,
                    false);
            tExtent = children[1].computeSize(SWT.DEFAULT, SWT.DEFAULT,
                    false);
        }
        int width = iExtent.x + 5 + tExtent.x;
        int height = Math.max(iExtent.y, tExtent.y);
        return new Point(width + 2, height + 200);
    }
    protected void layout(Composite composite, boolean changed) {
        Control[] children = composite.getChildren();
        Point windowSize = composite.getSize();
        children[0].setBounds(1, 1, windowSize.x, windowSize.y
                - (inputSize + separatorSize));
        children[1].setBounds(1, children[0].getSize().y + separatorSize,
                windowSize.x, inputSize);
        if (changed || iExtent == null || tExtent == null) {
            iExtent = children[0].computeSize(SWT.DEFAULT, SWT.DEFAULT,
                    false);
            tExtent = children[1].computeSize(SWT.DEFAULT, SWT.DEFAULT,
                    false);
        }
    }
    protected void setInputTextHeight(int height) {
        textHeight = height;
        inputSize = textHeight + TEXT_HEIGHT_FUDGE;
    }
}
 No newline at end of file