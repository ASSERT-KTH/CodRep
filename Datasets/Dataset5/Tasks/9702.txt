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

import org.eclipse.wst.xml.vex.core.internal.core.DisplayDevice;
import org.eclipse.wst.xml.vex.core.internal.css.MockDisplayDevice;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheetReader;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.RootElement;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext;
import org.eclipse.wst.xml.vex.core.internal.layout.RootBox;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;

import junit.framework.TestCase;

/**
 * Tests proper function of a block-level element within an inline element.
 * These must be layed out as a block child of the containing block element.
 */
@SuppressWarnings("restriction")
public class TestBlocksInInlines extends TestCase {

	FakeGraphics g;
	LayoutContext context;

	@Override
	protected void setUp() throws Exception {
		super.setUp();
		DisplayDevice.setCurrent(new MockDisplayDevice(90, 90));
	}
	
	public TestBlocksInInlines() throws Exception {
		URL url = this.getClass().getResource("test.css");
		StyleSheetReader reader = new StyleSheetReader();
		StyleSheet ss = reader.read(url);

		this.g = new FakeGraphics();

		this.context = new LayoutContext();
		this.context.setBoxFactory(new MockBoxFactory());
		this.context.setGraphics(this.g);
		this.context.setStyleSheet(ss);
	}

	public void testBlockInInline() throws Exception {
		RootElement root = new RootElement("root");
		VEXDocument doc = new Document(root);
		context.setDocument(doc);

		doc.insertText(1, "one  five");
		doc.insertElement(5, new Element("b"));
		doc.insertText(6, "two  four");
		doc.insertElement(10, new Element("p"));
		doc.insertText(11, "three");

		RootBox rootBox = new RootBox(this.context, root, 500);
		rootBox.layout(this.context, 0, Integer.MAX_VALUE);

	}
}