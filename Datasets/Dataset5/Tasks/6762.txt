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

import org.eclipse.wst.xml.vex.core.internal.core.FontResource;

/**
 * Wrapper for the SWT Font class.
 */
public class SwtFont implements FontResource {

	private org.eclipse.swt.graphics.Font swtFont;

	public SwtFont(org.eclipse.swt.graphics.Font swtFont) {
		this.swtFont = swtFont;
	}

	org.eclipse.swt.graphics.Font getSwtFont() {
		return this.swtFont;
	}

	public void dispose() {
		this.swtFont.dispose();
	}
}