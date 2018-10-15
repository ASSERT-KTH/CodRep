public Map<String, ? extends Property> getProperties (ExecutionContext ctx) {

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
import java.util.Collections;
import java.util.Map;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.common.Property;
import org.eclipse.xtend.backend.common.StaticProperty;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class ObjectType implements BackendType {
    private ObjectType() {}
    
    public static ObjectType INSTANCE = new ObjectType();
    
    public boolean isAssignableFrom (BackendType other) {
        return true;
    }

    public Object create () {
        throw new UnsupportedOperationException ("ObjectType can not be instantiated");
    }

    public Collection<? extends NamedFunction> getBuiltinOperations () {
        return Collections.emptyList();
    }

    public String getName () {
        return "Object";
    }
    
    public String getUniqueRepresentation () {
        return "{builtin}Object";
    }

    public Map<String, ? extends Property> getProperties () {
        return Collections.emptyMap();
    }

    public Object getProperty (ExecutionContext ctx, Object o, String name) {
        throw new IllegalArgumentException ("ObjectType has no properties");
    }

    public Map<String, ? extends StaticProperty> getStaticProperties () {
        throw new IllegalArgumentException ("ObjectType has no static properties");
    }

    public Collection<? extends BackendType> getSuperTypes () {
        return Collections.emptyList();
    }

    public void setProperty (ExecutionContext ctx, Object o, String name, Object value) {
        throw new IllegalArgumentException ("ObjectType has no properties");
    }
}