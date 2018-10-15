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
public final class PropertyOnCollectionExpression extends ExpressionBase {
    private final ExpressionBase _inner;
    private final String _propertyName;

    public PropertyOnCollectionExpression (ExpressionBase inner, String propertyName, SourcePos sourcePos) {
        super (sourcePos);
        
        _inner = inner;
        _propertyName = propertyName;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        final Collection<?> coll = (Collection<?>) _inner.evaluate(ctx);
        if (coll == null) {
            ctx.logNullDeRef (getPos());
            return null;
        }

        final Collection<Object> result = (coll instanceof List) ? new ArrayList<Object> () : new HashSet<Object> ();

        for (Object o: coll)
            result.add (ctx.getTypesystem().findType(o).getProperty(ctx, o, _propertyName));
        
        return result;
    }
}