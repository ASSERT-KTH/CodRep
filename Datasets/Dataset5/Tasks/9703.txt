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
import org.eclipse.wst.xml.vex.core.internal.css.Styles;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.RootElement;
import org.eclipse.wst.xml.vex.core.internal.layout.CssBoxFactory;
import org.eclipse.wst.xml.vex.core.internal.layout.DocumentTextBox;
import org.eclipse.wst.xml.vex.core.internal.layout.InlineBox;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;

import junit.framework.TestCase;

/**
 * Tests the DocumentTestBox class. We focus here on proper offsets, since text
 * splitting is tested thoroughly in TestStaticTextBox.
 */
@SuppressWarnings("restriction")
public class TestDocumentTextBox extends TestCase {

	FakeGraphics g;
	LayoutContext context;

	public TestDocumentTextBox() throws Exception {

		URL url = this.getClass().getResource("test.css");
		StyleSheetReader reader = new StyleSheetReader();
		StyleSheet ss = reader.read(url);

		this.g = new FakeGraphics();

		this.context = new LayoutContext();
		this.context.setBoxFactory(new CssBoxFactory());
		this.context.setGraphics(this.g);
		this.context.setStyleSheet(ss);
	}

	public void testSplit() throws Exception {
		RootElement root = new RootElement("root");
		VEXDocument doc = new Document(root);

		Styles styles = this.context.getStyleSheet().getStyles(root);

		int width = g.getCharWidth();

		// 0 6 13 21
		// / / / /
		// baggy orange trousers

		doc.insertText(1, "baggy orange trousers");
		DocumentTextBox box = new DocumentTextBox(this.context, root, 1, 22);
		assertEquals(box.getText().length() * width, box.getWidth());
		assertEquals(styles.getLineHeight(), box.getHeight());
		assertSplit(box, 22, false, "baggy orange ", "trousers");
		assertSplit(box, 21, false, "baggy orange ", "trousers");
		assertSplit(box, 20, false, "baggy orange ", "trousers");
		assertSplit(box, 13, false, "baggy orange ", "trousers");
		assertSplit(box, 12, false, "baggy ", "orange trousers");
		assertSplit(box, 6, false, "baggy ", "orange trousers");
		assertSplit(box, 5, false, null, "baggy orange trousers");
		assertSplit(box, 1, false, null, "baggy orange trousers");
		assertSplit(box, 0, false, null, "baggy orange trousers");
		assertSplit(box, -1, false, null, "baggy orange trousers");

		assertSplit(box, 22, true, "baggy orange ", "trousers");
		assertSplit(box, 21, true, "baggy orange ", "trousers");
		assertSplit(box, 20, true, "baggy orange ", "trousers");
		assertSplit(box, 13, true, "baggy orange ", "trousers");
		assertSplit(box, 12, true, "baggy ", "orange trousers");
		assertSplit(box, 6, true, "baggy ", "orange trousers");
		assertSplit(box, 5, true, "baggy ", "orange trousers");
		assertSplit(box, 4, true, "bagg", "y orange trousers");
		assertSplit(box, 3, true, "bag", "gy orange trousers");
		assertSplit(box, 2, true, "ba", "ggy orange trousers");
		assertSplit(box, 1, true, "b", "aggy orange trousers");
		assertSplit(box, 0, true, "b", "aggy orange trousers");
		assertSplit(box, -1, true, "b", "aggy orange trousers");

		doc.delete(1, 22);
	}

	private void assertSplit(DocumentTextBox box, int splitPos, boolean force,
			String left, String right) {

		Styles styles = this.context.getStyleSheet()
				.getStyles(box.getElement());

		int width = g.getCharWidth();

		InlineBox.Pair pair = box.split(context, splitPos * width, force);

		DocumentTextBox leftBox = (DocumentTextBox) pair.getLeft();
		DocumentTextBox rightBox = (DocumentTextBox) pair.getRight();

		int leftOffset = 1;
		int midOffset = leftOffset + (left == null ? 0 : left.length());
		int rightOffset = leftOffset + box.getText().length();

		if (left == null) {
			assertNull(leftBox);
		} else {
			assertNotNull(leftBox);
			assertEquals(left, leftBox.getText());
			assertEquals(left.length() * width, leftBox.getWidth());
			assertEquals(styles.getLineHeight(), leftBox.getHeight());
			assertEquals(leftOffset, leftBox.getStartOffset());
			assertEquals(midOffset - 1, leftBox.getEndOffset());
		}

		if (right == null) {
			assertNull(rightBox);
		} else {
			assertNotNull(rightBox);
			assertEquals(right, rightBox.getText());
			assertEquals(right.length() * width, rightBox.getWidth());
			assertEquals(styles.getLineHeight(), rightBox.getHeight());
			assertEquals(midOffset, rightBox.getStartOffset());
			assertEquals(rightOffset - 1, rightBox.getEndOffset());
		}

	}
}