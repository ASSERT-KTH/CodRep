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

import java.util.List;

import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class SequenceExpression extends ExpressionBase {
    private final List<ExpressionBase> _inner;

    public SequenceExpression (List<ExpressionBase> inner, SourcePos sourcePos) {
        super (sourcePos);
        _inner = inner;
    }
    
    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        Object result = null;
        
        for (ExpressionBase e: _inner)
            result = e.evaluate(ctx);
        
        return result;
    }
}