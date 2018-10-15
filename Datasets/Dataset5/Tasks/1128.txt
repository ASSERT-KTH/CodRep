protected Object evaluateInternal(ExecutionContext ctx) {

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

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;

import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class InvocationOnWhateverExpression extends ExpressionBase {
    private final String _functionName;
    private final List<? extends ExpressionBase> _params;
    
    public InvocationOnWhateverExpression (String functionName, List<? extends ExpressionBase> params, SourcePos sourcePos) {
        super (sourcePos);
        
        _functionName = functionName;
        _params = params;
    }
    
    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        final List<Object> params = new ArrayList<Object> ();
        for (ExpressionBase expr: _params)
        	params.add (expr.evaluate(ctx));

        if (params.get (0) instanceof Collection<?>) {
            // check if this is a function on Collection itself
            if (ctx.getFunctionDefContext().hasMatch(ctx, _functionName, params))
                return ctx.getFunctionDefContext().invoke(ctx, _functionName, params);

            final Collection<?> coll = (Collection<?>) params.get (0);
            
            final Collection<Object> result = (coll instanceof List) ? new ArrayList<Object> () : new HashSet<Object> ();
            
            for (Object o: coll) {
                params.set (0, o);
                result.add (ctx.getFunctionDefContext().invoke (ctx, _functionName, params));
            }
            
            return result;

        }
        else 
            return ctx.getFunctionDefContext().invoke (ctx, _functionName, params);
    }
}