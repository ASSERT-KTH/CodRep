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
package org.eclipse.wst.xml.vex.core.internal.widget;

import org.eclipse.wst.xml.vex.core.internal.css.CSS;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IWhitespacePolicy;

/**
 * Implementation of WhitespacePolicy using a CSS stylesheet.
 */
public class CssWhitespacePolicy implements IWhitespacePolicy {

	/**
	 * Class constructor.
	 * 
	 * @param styleSheet
	 *            The stylesheet used for the policy.
	 */
	public CssWhitespacePolicy(StyleSheet styleSheet) {
		this.styleSheet = styleSheet;
	}

	public boolean isBlock(VEXElement element) {
		return this.styleSheet.getStyles(element).isBlock();
	}

	public boolean isPre(VEXElement element) {
		return CSS.PRE.equals(this.styleSheet.getStyles(element)
				.getWhiteSpace());
	}

	// ===================================================== PRIVATE

	private StyleSheet styleSheet;
}