package org.eclipse.xtend.middleend.old.internal.xtend;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.middleend.old.xtend;

import java.lang.reflect.Method;
import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.util.ErrorHandler;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
final class JavaExtensionFunction implements Function {
    private final Method _mtd;
    private final boolean _cached;
    private final List<? extends BackendType> _paramTypes;

    public JavaExtensionFunction (Method mtd, boolean cached, List<? extends BackendType> paramTypes) {
        _mtd = mtd;
        _cached = cached;
        _paramTypes = paramTypes;
    }
    
    public ExpressionBase getGuard () {
        return null;
    }

    public String getName () {
        return _mtd.getName();
    }

    public List<? extends BackendType> getParameterTypes () {
        return _paramTypes;
    }

    public Object invoke (ExecutionContext ctx, Object[] params) {
        try {
            return _mtd.invoke (null, params);
        } catch (Exception e) {
            ErrorHandler.handle(e);
            return null; // to make the compiler happy - this is never executed
        }
    }

    public boolean isCached () {
        return _cached;
    }
}