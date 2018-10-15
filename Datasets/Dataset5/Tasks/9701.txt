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
package org.eclipse.wst.xml.vex.core.internal.layout;

import java.net.URL;

import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheetReader;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.RootElement;
import org.eclipse.wst.xml.vex.core.internal.layout.BlockElementBox;
import org.eclipse.wst.xml.vex.core.internal.layout.BlockPseudoElementBox;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext;
import org.eclipse.wst.xml.vex.core.internal.layout.RootBox;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;

import junit.framework.TestCase;

@SuppressWarnings("restriction")
public class TestBlockElementBox extends TestCase {

	FakeGraphics g;
	LayoutContext context;

	public TestBlockElementBox() throws Exception {
		URL url = this.getClass().getResource("test.css");
		StyleSheetReader reader = new StyleSheetReader();
		StyleSheet ss = reader.read(url);

		this.g = new FakeGraphics();

		this.context = new LayoutContext();
		this.context.setBoxFactory(new MockBoxFactory());
		this.context.setGraphics(this.g);
		this.context.setStyleSheet(ss);
	}
 
	public void testBeforeAfter() throws Exception {
		RootElement root = new RootElement("root");
		VEXDocument doc = new Document(root);
		doc.insertElement(1, new Element("beforeBlock"));
		context.setDocument(doc);

		RootBox rootBox = new RootBox(this.context, root, 500);
		rootBox.layout(this.context, 0, Integer.MAX_VALUE);

		Box[] children;
		BlockElementBox beb;

		children = rootBox.getChildren();
		assertEquals(1, children.length);
		assertEquals(BlockElementBox.class, children[0].getClass());
		beb = (BlockElementBox) children[0];
		assertEquals(root, beb.getElement());

		children = beb.getChildren();
		assertEquals(1, children.length);
		assertEquals(BlockElementBox.class, children[0].getClass());
		beb = (BlockElementBox) children[0];
		assertEquals("beforeBlock", beb.getElement().getName());

	}

}