package org.eclipse.jst.ws.jaxws.core.tests;

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.jaxws.core.tests;

import junit.framework.TestSuite;

/**
 * This class specifies all the bundles of this component that provide a test
 * suite to run during automated testing.
 */

public class AllTestsSuite extends TestSuite {

    public AllTestsSuite() {
        super("JAX-WS Core Tests");
        addTestSuite(AddAnnotationToTypeTest.class);
        addTestSuite(RemoveAnnotationFromTypeTest.class);
        addTestSuite(AddAnnotationToFieldTest.class);
        addTestSuite(RemoveAnnotationFromFieldTest.class);
        addTestSuite(AddAnnotationToMethodTest.class);
        addTestSuite(RemoveAnnotationFromMethodTest.class);
        addTestSuite(AddAnnotationToMethodParameterTest.class);
        addTestSuite(RemoveAnnotationFromMethodParameterTest.class);        
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