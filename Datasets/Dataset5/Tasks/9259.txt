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

import org.eclipse.wst.xml.vex.core.internal.core.DisplayDevice;
import org.w3c.css.sac.LexicalUnit;

/**
 * The border-XXX-width CSS property. Since the value of this property depends
 * on the corresponding border-XXX-style property, the style property must be
 * calculated first and placed in the styles, and its name given to the
 * constructor of this class.
 */
public class BorderWidthProperty extends AbstractProperty {

	/**
	 * Class constructor.
	 * 
	 * @param name
	 *            Name of the property.
	 * @param borderStyleName
	 *            Name of the corresponding border style property. For example,
	 *            if name is CSS.BORDER_TOP_WIDTH, then borderStyleName should
	 *            be CSS.BORDER_TOP_STYLE.
	 * @param axis
	 *            AXIS_HORIZONTAL (for left and right borders) or AXIS_VERTICAL
	 *            (for top and bottom borders).
	 */
	public BorderWidthProperty(String name, String borderStyleName, byte axis) {
		super(name);
		this.borderStyleName = borderStyleName;
		this.axis = axis;
	}

	/**
	 * Returns true if the given lexical unit represents a border width.
	 * 
	 * @param lu
	 *            LexicalUnit to check.
	 */
	public static boolean isBorderWidth(LexicalUnit lu) {
		if (lu == null) {
			return false;
		} else if (isLength(lu)) {
			return true;
		} else if (lu.getLexicalUnitType() == LexicalUnit.SAC_IDENT) {
			String s = lu.getStringValue();
			return s.equals(CSS.THIN) || s.equals(CSS.MEDIUM)
					|| s.equals(CSS.THICK);
		} else {
			return false;
		}
	}

	public Object calculate(LexicalUnit lu, Styles parentStyles, Styles styles) {
		return new Integer(this.calculateInternal(lu, parentStyles, styles));
	}

	private int calculateInternal(LexicalUnit lu, Styles parentStyles,
			Styles styles) {

		DisplayDevice device = DisplayDevice.getCurrent();
		int ppi = this.axis == AXIS_HORIZONTAL ? device.getHorizontalPPI()
				: device.getVerticalPPI();

		String borderStyle = (String) styles.get(this.borderStyleName);

		if (borderStyle.equals(CSS.NONE) || borderStyle.equals(CSS.HIDDEN)) {
			return 0;
		} else if (isBorderWidth(lu)) {
			return getBorderWidth(lu, styles.getFontSize(), ppi);
		} else if (isInherit(lu) && parentStyles != null) {
			return ((Integer) parentStyles.get(this.getName())).intValue();
		} else {
			// not specified, "none", or other unknown value
			return BORDER_WIDTH_MEDIUM;
		}
	}

	// =================================================== PRIVATE

	// Name of the corresponding border style property
	private String borderStyleName;

	// Axis along which the border width is measured.
	private byte axis;

	// named border widths
	private static final int BORDER_WIDTH_THIN = 1;
	private static final int BORDER_WIDTH_MEDIUM = 3;
	private static final int BORDER_WIDTH_THICK = 5;

	private static int getBorderWidth(LexicalUnit lu, float fontSize, int ppi) {
		if (isLength(lu)) {
			return getIntLength(lu, fontSize, ppi);
		} else if (lu.getLexicalUnitType() == LexicalUnit.SAC_IDENT) {
			String s = lu.getStringValue();
			if (s.equals(CSS.THIN)) {
				return BORDER_WIDTH_THIN;
			} else if (s.equals(CSS.MEDIUM)) {
				return BORDER_WIDTH_MEDIUM;
			} else if (s.equals(CSS.THICK)) {
				return BORDER_WIDTH_THICK;
			} else {
				return 0;
			}
		} else {
			return 0;
		}
	}

}