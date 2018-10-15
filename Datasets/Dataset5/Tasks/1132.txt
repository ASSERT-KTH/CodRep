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

import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;


/**
 * this is not delegated to syslib because of shortcut evaluation
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class OrExpression extends ExpressionBase {
    private final ExpressionBase _left, _right;

    public OrExpression (ExpressionBase left, ExpressionBase right, SourcePos sourcePos) {
        super(sourcePos);
        
        _left = left;
        _right = right;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        final Object left = _left.evaluate(ctx);
        if (left == null) {
            ctx.logNullDeRef (getPos());
            return null;
        }
        
        if (Boolean.TRUE.equals (left))
            return Boolean.TRUE;
            
        final Object right = _right.evaluate(ctx);
        if (right == null) {
            ctx.logNullDeRef (getPos());
            return null;
        }
        return right;
    }
}