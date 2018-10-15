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
 * A "global variable" is a constant that is bound outside the execution of the program. Its
 *  purpose is to e.g. make configuration properties available inside the program.
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class GlobalVarExpression extends ExpressionBase {
    private final String _varName;

    public GlobalVarExpression (String varName, SourcePos sourcePos) {
        super(sourcePos);
        _varName = varName;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        return ctx.getGlobalVarContext().getGlobalVars().get (_varName);
    }
}