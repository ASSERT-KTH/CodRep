import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.*;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types;

import static org.junit.Assert.*;
import static org.eclipse.xtend.backend.helpers.BackendTestHelper.*;

import java.util.Arrays;

import org.eclipse.xtend.backend.expr.PropertyOnObjectExpression;
import org.junit.Test;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class AbstractTypeTest {
    @Test public void testInheritedProperties () {
        // tests that ListType inherits the property "size" from CollectionType
        assertEquals (2L, new PropertyOnObjectExpression (createLiteral (Arrays.asList ("a", "b")), "size", SOURCE_POS).evaluate (createEmptyExecutionContext()));
    }
}