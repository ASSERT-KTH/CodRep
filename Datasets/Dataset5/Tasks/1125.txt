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

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;
import org.eclipse.xtend.backend.functions.Closure;


/**
 * This expression creates an initialized closure. A closure needs to be initialized
 *  at runtime because it contains a snapshot of the local variables that are visible
 *  during its creation
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class InitClosureExpression extends ExpressionBase {
    private final List<String> _paramNames;
    private final List<? extends BackendType> _paramTypes;
    private final ExpressionBase _def;

    public InitClosureExpression (List<String> paramNames, List<? extends BackendType> paramTypes, ExpressionBase def, SourcePos sourcePos) {
        super (sourcePos);
        
        _paramNames = paramNames;
        _paramTypes = paramTypes;
        _def = def;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        return new Closure (ctx.getLocalVarContext(), ctx.getFunctionDefContext(), _paramNames, _paramTypes, _def);
    }
}