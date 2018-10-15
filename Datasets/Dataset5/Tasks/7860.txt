package org.eclipse.xtend.backend.functions.internal;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.functions;

import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.FunctionDefContext;
import org.eclipse.xtend.backend.common.LocalVarContext;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class Closure implements Function {
    private final LocalVarContext _lvcAtDefinitionTime;
    private final FunctionDefContext _fdcAtDefinitionTime;

    private final List<String> _paramNames;
    private final List<? extends BackendType> _paramTypes;
    private final ExpressionBase _def;
    
    public Closure (LocalVarContext lvcAtDefinitionTime, FunctionDefContext fdcAtDefinitionTime, List<String> paramNames, List<? extends BackendType> paramTypes, ExpressionBase def) {
        //freeze local variables at definition time so they will be available in a different context at evaluation time
        _lvcAtDefinitionTime = new LocalVarContext();
        _lvcAtDefinitionTime.getLocalVars().putAll (lvcAtDefinitionTime.getLocalVars());

        _fdcAtDefinitionTime = fdcAtDefinitionTime;
        _paramNames = paramNames;
        _paramTypes = paramTypes;
        _def = def;
    }

    public String getName () {
        return "<Closure>";
    }
    
    
    public boolean isCached () {
        return false;
    }
    
    public List<? extends BackendType> getParameterTypes() {
        return _paramTypes;
    }

    public Object invoke (ExecutionContext ctx, Object[] params) {
        if (_fdcAtDefinitionTime == ctx.getFunctionDefContext())
            return invokeWithExistingFdc (ctx, params);
        else {
            final FunctionDefContext oldFdc = ctx.getFunctionDefContext ();
            try {
                ctx.setFunctionDefContext (_fdcAtDefinitionTime);
                return invokeWithExistingFdc(ctx, params);
            }
            finally {
                ctx.setFunctionDefContext (oldFdc);
            }
        }
    }
    
    private Object invokeWithExistingFdc (ExecutionContext ctx, Object... params) {
        // potential local variables that are hidden by parameters are not restored - but they will never be visible anyway
        final LocalVarContext lvc = _lvcAtDefinitionTime; 
        for (int i=0; i<_paramNames.size(); i++) {
            lvc.getLocalVars().put(_paramNames.get(i), params[i]);
        }
        
        final LocalVarContext oldLvc = ctx.getLocalVarContext();
        try {
            ctx.setLocalVarContext(lvc);
            return _def.evaluate(ctx);
        }
        finally {
            ctx.setLocalVarContext(oldLvc);
        }
    }

	public ExpressionBase getGuard() {
		return null;
	}
}