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

import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Stack;

import javax.xml.parsers.FactoryConfigurationError;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParserFactory;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;

import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheetReader;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentReader;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext;
import org.eclipse.wst.xml.vex.core.internal.layout.RootBox;
import org.eclipse.wst.xml.vex.core.internal.layout.TextBox;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IWhitespacePolicy;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IWhitespacePolicyFactory;
import org.eclipse.wst.xml.vex.core.internal.widget.CssWhitespacePolicy;
import org.xml.sax.Attributes;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.DefaultHandler;

/**
 * Runs several suites of layout tests. Each suite is defined in an XML file.
 * The XML files to run are registered in the suite() method.
 */
@SuppressWarnings("restriction")
public class LayoutTestSuite extends TestCase {

	public String id;
	public String doc;
	public int layoutWidth = 100;
	public BoxSpec result;
	public String css;

	public static Test suite() throws ParserConfigurationException,
			FactoryConfigurationError, IOException, SAXException {
		TestSuite suite = new TestSuite(LayoutTestSuite.class.getName());
		suite.addTest(loadSuite("block-inline.xml"));
		suite.addTest(loadSuite("before-after.xml"));
		suite.addTest(loadSuite("linebreaks.xml"));
		suite.addTest(loadSuite("tables.xml"));
		return suite;
	}

	public static Test loadSuite(String filename)
			throws ParserConfigurationException, FactoryConfigurationError,
			IOException, SAXException {
		XMLReader xmlReader = SAXParserFactory.newInstance().newSAXParser()
				.getXMLReader();
		TestCaseBuilder builder = new TestCaseBuilder();
		xmlReader.setContentHandler(builder);
		// xmlReader.setEntityResolver(builder);
		URL url = LayoutTestSuite.class.getResource(filename);
		xmlReader.parse(new InputSource(url.toString()));

		TestSuite suite = new TestSuite(filename);
		for (Iterator it = builder.testCases.iterator(); it.hasNext();) {
			LayoutTestSuite test = (LayoutTestSuite) it.next();
			suite.addTest(test);
		}
		return suite;
	}

	public LayoutTestSuite() {
		super("testLayout");
	}

	public String getName() {
		return this.id;
	}

	public void testLayout() throws Exception {

		URL url = LayoutTestSuite.class.getResource(this.css);
		StyleSheetReader reader = new StyleSheetReader();
		final StyleSheet ss = reader.read(url);

		FakeGraphics g = new FakeGraphics();

		LayoutContext context = new LayoutContext();
		context.setBoxFactory(new MockBoxFactory());
		context.setGraphics(g);
		context.setStyleSheet(ss);

		DocumentReader docReader = new DocumentReader();
		docReader.setWhitespacePolicyFactory(new IWhitespacePolicyFactory() {
			public IWhitespacePolicy getPolicy(String publicId) {
				return new CssWhitespacePolicy(ss);
			}
		});
		VEXDocument doc = docReader.read(this.doc);
		context.setDocument(doc);

		RootBox rootBox = new RootBox(context, doc.getRootElement(),
				this.layoutWidth);
		rootBox.layout(context, 0, Integer.MAX_VALUE);

		assertBox(this.result, rootBox, "");
	}

	private static void assertBox(BoxSpec boxSpec, Box box, String indent) {

		System.out.println(indent + boxSpec.className);

		if (boxSpec.className != null) {
			String actualClassName = box.getClass().getName();
			if (boxSpec.className.lastIndexOf('.') == -1) {
				// no dot in box spec classname, so strip the prefix from the
				// actual classname
				int lastDot = actualClassName.lastIndexOf('.');
				actualClassName = actualClassName.substring(lastDot + 1);
			}
			assertEquals(boxSpec.className, actualClassName);
		}

		if (boxSpec.element != null) {
			assertNotNull(box.getElement());
			assertEquals(boxSpec.element, box.getElement().getName());
		}

		if (boxSpec.text != null && box instanceof TextBox) {
			assertEquals(boxSpec.text, ((TextBox) box).getText());
		}

		if (boxSpec.children.size() > 0 && box.getChildren() == null) {
			fail("Expected " + boxSpec.children.size() + " children, but "
					+ boxSpec.className + "'s children is null");
		}

		if (boxSpec.children.size() != box.getChildren().length) {
			System.out.println("Wrong number of child boxes");
			System.out.println("  Expected:");
			for (Iterator it = boxSpec.children.iterator(); it.hasNext();) {
				BoxSpec childSpec = (BoxSpec) it.next();
				System.out.print("    " + childSpec.className);
				if (childSpec.text != null) {
					System.out.print(" '" + childSpec.text + "'");
				}
				System.out.println();
			}
			System.out.println("  Actual:");
			for (int i = 0; i < box.getChildren().length; i++) {
				Box childBox = box.getChildren()[i];
				System.out.println("    " + childBox.getClass() + ": "
						+ childBox);
			}
			fail("Wrong number of child boxes.");
		}

		for (int i = 0; i < boxSpec.children.size(); i++) {
			assertBox((BoxSpec) boxSpec.children.get(i), box.getChildren()[i],
					indent + "  ");
		}

	}

	private static class TestCaseBuilder extends DefaultHandler {

		private List testCases;
		private String css;
		private LayoutTestSuite testCase;
		private BoxSpec boxSpec;
		private Stack boxSpecs;
		private boolean inDoc;

		public void characters(char[] ch, int start, int length)
				throws SAXException {

			String s = new String(ch, start, length).trim();
			if (s.length() > 0) {
				if (inDoc) {
					this.testCase.doc = new String(ch, start, length);
				} else {
					throw new IllegalStateException();
				}
			}
		}

		public void endElement(String uri, String localName, String qName)
				throws SAXException {
			if (qName.equals("box")) {
				if (this.boxSpecs.isEmpty()) {
					this.boxSpec = null;
				} else {
					this.boxSpec = (BoxSpec) this.boxSpecs.pop();
				}
			} else if (qName.equals("doc")) {
				this.inDoc = false;
			}
		}

		public void startElement(String uri, String localName, String qName,
				Attributes attributes) throws SAXException {

			if (qName.equals("testcases")) {
				this.testCases = new ArrayList();
				this.css = attributes.getValue("css");
				if (this.css == null) {
					this.css = "test.css";
				}
				this.testCase = null;
				this.boxSpecs = new Stack();
			} else if (qName.equals("test")) {
				this.testCase = new LayoutTestSuite();
				this.testCase.id = attributes.getValue("id");
				this.testCase.css = this.css;
				String layoutWidth = attributes.getValue("layoutWidth");
				if (layoutWidth != null) {
					this.testCase.layoutWidth = Integer.parseInt(layoutWidth);
				}
				testCases.add(this.testCase);
			} else if (qName.equals("doc")) {
				this.inDoc = true;
			} else if (qName.equals("result")) {
			} else if (qName.equals("box")) {
				BoxSpec parent = this.boxSpec;
				this.boxSpec = new BoxSpec();
				this.boxSpec.className = attributes.getValue("class");
				this.boxSpec.element = attributes.getValue("element");
				this.boxSpec.text = attributes.getValue("text");
				if (parent == null) {
					this.testCase.result = this.boxSpec;
				} else {
					this.boxSpecs.push(parent);
					parent.children.add(this.boxSpec);
				}
			} else {
				throw new SAXException("Unrecognized element: " + qName);
			}
		}
	}

	private static class BoxSpec {
		public String className;
		public String element;
		public List children = new ArrayList();
		public String text;
	}

}