assertNull(javaBeansMetaType.getOperation("getMyProp", null));

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.xtend.typesystem.impl.javabeans;

import java.util.Collections;

import junit.framework.TestCase;

import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.ExpressionFacade;
import org.eclipse.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.xtend.type.impl.java.beans.JavaBeansStrategy;
import org.eclipse.xtend.typesystem.Property;
import org.eclipse.xtend.typesystem.StaticProperty;
import org.eclipse.xtend.typesystem.Type;

public class JavaBeansStrategyTest extends TestCase {
	
	private ExecutionContextImpl ec;
	private JavaBeansStrategy strategy;

	@Override
	protected void setUp() throws Exception {
		super.setUp();
		ec = new ExecutionContextImpl();
        strategy = new JavaBeansStrategy();
        ec.registerMetaModel(new JavaMetaModel("javaMM", strategy));
	}
	
	@Override
	protected void tearDown() throws Exception {
		ec = null;
		strategy = null;
		super.tearDown();
	}
	
    public final void testLowerCase() {
        final Type mt = ec.getTypeForName(JavaBeansMetaType.class.getName().replaceAll("\\.", "::"));
        assertNotNull(mt);

        final Property prop = mt.getProperty("myProp");
        assertNotNull(prop);
    }

    public final void testFinalStaticField() {
        final Type mt = ec.getTypeForName(MyMetaTypeInterface.class.getName().replaceAll("\\.", "::"));
        assertNotNull(mt);

        final StaticProperty prop = mt.getStaticProperty("FOO");
        assertEquals("f",prop.get());
    }
    
    public final void testFinalStaticField2() {
        final ExpressionFacade ef = new ExpressionFacade(ec);
        String typeName = MyMetaTypeInterface.class.getName().replaceAll("\\.", "::");
        String expr = "switch(x) { case "+typeName+"::FOO : true case "+typeName+"::BAR : false default : null }";
        assertEquals(true, ef.evaluate(expr, Collections.singletonMap("x", "f")));
        assertEquals(false, ef.evaluate(expr, Collections.singletonMap("x", "b")));
        assertNull(ef.evaluate(expr, Collections.singletonMap("x", "x")));
    }

    public void testGetterAndSetterForProperty() {
    	Type javaBeansMetaType = ec.getTypeForName(JavaBeansMetaType.class.getName().replaceAll("\\.", "::"));
    	Type string = ec.getTypeForName(String.class.getName().replaceAll("\\.", "::"));
    	assertNotNull(string);
    	assertNotNull(javaBeansMetaType.getOperation("getMyProp", null));
    	assertNotNull(javaBeansMetaType.getOperation("setMyProp", new Type[]{string}));
    }
}