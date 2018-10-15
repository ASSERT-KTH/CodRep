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
 *     Dave Holroyd - Implement font-weight:bolder
 *     Dave Holroyd - Implement text decoration
 *     John Austin - More complete CSS constants. Add the colour "orange".
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.css;

import java.io.Serializable;
import java.lang.ref.WeakReference;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

import org.eclipse.wst.xml.vex.core.internal.core.FontSpec;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;
import org.w3c.css.sac.LexicalUnit;

/**
 * Represents a CSS style sheet.
 */
public class StyleSheet implements Serializable {

	/**
	 * Standard CSS properties.
	 */
	private static final IProperty[] CSS_PROPERTIES = new IProperty[] {
			new DisplayProperty(),
			new LineHeightProperty(),
			new ListStyleTypeProperty(),
			new TextAlignProperty(),
			new WhiteSpaceProperty(),

			new FontFamilyProperty(),
			new FontSizeProperty(),
			new FontStyleProperty(),
			new FontWeightProperty(),
			new TextDecorationProperty(),

			new ColorProperty(CSS.COLOR),
			new ColorProperty(CSS.BACKGROUND_COLOR),

			new LengthProperty(CSS.MARGIN_BOTTOM, IProperty.AXIS_VERTICAL),
			new LengthProperty(CSS.MARGIN_LEFT, IProperty.AXIS_HORIZONTAL),
			new LengthProperty(CSS.MARGIN_RIGHT, IProperty.AXIS_HORIZONTAL),
			new LengthProperty(CSS.MARGIN_TOP, IProperty.AXIS_VERTICAL),

			new LengthProperty(CSS.PADDING_BOTTOM, IProperty.AXIS_VERTICAL),
			new LengthProperty(CSS.PADDING_LEFT, IProperty.AXIS_HORIZONTAL),
			new LengthProperty(CSS.PADDING_RIGHT, IProperty.AXIS_HORIZONTAL),
			new LengthProperty(CSS.PADDING_TOP, IProperty.AXIS_VERTICAL),

			new ColorProperty(CSS.BORDER_BOTTOM_COLOR),
			new ColorProperty(CSS.BORDER_LEFT_COLOR),
			new ColorProperty(CSS.BORDER_RIGHT_COLOR),
			new ColorProperty(CSS.BORDER_TOP_COLOR),
			new BorderStyleProperty(CSS.BORDER_BOTTOM_STYLE),
			new BorderStyleProperty(CSS.BORDER_LEFT_STYLE),
			new BorderStyleProperty(CSS.BORDER_RIGHT_STYLE),
			new BorderStyleProperty(CSS.BORDER_TOP_STYLE),
			new BorderWidthProperty(CSS.BORDER_BOTTOM_WIDTH,
					CSS.BORDER_BOTTOM_STYLE, IProperty.AXIS_VERTICAL),
			new BorderWidthProperty(CSS.BORDER_LEFT_WIDTH,
					CSS.BORDER_LEFT_STYLE, IProperty.AXIS_HORIZONTAL),
			new BorderWidthProperty(CSS.BORDER_RIGHT_WIDTH,
					CSS.BORDER_RIGHT_STYLE, IProperty.AXIS_HORIZONTAL),
			new BorderWidthProperty(CSS.BORDER_TOP_WIDTH, CSS.BORDER_TOP_STYLE,
					IProperty.AXIS_VERTICAL), new BorderSpacingProperty(), };

	/**
	 * The properties to calculate. This can be changed by the app.
	 */
	private static IProperty[] properties = CSS_PROPERTIES;

	/**
	 * Style sheet is the default for the renderer.
	 */
	public static final byte SOURCE_DEFAULT = 0;

	/**
	 * Style sheet was provided by the document author.
	 */
	public static final byte SOURCE_AUTHOR = 1;

	/**
	 * Style sheet was provided by the user.
	 */
	public static final byte SOURCE_USER = 2;

	/**
	 * The rules that comprise the stylesheet.
	 */
	private Rule[] rules;

	/**
	 * Computing styles can be expensive, e.g. we have to calculate the styles
	 * of all parents of an element. We therefore cache styles in a map of
	 * element => WeakReference(styles). A weak hash map is used to avoid
	 * leaking memory as elements are deleted. By using weak references to the
	 * values, we also ensure the cache is memory-sensitive.
	 * 
	 * This must be transient to prevent it from being serialized, as
	 * WeakHashMaps are not serializable.
	 */
	private transient Map styleMap = null;

	/**
	 * Class constructor.
	 * 
	 * @param rules
	 *            Rules that constitute the style sheet.
	 */
	public StyleSheet(Rule[] rules) {
		this.rules = rules;
	}

	/**
	 * Flush any cached styles for the given element.
	 * 
	 * @param element
	 *            IVEXElement for which styles are to be flushed.
	 */
	public void flushStyles(VEXElement element) {
		this.getStyleMap().remove(element);
	}

	/**
	 * Returns a pseudo-element representing content to be displayed after the
	 * given element, or null if there is no such content.
	 * 
	 * @param element
	 *            Parent element of the pseudo-element.
	 */
	public VEXElement getAfterElement(VEXElement element) {
		PseudoElement pe = new PseudoElement(element, PseudoElement.AFTER);
		Styles styles = this.getStyles(pe);
		if (styles == null) {
			return null;
		} else {
			return pe;
		}
	}

	/**
	 * Returns a pseudo-element representing content to be displayed before the
	 * given element, or null if there is no such content.
	 * 
	 * @param element
	 *            Parent element of the pseudo-element.
	 */
	public VEXElement getBeforeElement(VEXElement element) {
		PseudoElement pe = new PseudoElement(element, PseudoElement.BEFORE);
		Styles styles = this.getStyles(pe);
		if (styles == null) {
			return null;
		} else {
			return pe;
		}
	}

