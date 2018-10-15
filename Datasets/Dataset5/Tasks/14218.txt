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

import org.eclipse.xtend.backend.common.BackendType;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class AdviceParamType {
    private final BackendType _type;
    private final boolean _includingSubtypes;
    
    public AdviceParamType (BackendType type, boolean includingSubtypes) {
        _type = type;
        _includingSubtypes = includingSubtypes;
    }

    //TODO testen!
    
    public boolean matches (BackendType type) {
        if (_includingSubtypes)
            return _type.isAssignableFrom (type);
        else
            return _type.equals (type);
    }
}