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

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class SetPropertyExpression extends ExpressionBase {
    private final ExpressionBase _inner;
    private final String _propertyName;
    private final ExpressionBase _valueExpr;
    

    public SetPropertyExpression (ExpressionBase inner, String propertyName, ExpressionBase valueExpr, SourcePos sourcePos) {
        super(sourcePos);
        
        _inner = inner;
        _propertyName = propertyName;
        _valueExpr = valueExpr;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        final Object o = _inner.evaluate(ctx);
        if (o == null) {
            ctx.logNullDeRef (getPos());
            return null;
        }
        
        final BackendType t = ctx.getTypesystem().findType(o);
        final Object value = _valueExpr.evaluate(ctx);
        t.setProperty (ctx, o, _propertyName, value);
        
        return o;
    }
}