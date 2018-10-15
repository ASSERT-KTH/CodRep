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

import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;

/**
 * Wrapper for the AWT Color class.
 */
public class AwtColor implements ColorResource {

	private java.awt.Color awtColor;

	public AwtColor(java.awt.Color awtColor) {
		this.awtColor = awtColor;
	}

	java.awt.Color getAwtColor() {
		return this.awtColor;
	}

	public void dispose() {
	}
}