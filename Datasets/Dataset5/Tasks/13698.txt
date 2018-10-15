//addTestSuite(SpaceNormalizerTest.class);

/*******************************************************************************
 * Copyright (c) 2004, 2008 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.tests;

import junit.framework.Test;
import junit.framework.TestSuite;

import org.eclipse.wst.xml.vex.core.internal.css.*;
import org.eclipse.wst.xml.vex.core.internal.dom.*;
import org.eclipse.wst.xml.vex.core.internal.layout.*;

public class VEXCoreTestSuite extends TestSuite {
	public static Test suite() {
		return new VEXCoreTestSuite();
	}

	public VEXCoreTestSuite() {
		super("VEX Core Tests");
		addTestSuite(CssTest.class);
		addTestSuite(PropertyTest.class);
		addTestSuite(RuleTest.class);
		addTestSuite(SerializationTest.class);
		addTestSuite(BlockElementBoxTest.class);
		addTestSuite(DFABuilderTest.class);
		addTestSuite(DocumentWriterTest.class);
		addTestSuite(DomTest.class);
		addTestSuite(DTDValidatorTest.class);
		addTestSuite(GapContentTest.class);
		addTestSuite(SpaceNormalizerTest.class);
		addTestSuite(TextWrapperTest.class);
		addTestSuite(TestBlockElementBox.class);
		addTestSuite(TestBlocksInInlines.class);
		addTestSuite(TestDocumentTextBox.class);
		addTestSuite(TestStaticTextBox.class);
	}
}