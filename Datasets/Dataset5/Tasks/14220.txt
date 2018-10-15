package org.eclipse.xtend.backend.aop.internal;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
*/
package org.eclipse.xtend.backend.aop;

import org.eclipse.xtend.backend.common.Function;


/**
 * This class exposes all static information about the matched join point.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class ThisJoinPointStaticPart {
    private final String _functionName;
    private final Function _function;
    
    public ThisJoinPointStaticPart (String functionName, Function function) {
        _functionName = functionName;
        _function = function;
    }

    public String getFunctionName () {
        return _functionName;
    }

    public Function getFunction () {
        return _function;
    }
    
    @Override
    public String toString () {
        return _functionName + ": " + _function;
    }
}