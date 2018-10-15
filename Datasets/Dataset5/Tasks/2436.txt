fdc.register (myToString, true);

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.expr;

import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.SOURCE_POS;
import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.createEmptyExecutionContext;
import static org.eclipse.xtend.backend.testhelpers.BackendTestHelper.createLiteral;
import static org.junit.Assert.assertEquals;

import java.util.Arrays;

import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Helpers;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.functions.FunctionDefContextFactory;
import org.eclipse.xtend.backend.functions.FunctionDefContextInternal;
import org.eclipse.xtend.backend.testhelpers.NamedFunctionFactory;
import org.eclipse.xtend.backend.types.CompositeTypesystem;
import org.eclipse.xtend.backend.types.builtin.ObjectType;
import org.junit.Test;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class ConcatExpressionTest {
    @Test public void testLogic () {
        assertEquals ("", eval ());
        assertEquals ("abc", eval (createLiteral ("abc")));
        assertEquals ("abc", eval (createLiteral ("a"), createLiteral ("b"), createLiteral ("c")));
        assertEquals ("123", eval (createLiteral (1), createLiteral (2), createLiteral (3)));
        assertEquals ("123", eval (createLiteral (1), createLiteral ("2"), createLiteral (3)));
        assertEquals ("", eval (createLiteral (null)));
        assertEquals ("a", eval (createLiteral (null), createLiteral ("a")));
    }
    
    private Object eval (ExpressionBase... parts) {
        return new ConcatExpression (Arrays.asList(parts), SOURCE_POS).evaluate (createEmptyExecutionContext()).toString();
    }
    
    @Test public void testUsesToStringExtension () {
        final NamedFunction myToString = new NamedFunctionFactory (Helpers.TO_STRING_METHOD_NAME, ObjectType.INSTANCE) {
            public Object invoke (ExecutionContext ctx, Object[] params) {
                return "#" + params[0] + "!";
            }
        }.create(); 
        
        final FunctionDefContextInternal fdc = new FunctionDefContextFactory (new CompositeTypesystem ()).create();
        fdc.register (myToString);

        final ExpressionBase expr = new ConcatExpression (Arrays.asList (createLiteral("a"), createLiteral("b")), SOURCE_POS);
        
        final ExecutionContext ctx = createEmptyExecutionContext();
        assertEquals ("ab", expr.evaluate(ctx).toString());
        
        ctx.setFunctionDefContext(fdc);
        assertEquals ("#a!#b!", expr.evaluate(ctx).toString());
    }
}