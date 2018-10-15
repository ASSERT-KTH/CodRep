super ("String", "{builtin}String");

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types.builtin;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.types.AbstractType;
import org.eclipse.xtend.backend.util.ReflectionHelper;


/**
 * The canonical, internal representation of a string object is "anything that implements CharSequence", i.e.
 *  a function that accepts a parameter of type string must accept any CharSequence. This is done to
 *  enable internal optimizations like lazy concatenation and streaming.<p>
 *  
 * This has the consequence that functions may need to convert a given CharSequence to whatever more specific
 *  string representation they need internally.
 *  
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class StringType extends AbstractType {
    public static final StringType INSTANCE = new StringType();
    
    private StringType () {
        super ("String");
        
        register (new BuiltinProperty (this, this, "length", ReflectionHelper.getKnownMethod (CharSequence.class, "length"), null));
    }

    @Override
    public boolean isAssignableFrom (BackendType other) {
        return other == this || other == VoidType.INSTANCE;
    }
    
    @Override
    public Object create () {
        return "";
    }
}