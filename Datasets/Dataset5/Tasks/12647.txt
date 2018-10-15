public final class JavaBeansStaticProperty implements StaticProperty {

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types.java.internal;

import java.lang.reflect.Field;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.StaticProperty;
import org.eclipse.xtend.backend.functions.java.internal.JavaBuiltinConverter;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
final class JavaBeansStaticProperty implements StaticProperty {
    private final String _name;
    private final Object _value;
    private final BackendType _owner;
    private final BackendType _type;
    

    public JavaBeansStaticProperty (Field field, BackendType owner, BackendType type, JavaBuiltinConverter converter) throws IllegalArgumentException, IllegalAccessException {
        this (owner, type, field.getName(), converter.javaToBackend (field.get (null)));
    }
    
    public JavaBeansStaticProperty (BackendType owner, BackendType type, String name, Object value) {
        _name = name;
        _owner = owner;
        _type = type;
        _value = value;
    }
    
    
    public String getName () {
        return _name;
    }

    public BackendType getOwner () {
        return _owner;
    }

    public BackendType getType () {
        return _type;
    }

    public Object get () {
        return _value;
    }
}