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
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class LocalVarEvalExpression extends ExpressionBase {
    private final String _localVarName;

    public LocalVarEvalExpression (String localVarName, SourcePos sourcePos) {
        super(sourcePos);
        _localVarName = localVarName;
    }
    
    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        //expects a static check to have been performed that a local variable of this name exists
        return ctx.getLocalVarContext().getLocalVars().get (_localVarName);
    }
}