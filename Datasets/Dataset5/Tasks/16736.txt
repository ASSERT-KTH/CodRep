public Object proceedWithParams (List<?> localParams) {

/*
Copyright (c) 2008 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
*/
package org.eclipse.xtend.backend.aop;

import java.util.List;

import org.eclipse.xtend.backend.aop.internal.AdviceScopeCounter;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.backend.util.ObjectWrapper;
import org.eclipse.xtend.backend.util.Triplet;


/**
 * This class represents a function with all applicable Advice.<br>
 * 
 * It could formally be treated as a function, but it is a conscious design decision
 *  not to do that. The rationale behind that decision is that advice is bound to a
 *  name or context (via its PointCut) whereas a function is not. In other words, if
 *  a function is passed around in a program, the applicable advice can vary - and
 *  for that reason, advice is only applied "just in time", based on the then current
 *  name and context. 
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public final class AdvisedFunction {
    private final Function _function;
    private final List<AroundAdvice> _advice;
    private final int _firstCacheableIndex;
    private final AdviceScopeCounter _scopeCounter;
    
    private final ThisJoinPointStaticPart _thisJoinPointStaticPart;

    
    public AdvisedFunction (QualifiedName functionName, Function function, List<AroundAdvice> advice, AdviceScopeCounter scopeCounter) {
        _function = function;
        _advice = advice;
        _scopeCounter = scopeCounter;

        _thisJoinPointStaticPart = new ThisJoinPointStaticPart (functionName, _function);
        
        if (function.isCached()) {
            int firstCacheableIndex = advice.size();
            while (firstCacheableIndex > 0 && advice.get (firstCacheableIndex - 1).isCacheable())
                firstCacheableIndex--;
            
            _firstCacheableIndex = firstCacheableIndex;
        }
        else
            _firstCacheableIndex = advice.size();
    }

    public Object evaluate (ExecutionContext ctx, List<?> params) {
        // the evaluation of the advice is performed in three stages:
        //  1. all advice that is "outside" the outermost non-cacheable advice
        //       is always actually evaluated
        //  2. advice that is cacheable but not yet cached is evaluated and cached 
        //       (iff the function is cached)
        //  3. once cached advice is encountered, the evaluation is short-circuited
        //       and the result from the cache is returned

        return proceedInternal (ctx, 0, params);
    }
    
    private Object proceedInternal (final ExecutionContext ctx, final int indNextAdvice, final List<?> params) {
        if (indNextAdvice >= _advice.size())
            return ctx.getFunctionInvoker().invoke (ctx, _function, params);

        if (indNextAdvice >= _firstCacheableIndex) {
            final ObjectWrapper ow = ctx.getAdviceContext().getResultCache().get (new Triplet<Function, AroundAdvice, List<?>> (_function, _advice.get (indNextAdvice), params));
            if (ow != null)
                return ow._content;
        }

        final ThisJoinPoint thisJoinPoint = new ThisJoinPoint (ctx.getStacktrace(), params) {
            @Override
            public Object proceed (List<?> localParams) {
                return proceedInternal (ctx, indNextAdvice+1, localParams);
            }
        };

        final AroundAdvice advice = _advice.get (indNextAdvice);
        final Object result = advice.evaluate (ctx, _scopeCounter, thisJoinPoint, _thisJoinPointStaticPart); 
        
        if (indNextAdvice >= _firstCacheableIndex) {
            final Triplet<Function, AroundAdvice, List<?>> key = new Triplet<Function, AroundAdvice, List<?>> (_function, _advice.get (indNextAdvice), params);
            ctx.getAdviceContext().getResultCache().put (key, new ObjectWrapper (result));
        }
        
        return result;
    }
}




