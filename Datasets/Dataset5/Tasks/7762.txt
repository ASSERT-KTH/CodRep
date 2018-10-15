return BackendFacade.createExecutionContext (new FunctionDefContextFactory (ts).create(), ts, true);

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.helpers;

import org.eclipse.xtend.backend.BackendFacade;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;
import org.eclipse.xtend.backend.expr.LiteralExpression;
import org.eclipse.xtend.backend.functions.FunctionDefContextFactory;
import org.eclipse.xtend.backend.types.CompositeTypesystem;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class BackendTestHelper {
    public static final SourcePos SOURCE_POS = createSourcePos();
    
    /**
     * This method returns an ExecutionContext that is basically empty - no registered functions, and
     *  only the JavaBeansTypeSystem. It is useful for simple tests.
     */
    public static ExecutionContext createEmptyExecutionContext () {
        final BackendTypesystem ts = new CompositeTypesystem ();
        return BackendFacade.createExecutionContext (new FunctionDefContextFactory (ts).create(), ts);
    }

    public static ExpressionBase createLiteral (Object literal) {
        return new LiteralExpression (literal, SOURCE_POS);
    }
    
    public static SourcePos createSourcePos () {
        return new SourcePos ("<no file>", "<no callable>", 0);
    }
}