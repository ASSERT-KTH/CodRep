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
package org.eclipse.wst.xml.vex.core.internal.dom;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.core.Graphics;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheet;
import org.eclipse.wst.xml.vex.core.internal.css.StyleSheetReader;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentReader;
import org.eclipse.wst.xml.vex.core.internal.layout.BlockElementBox;
import org.eclipse.wst.xml.vex.core.internal.layout.Box;
import org.eclipse.wst.xml.vex.core.internal.layout.CssBoxFactory;
import org.eclipse.wst.xml.vex.core.internal.layout.FakeGraphics;
import org.eclipse.wst.xml.vex.core.internal.layout.LayoutContext;
import org.eclipse.wst.xml.vex.core.internal.layout.RootBox;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXDocument;

import junit.framework.TestCase;

@SuppressWarnings("restriction")
public class BlockElementBoxTest extends TestCase {

	private Graphics g;
	private LayoutContext context;

	public BlockElementBoxTest() throws Exception {

		StyleSheetReader ssReader = new StyleSheetReader();
		StyleSheet ss = ssReader.read(this.getClass().getResource("test.css"));

		this.g = new FakeGraphics();

		this.context = new LayoutContext();
		this.context.setBoxFactory(new CssBoxFactory());
		this.context.setGraphics(this.g);
		this.context.setStyleSheet(ss);

	}

	public void testPositioning() throws Exception {

		String docString = "<root><small/><medium/><large/></root>";
		DocumentReader docReader = new DocumentReader();
		docReader.setDebugging(true);
		VEXDocument doc = docReader.read(docString);
		context.setDocument(doc);
		
		RootBox parentBox = new RootBox(context, doc.getRootElement(), 500);
		
		BlockElementBox box = new BlockElementBox(context, parentBox, doc
				.getRootElement());

		List childrenList = box.createChildren(context);		
		
		Box[] children = new Box[childrenList.size()];
        childrenList.toArray(children);
		assertNotNull("No Children created.", children);
		assertEquals(3, children.length);

		Box child = children[1];
	}

	public int getGap(BlockElementBox box, int n) throws SecurityException,
			NoSuchMethodException, IllegalArgumentException,
			IllegalAccessException, InvocationTargetException {
		Method getGap = BlockElementBox.class.getDeclaredMethod("getGap",
				new Class[] { Integer.TYPE });
		getGap.setAccessible(true);
		return ((Integer) getGap.invoke(box, new Object[] { new Integer(n) }))
				.intValue();
	}
}