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

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;
import org.eclipse.xtend.backend.types.builtin.CollectionType;


/**
 * This class deals with the case where the middle end can not decide statically whether
 *  a property is to be resolved on a single object or on a collection
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class PropertyOnWhateverExpression extends ExpressionBase {
    private final ExpressionBase _inner;
    private final String _propertyName;

    public PropertyOnWhateverExpression (ExpressionBase inner, String propertyName, SourcePos sourcePos) {
        super (sourcePos);
        
        _inner = inner;
        _propertyName = propertyName;
    }

    @Override
    public Object evaluateInternal(ExecutionContext ctx) {
        final Object o = _inner.evaluate(ctx);
        if (o == null) {
            ctx.logNullDeRef (getPos());
            return null;
        }

        final BackendType t = ctx.getTypesystem().findType (o);
        
        if (CollectionType.INSTANCE.isAssignableFrom(t)) {
            if (isProperty (t, _propertyName))
                return t.getProperty (ctx, o, _propertyName);
            
            final Collection<Object> result = (o instanceof List) ? new ArrayList<Object> () : new HashSet<Object> ();

            for (Object obj: (Collection<?>) o)
                result.add (ctx.getTypesystem().findType(obj).getProperty(ctx, obj, _propertyName));

            return result;
        }
        else
            return t.getProperty (ctx, o, _propertyName);
    }

    private boolean isProperty (BackendType t, String propName) {
        return t.getProperties().containsKey (propName);
    }
}