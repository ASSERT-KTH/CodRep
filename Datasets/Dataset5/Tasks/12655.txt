package org.eclipse.xtend.backend.testhelpers;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.helpers;

import java.util.Arrays;
import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.NamedFunction;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public abstract class NamedFunctionFactory implements Function {
    private final String _name;
    private final List<BackendType> _parameterTypes;
    private final boolean _cached;
    
    public NamedFunctionFactory (String name, BackendType... paramTypes) {
        this (name, false, paramTypes);
    }
        
    public NamedFunction create () {
        return new NamedFunction (_name, this);
    }
    
    public NamedFunctionFactory (String name, boolean cached, BackendType... paramTypes) {
        _name = name;
        _cached = cached;
        _parameterTypes = Arrays.asList (paramTypes);
    }

    public ExpressionBase getGuard () {
        return null;
    }

    public List<? extends BackendType> getParameterTypes () {
        return _parameterTypes;
    }

    public boolean isCached () {
        return _cached;
    }
}