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
import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class CreateCachedExpression extends ExpressionBase {
    private final BackendType _t;
    private final List<ExpressionBase> _paramExpr;

    public CreateCachedExpression (BackendType t, List<ExpressionBase> paramExpr, SourcePos sourcePos) {
        super(sourcePos);
        
        _t = t;
        _paramExpr = paramExpr;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        final List<Object> params = new ArrayList<Object>();
        
        for (ExpressionBase e: _paramExpr)
            params.add (e.evaluate(ctx));
        
        return ctx.getCreationCache().createRaw (_t, params);
    }
}