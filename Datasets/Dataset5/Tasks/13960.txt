execCtx.getResourceManager().setFileEncoding("ISO-8859-1");

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xpand.internal.tests.evaluate;

import junit.framework.TestCase;

import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.xpand2.XpandExecutionContextImpl;
import org.eclipse.xpand2.XpandFacade;
import org.eclipse.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.xtend.type.impl.java.beans.JavaBeansStrategy;
import org.eclipse.xtend.typesystem.Type;

public class AopFeatureTest extends TestCase {
    private XpandExecutionContextImpl execCtx;

    private OutputStringImpl out;

    @Override
    protected void setUp() throws Exception {
        super.setUp();
        
        out = new OutputStringImpl ();
        
        execCtx = new XpandExecutionContextImpl(out, null);
        execCtx.registerMetaModel(new JavaMetaModel("JavaBeans", new JavaBeansStrategy()));

        // ADDED encoding
        execCtx.setFileEncoding("ISO-8859-1");
        execCtx.registerAdvices(prefix() + "Advices1");
    }

    public final void test_test1_Object() {
        final XpandDefinition def = execCtx.findDefinition(prefix() + "Adviced::test1", execCtx.getObjectType(), null);
        def.evaluate(execCtx,"foo");
        assertEquals("12", out.buff.toString());
    }

    public final void test_test2_Object() {
        final XpandDefinition def = execCtx.findDefinition(prefix() + "Adviced::test2", execCtx.getObjectType(), null);
        def.evaluate(execCtx, "foo");
        assertEquals("13", out.buff.toString());
    }

    public final void test_te2st_Object() {
        final XpandDefinition def = execCtx.findDefinition(prefix() + "Adviced::te2st", execCtx.getObjectType(), null);
        def.evaluate(execCtx,"foo");
        assertEquals("14", out.buff.toString());
    }

    public final void test_test1_String() {
        final XpandDefinition def = execCtx.findDefinition(prefix() + "Adviced::test1", execCtx.getStringType(), null);
        def.evaluate(execCtx,"foo");
        assertEquals("1258", out.buff.toString());
    }

    public final void test_test1_StringParam_String() {
        final XpandDefinition def = execCtx.findDefinition(prefix() + "Adviced::test1", execCtx.getStringType(),
                new Type[] { execCtx.getStringType() });
        def.evaluate(execCtx,"foo","bar");
        assertEquals("678", out.buff.toString());
    }

    public final void test_test1_StringParams_String() {
        final XpandDefinition def = execCtx.findDefinition(prefix() + "Adviced::test1", execCtx.getStringType(),
                new Type[] { execCtx.getStringType(), execCtx.getStringType() });
        def.evaluate(execCtx,"Foo","bar","baz");
        assertEquals("78", out.buff.toString());
    }
    
    public final void test_testParamNames_StringParam_String() {
    	XpandFacade xpandFacade = XpandFacade.create(execCtx);
    	xpandFacade.evaluate(prefix() + "Adviced::testParamNames", "foo","bar");
    	assertEquals("barbar", out.buff.toString());
    }

    private String prefix() {
        return getClass().getPackage().getName().replaceAll("\\.", SyntaxConstants.NS_DELIM) + SyntaxConstants.NS_DELIM;
    }
}