	/**
	 * Returns the array of standard CSS properties.
	 */
	public static IProperty[] getCssProperties() {
		return CSS_PROPERTIES;
	}

	/**
	 * Returns the styles for the given element. The styles are cached to ensure
	 * reasonable performance.
	 * 
	 * @param element
	 *            IVEXElement for which to calculate the styles.
	 */
	public Styles getStyles(VEXElement element) {

		Styles styles;
		WeakReference ref = (WeakReference) this.getStyleMap().get(element);

		if (ref != null) {
			// can't combine these tests, since calling ref.get() twice
			// (once to query for null, once to get the value) would
			// cause a race condition should the GC happen btn the two.
			styles = (Styles) ref.get();
			if (styles != null) {
				return styles;
			}
		} else if (this.getStyleMap().containsKey(element)) {
			// this must be a pseudo-element with no content
			return null;
		}

		styles = calculateStyles(element);

		if (styles == null) {
			// Yes, they can be null if element is a PseudoElement with no
			// content property
			this.getStyleMap().put(element, null);
		} else {
			this.getStyleMap().put(element, new WeakReference(styles));
		}

		return styles;
	}

	private Styles calculateStyles(VEXElement element) {

		Styles styles = new Styles();
		Styles parentStyles = null;
		if (element.getParent() != null) {
			parentStyles = this.getStyles(element.getParent());
		}

		Map decls = this.getApplicableDecls(element);

		LexicalUnit lu;

		// If we're finding a pseudo-element, look at the 'content' property
		// first, since most of the time it'll be empty and we'll return null.
		if (element instanceof PseudoElement) {
			lu = (LexicalUnit) decls.get(CSS.CONTENT);
			if (lu == null) {
				return null;
			}

			List content = new ArrayList();
			while (lu != null) {
				if (lu.getLexicalUnitType() == LexicalUnit.SAC_STRING_VALUE) {
					content.add(lu.getStringValue());
				}
				lu = lu.getNextLexicalUnit();
			}
			styles.setContent(content);
		}

		for (int i = 0; i < properties.length; i++) {
			IProperty property = properties[i];
			lu = (LexicalUnit) decls.get(property.getName());
			Object value = property.calculate(lu, parentStyles, styles);
			styles.put(property.getName(), value);
		}

		// Now, map font-family, font-style, font-weight, and font-size onto
		// an AWT font.

		int styleFlags = FontSpec.PLAIN;
		String fontStyle = styles.getFontStyle();
		if (fontStyle.equals(CSS.ITALIC) || fontStyle.equals(CSS.OBLIQUE)) {
			styleFlags |= FontSpec.ITALIC;
		}
		if (styles.getFontWeight() > 550) {
			// 550 is halfway btn normal (400) and bold (700)
			styleFlags |= FontSpec.BOLD;
		}
		String textDecoration = styles.getTextDecoration();
		if (textDecoration.equals(CSS.UNDERLINE)) {
			styleFlags |= FontSpec.UNDERLINE;
		} else if (textDecoration.equals(CSS.OVERLINE)) {
			styleFlags |= FontSpec.OVERLINE;
		} else if (textDecoration.equals(CSS.LINE_THROUGH)) {
			styleFlags |= FontSpec.LINE_THROUGH;
		}

		styles.setFont(new FontSpec(styles.getFontFamilies(), styleFlags, Math
				.round(styles.getFontSize())));

		return styles;
	}

	/**
	 * Returns the list of properties to be parsed by StyleSheets in this app.
	 */
	public static IProperty[] getProperties() {
		return StyleSheet.properties;
	}

	/**
	 * Returns the rules comprising this stylesheet.
	 */
	public Rule[] getRules() {
		return this.rules;
	}

	/**
	 * Sets the list of properties to be used by StyleSheets in this
	 * application.
	 * 
	 * @param properties
	 *            New array of IProperty objects to be used.
	 */
	public static void setProperties(IProperty[] properties) {
		StyleSheet.properties = properties;
	}

	// ========================================================= PRIVATE

	/**
	 * Returns all the declarations that apply to the given element.
	 */
	private Map getApplicableDecls(VEXElement element) {
		// Find all the property declarations that apply to this element.
		List declList = new ArrayList();
		Rule[] rules = this.getRules();

		for (int i = 0; i < rules.length; i++) {
			Rule rule = rules[i];
			if (rule.matches(element)) {
				PropertyDecl[] ruleDecls = rule.getPropertyDecls();
				for (int j = 0; j < ruleDecls.length; j++) {
					declList.add(ruleDecls[j]);
				}
			}
		}

		// Sort in cascade order. We can then just stuff them into a
		// map and get the right values since higher-priority values
		// come later and overwrite lower-priority ones.
		Collections.sort(declList);

		Map decls = new HashMap();
		Iterator iter = declList.iterator();
		while (iter.hasNext()) {
			PropertyDecl decl = (PropertyDecl) iter.next();
			PropertyDecl prevDecl = (PropertyDecl) decls
					.get(decl.getProperty());
			if (prevDecl == null || !prevDecl.isImportant()
					|| decl.isImportant()) {
				decls.put(decl.getProperty(), decl);
			}
		}

		Map values = new HashMap();
		for (Iterator it = decls.keySet().iterator(); it.hasNext();) {
			PropertyDecl decl = (PropertyDecl) decls.get(it.next());
			values.put(decl.getProperty(), decl.getValue());
		}

		return values;
	}

	private Map getStyleMap() {
		if (this.styleMap == null) {
			this.styleMap = new WeakHashMap();
		}
		return this.styleMap;
	}
}