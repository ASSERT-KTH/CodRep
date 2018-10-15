super ("Collection", "{builtin}Collection");

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

import java.util.Collection;

import org.eclipse.xtend.backend.types.AbstractType;
import org.eclipse.xtend.backend.util.ReflectionHelper;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class CollectionType extends AbstractType {
    public static final CollectionType INSTANCE = new CollectionType();

    private CollectionType() {
        super ("Collection"); 
    
        register (new BuiltinProperty (this, LongType.INSTANCE, "size", ReflectionHelper.getKnownMethod(Collection.class, "size"), null));
        register (new BuiltinProperty (this, BooleanType.INSTANCE, "isEmpty", ReflectionHelper.getKnownMethod(Collection.class, "isEmpty"), null));
    }
}
