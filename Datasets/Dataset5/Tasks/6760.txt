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

import org.eclipse.wst.xml.vex.core.internal.core.ColorResource;

/**
 * Wrapper for the SWT Color class.
 */
public class SwtColor implements ColorResource {

	private org.eclipse.swt.graphics.Color swtColor;

	public SwtColor(org.eclipse.swt.graphics.Color swtColor) {
		this.swtColor = swtColor;
	}

	org.eclipse.swt.graphics.Color getSwtColor() {
		return this.swtColor;
	}

	public void dispose() {
		this.swtColor.dispose();
	}
}