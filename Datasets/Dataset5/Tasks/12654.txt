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

import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class MutableLiteralExpression extends ExpressionBase {
    private Object _value;
    
    public MutableLiteralExpression (Object value) {
        super (BackendTestHelper.SOURCE_POS);
        
        _value = value;
    }

    public void setValue (Object value) {
        _value = value;
    }
    
    @Override
    protected Object evaluateInternal (ExecutionContext ctx) {
        return _value;
    }
}