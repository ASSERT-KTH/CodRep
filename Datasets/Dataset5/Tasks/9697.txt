import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXDocument;

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

import java.net.URL;

import org.eclipse.wst.xml.vex.core.internal.css.Rule;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheetReader;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.RootElement;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;

import junit.framework.TestCase;

/**
 * Test rule matching.
 */
@SuppressWarnings("restriction")

public class RuleTest extends TestCase {

	public void testRuleMatching() throws Exception {
		URL url = RuleTest.class.getResource("testRules.css");
		StyleSheetReader reader = new StyleSheetReader();
		reader.setSource(StyleSheet.SOURCE_USER);
		StyleSheet ss = reader.read(url);
		Rule[] rules = ss.getRules();

		RootElement a = new RootElement("a");
		Element b = new Element("b");
		Element c = new Element("c");
		Element d = new Element("d");
		Element e = new Element("e");
		Element f = new Element("f");

		b.setAttribute("color", "blue");
		c.setAttribute("color", "blue red");
		d.setAttribute("color", "gree blue red");
		e.setAttribute("color", "red blue");
		f.setAttribute("color", "bluered");

		VEXDocument doc = new Document(a);
		doc.insertElement(1, b);
		doc.insertElement(2, c);
		doc.insertElement(3, d);
		doc.insertElement(4, e);
		doc.insertElement(5, f);

		// /* 0 */ c { }
		Rule rule = rules[0];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertTrue(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 1 */ b c { }
		rule = rules[1];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertTrue(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 2 */ b d { }
		rule = rules[2];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertTrue(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 3 */ other b c { }
		rule = rules[3];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 4 */ other b d { }
		rule = rules[4];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 5 */ a c e { }
		rule = rules[5];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertTrue(rule.matches(e));

		// /* 6 */ c a e { }
		rule = rules[6];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 7 */ * { }
		rule = rules[7];
		assertTrue(rule.matches(a));
		assertTrue(rule.matches(b));
		assertTrue(rule.matches(c));
		assertTrue(rule.matches(d));
		assertTrue(rule.matches(e));

		// /* 8 */ *[color]
		rule = rules[8];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertTrue(rule.matches(c));
		assertTrue(rule.matches(d));
		assertTrue(rule.matches(e));

		// /* 9 */ a[color]
		rule = rules[9];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 10 */ b[color]
		rule = rules[10];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 11 */ c[color]
		rule = rules[11];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertTrue(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 12 */ d[color]
		rule = rules[12];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertTrue(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 13 */ *[color=blue]
		rule = rules[13];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 14 */ a[color=blue]
		rule = rules[14];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 15 */ b[color=blue]
		rule = rules[15];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 16 */ b[color='blue']
		rule = rules[16];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 17 */ b[color="blue"]
		rule = rules[17];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 18 */ c[color=blue]
		rule = rules[18];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 19 */ a * { }
		rule = rules[19];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertTrue(rule.matches(c));
		assertTrue(rule.matches(d));
		assertTrue(rule.matches(e));

		// /* 20 */ a > * { }
		rule = rules[20];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 21 */ a *[color] { }
		rule = rules[21];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertTrue(rule.matches(c));
		assertTrue(rule.matches(d));
		assertTrue(rule.matches(e));

		// /* 22 */ a > *[color] { }
		rule = rules[22];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertFalse(rule.matches(c));
		assertFalse(rule.matches(d));
		assertFalse(rule.matches(e));

		// /* 23 */ *[color~=blue] { }
		rule = rules[23];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertTrue(rule.matches(c));
		assertTrue(rule.matches(d));
		assertTrue(rule.matches(e));
		assertFalse(rule.matches(f));

		//
		// Rules that test class conditions
		//

		b.setAttribute("class", "foo");
		c.setAttribute("class", "foo bar");
		d.setAttribute("class", "bar");

		// /* 24 */ .foo { }
		rule = rules[24];
		assertFalse(rule.matches(a));
		assertTrue(rule.matches(b));
		assertTrue(rule.matches(c));
		assertFalse(rule.matches(d));

		// /* 25 */ .foo.bar { }
		rule = rules[25];
		assertFalse(rule.matches(a));
		assertFalse(rule.matches(b));
		assertTrue(rule.matches(c));
		assertFalse(rule.matches(d));

	}
}