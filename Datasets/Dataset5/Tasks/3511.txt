package org.eclipse.jst.ws.cxf.tests;

/*******************************************************************************
 * Copyright (c) 2008 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.cfx.tests;

import junit.framework.TestSuite;

import org.eclipse.jst.ws.jaxb.core.tests.JAXBCoreTestSuite;
import org.eclipse.jst.ws.jaxws.core.annotation.validation.tests.JAXWSAnnotationValidationTestSuite;
import org.eclipse.jst.ws.jaxws.core.tests.JAXWSCoreTestSuite;

/**
 * This class specifies all the bundles of this component that provide a test
 * suite to run during automated testing.
 */
public class AllTestsSuite extends TestSuite {


	public AllTestsSuite() {
		super("All JAXWS and JAXB Test Suites");
		addTest(JAXWSCoreTestSuite.suite());
		addTest(JAXWSAnnotationValidationTestSuite.suite());
		addTest(JAXBCoreTestSuite.suite());
		
		//Adding two JAX-WS DOM Tools test suites for a trial run
		addTest(org.eclipse.jst.ws.jaxws.dom.integration.tests.dom.AllTestsSuite.suite());
		addTest(org.eclipse.jst.ws.jaxws.dom.runtime.tests.AllTestsSuite.suite());
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