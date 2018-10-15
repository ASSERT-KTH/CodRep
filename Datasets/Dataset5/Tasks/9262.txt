return Integer.valueOf(calculateInternal(lu, parentStyles, styles));

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

import org.w3c.css.sac.LexicalUnit;

/**
 * The CSS font-weight property.
 */
public class FontWeightProperty extends AbstractProperty {

	private static final int FONT_WEIGHT_NORMAL = 400;
	private static final int FONT_WEIGHT_BOLD = 700;

	/**
	 * Class constructor.
	 */
	public FontWeightProperty() {
		super(CSS.FONT_WEIGHT);
	}

	public Object calculate(LexicalUnit lu, Styles parentStyles, Styles styles) {
		return new Integer(this.calculateInternal(lu, parentStyles, styles));
	}

	public int calculateInternal(LexicalUnit lu, Styles parentStyles,
			Styles styles) {
		if (isFontWeight(lu)) {
			return getFontWeight(lu, parentStyles);
		} else {
			// not specified, "inherit", or some other value
			if (parentStyles != null) {
				return parentStyles.getFontWeight();
			} else {
				return FONT_WEIGHT_NORMAL;
			}
		}

	}

	/**
	 * Returns true if the given lexical unit represents a font weight.
	 * 
	 * @param lu
	 *            LexicalUnit to check.
	 */
	public static boolean isFontWeight(LexicalUnit lu) {
		if (lu == null) {
			return false;
		} else if (lu.getLexicalUnitType() == LexicalUnit.SAC_INTEGER) {
			return true;
		} else if (lu.getLexicalUnitType() == LexicalUnit.SAC_IDENT) {
			String s = lu.getStringValue();
			return s.equals(CSS.NORMAL) || s.equals(CSS.BOLD)
					|| s.equals(CSS.BOLDER) || s.equals(CSS.LIGHTER);
		} else {
			return false;
		}
	}

	private static int getFontWeight(LexicalUnit lu, Styles parentStyles) {
		if (lu == null) {
			return FONT_WEIGHT_NORMAL;
		} else if (lu.getLexicalUnitType() == LexicalUnit.SAC_INTEGER) {
			return lu.getIntegerValue();
		} else if (lu.getLexicalUnitType() == LexicalUnit.SAC_IDENT) {
			String s = lu.getStringValue();
			if (s.equals(CSS.NORMAL)) {
				return FONT_WEIGHT_NORMAL;
			} else if (s.equals(CSS.BOLD)) {
				return FONT_WEIGHT_BOLD;
			} else if (s.equals(CSS.BOLDER)) {
				if (parentStyles != null) {
					return parentStyles.getFontWeight() + 151;
				} else {
					return FONT_WEIGHT_BOLD;
				}
			} else if (s.equals(CSS.LIGHTER)) {
				if (parentStyles != null) {
					return parentStyles.getFontWeight() - 151;
				} else {
					return FONT_WEIGHT_NORMAL;
				}
			} else {
				return FONT_WEIGHT_NORMAL;
			}
		} else {
			return FONT_WEIGHT_NORMAL;
		}
	}

}