List<String> list = new ArrayList<String>();

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
package org.eclipse.wst.xml.vex.core.internal.css;

import java.util.ArrayList;
import java.util.List;

import org.w3c.css.sac.LexicalUnit;

/**
 * The CSS 'font-family' property.
 */
public class FontFamilyProperty extends AbstractProperty {

	/**
	 * Class constructor.
	 */
	public FontFamilyProperty() {
		super(CSS.FONT_FAMILY);
	}

	/**
     *
     */

	public Object calculate(LexicalUnit lu, Styles parentStyles, Styles styles) {
		if (isFontFamily(lu)) {
			return getFontFamilies(lu);
		} else {
			// not specified, "inherit", or some other value
			if (parentStyles != null) {
				return parentStyles.getFontFamilies();
			} else {
				return DEFAULT_FONT_FAMILY;
			}
		}
	}

	// ================================================= PRIVATE

	private static final String[] DEFAULT_FONT_FAMILY = new String[] { "sans-serif" };

	private static boolean isFontFamily(LexicalUnit lu) {
		return lu != null
				&& (lu.getLexicalUnitType() == LexicalUnit.SAC_STRING_VALUE || lu
						.getLexicalUnitType() == LexicalUnit.SAC_IDENT);
	}

	private static String[] getFontFamilies(LexicalUnit lu) {
		List list = new ArrayList();
		while (lu != null) {
			if (lu.getLexicalUnitType() == LexicalUnit.SAC_STRING_VALUE
					|| lu.getLexicalUnitType() == LexicalUnit.SAC_IDENT) {

				list.add(lu.getStringValue());
			}
			lu = lu.getNextLexicalUnit();
		}
		return (String[]) list.toArray(new String[list.size()]);
	}

}