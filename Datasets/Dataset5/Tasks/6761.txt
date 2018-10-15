package org.eclipse.wst.xml.vex.ui.internal.swt;

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
package org.eclipse.wst.xml.vex.core.internal.swt;

import org.eclipse.swt.widgets.Display;
import org.eclipse.wst.xml.vex.core.internal.core.DisplayDevice;

/**
 * Adapts the DisplayDevice display to the current SWT display.
 */
public class SwtDisplayDevice extends DisplayDevice {

	/**
	 * Class constructor.
	 */
	public SwtDisplayDevice() {
		// We used to do it like this, but it turns out sometimes we did it
		// too early and getCurrent() returned null, so now the convoluted stuff
		// below.
		// Display display = Display.getCurrent();
		// this.horizontalPPI = display.getDPI().x;
		// this.verticalPPI = display.getDPI().y;
	}

	public int getHorizontalPPI() {
		if (!this.loaded) {
			this.load();
		}
		return this.horizontalPPI;
	}

	public int getVerticalPPI() {
		if (!this.loaded) {
			this.load();
		}
		return this.verticalPPI;
	}

	private boolean loaded = false;
	private int horizontalPPI = 72;
	private int verticalPPI = 72;

	private void load() {
		Display display = Display.getCurrent();
		if (display != null) {
			this.horizontalPPI = display.getDPI().x;
			this.verticalPPI = display.getDPI().y;
			this.loaded = true;
		}
	}

}