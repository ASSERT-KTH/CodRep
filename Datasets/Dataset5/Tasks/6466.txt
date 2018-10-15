super ("StaticProperty", "{builtin}StaticProperty");

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
import org.eclipse.xtend.backend.common.Property;
import org.eclipse.xtend.backend.types.AbstractType;
import org.eclipse.xtend.backend.util.ReflectionHelper;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class StaticPropertyType extends AbstractType {
    public static final StaticPropertyType INSTANCE = new StaticPropertyType ();
    
    private StaticPropertyType () {
        super ("Property");

        register (new BuiltinProperty (this, StringType.INSTANCE, "name", ReflectionHelper.getKnownMethod(Property.class, "getName"), null));
        register (new BuiltinProperty (this, TypeType.INSTANCE, "returnType", ReflectionHelper.getKnownMethod(Property.class, "getType"), null));
        register (new BuiltinProperty (this, TypeType.INSTANCE, "owner", ReflectionHelper.getKnownMethod(Property.class, "getOwner"), null));
    }

    @Override
    public boolean isAssignableFrom (BackendType other) {
        return other == this || other == VoidType.INSTANCE;
    }
}


