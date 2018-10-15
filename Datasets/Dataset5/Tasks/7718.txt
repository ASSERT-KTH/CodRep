//		addTestSuite(IconTest.class);

/*******************************************************************************
 * Copyright (c) 2008 Standards for Technology in Automotive Retail and others
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     David Carver (STAR) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.tests;

import junit.framework.TestSuite;

import org.eclipse.wst.xml.vex.core.tests.VEXCoreTestSuite;
import org.eclipse.wst.xml.vex.ui.internal.editor.tests.FindReplaceTargetTest;
import org.eclipse.wst.xml.vex.ui.internal.tests.ResourceTrackerTest;
import org.eclipse.wst.xml.vex.ui.tests.IconTest;

/**
 * This class specifies all the bundles of this component that provide a test
 * suite to run during automated testing.
 */
public class AllTestsSuite extends TestSuite {

	public AllTestsSuite() {
		super("All Vex Test Suites"); //$NON-NLS-1$
		addTest(VEXCoreTestSuite.suite());
//		addTest(VexUiTestSuite.suite());
		addTestSuite(IconTest.class);
		addTestSuite(ResourceTrackerTest.class);
		addTestSuite(FindReplaceTargetTest.class);	
	}

	/**
	 * This is just need to run in a development environment workbench.
	 */
	public void testAll() {
		// this method needs to exist, but doesn't really do anything
		// other than to signal to create an instance of this class.
		// The rest it automatic from the tests added in constructor.
	}

}