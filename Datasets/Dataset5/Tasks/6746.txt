package org.eclipse.wst.xml.vex.ui.internal.swing;

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

package org.eclipse.wst.xml.vex.core.internal.swing;

import java.awt.Toolkit;

import org.eclipse.wst.xml.vex.core.internal.core.DisplayDevice;

/**
 * Swing implementation of the Display Device abstract class
 * 
 * @author Vincent Lambert, Matrox Imaging
 */
public class AwtDisplayDevice extends DisplayDevice {

	private boolean loaded = false;
	private int horizontalPPI = 72;
	private int verticalPPI = 72;

	/** Creates a new instance of AwtDisplayDevice */
	public AwtDisplayDevice() {
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

	private void load() {
		Toolkit tk = Toolkit.getDefaultToolkit();

		this.horizontalPPI = tk.getScreenResolution();
		this.verticalPPI = tk.getScreenResolution();
		this.loaded = true;
	}
}