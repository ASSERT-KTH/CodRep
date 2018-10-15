final ExecutionContext initCtx = BackendFacade.createExecutionContext (fdc, ts, true);

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

import static org.eclipse.xtend.backend.helpers.BackendTestHelper.SOURCE_POS;
import static org.eclipse.xtend.backend.helpers.BackendTestHelper.createEmptyExecutionContext;
import static org.junit.Assert.assertEquals;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.eclipse.xtend.backend.BackendFacade;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.functions.FunctionDefContextFactory;
import org.eclipse.xtend.backend.functions.FunctionDefContextInternal;
import org.eclipse.xtend.backend.types.CompositeTypesystem;
import org.eclipse.xtend.backend.types.builtin.StringType;
import org.junit.Test;


/**
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class InitClosureExpressionTest {
    
    /**
     * test that the newly initialized closure actually has the correct number and type of parameters, and correctly binds the values to the right
     *  local variables in its body.
     */
    @Test public void testParameterBinding () {
        final List<String> paramNames = Arrays.asList("a");
        final List<StringType> paramTypes = Arrays.asList(StringType.INSTANCE);
        final LocalVarEvalExpression body = new LocalVarEvalExpression ("a", SOURCE_POS);
        
        final Function closure = (Function) new InitClosureExpression (paramNames, paramTypes, body, SOURCE_POS).evaluate (createEmptyExecutionContext());
        assertEquals (1, closure.getParameterTypes().size());
        assertEquals (StringType.INSTANCE, closure.getParameterTypes().get(0));
        
        assertEquals ("xyz", closure.invoke(createEmptyExecutionContext(), new Object[] {"xyz"}));
        assertEquals ("abc", closure.invoke(createEmptyExecutionContext(), new Object[] {"abc"}));
    }
    
    
    /**
     * test that local variables that were in scope during the initialization of a closure are visible during its execution, even if that is in an
     *  entirely different scope.
     */
    @Test public void testLocalVariableBinding () {
        final ExecutionContext initContext = createEmptyExecutionContext();
        initContext.getLocalVarContext().getLocalVars().put ("a", "aValue");
        
        final LocalVarEvalExpression body = new LocalVarEvalExpression ("a", SOURCE_POS);
        
        final Function closure = (Function) new InitClosureExpression (new ArrayList<String>(), new ArrayList<BackendType>(), body, SOURCE_POS).evaluate (initContext);
        
        assertEquals ("aValue", closure.invoke (createEmptyExecutionContext(), new Object[] {}));
    }
    
    
    /**
     * test that functions visible during the initialization of a closure are callable in a different context where they are no longer in scope.
     */
    @Test public void testFdcPropagation () {
        final BackendTypesystem ts = new CompositeTypesystem ();
        
        final FunctionDefContextInternal fdc = new FunctionDefContextFactory (ts).create();
        fdc.register (new NamedFunction ("myFunction", new Function () {

            public ExpressionBase getGuard () {
                return null;
            }

            public List<? extends BackendType> getParameterTypes () {
                return new ArrayList<BackendType>();
            }

            public Object invoke (ExecutionContext ctx, Object[] params) {
                return "myResult";
            }

            public boolean isCached () {
                return false;
            }
            
        }));
        
        final ExecutionContext initCtx = BackendFacade.createExecutionContext (fdc, ts);
        final ExpressionBase body = new InvocationOnObjectExpression ("myFunction", new ArrayList<ExpressionBase> (), false, SOURCE_POS);
        final Function closure = (Function) new InitClosureExpression (new ArrayList<String>(), new ArrayList<BackendType>(), body, SOURCE_POS).evaluate (initCtx);
        
        assertEquals ("myResult", closure.invoke(createEmptyExecutionContext(), new Object[]{}));
    }
}





