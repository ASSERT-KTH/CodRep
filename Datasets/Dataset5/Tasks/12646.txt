public final class JavaBeansProperty implements Property {

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

import java.beans.PropertyDescriptor;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.Property;
import org.eclipse.xtend.backend.functions.java.internal.JavaBuiltinConverter;
import org.eclipse.xtend.backend.util.ErrorHandler;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
final class JavaBeansProperty implements Property {
    private final PropertyDescriptor _pd;
    private final BackendType _owner;
    private final BackendType _type;
    private final JavaBuiltinConverter _converter;
    

    public JavaBeansProperty (PropertyDescriptor pd, BackendType owner, BackendType type, JavaBuiltinConverter converter) {
        _pd = pd;
        _owner = owner;
        _type = type;
        _converter = converter;
    }

    public String getName () {
        return _pd.getName();
    }

    public BackendType getOwner () {
        return _owner;
    }

    public BackendType getType () {
        return _type;
    }

    public Object get (ExecutionContext ctx, Object o) {
        try {
            if (_pd.getReadMethod() == null)
                throw new IllegalArgumentException ("no readable property " + _pd.getName() + " for type " + _owner.getName());
            return _converter.javaToBackend (_pd.getReadMethod().invoke (o));
        } catch (Exception e) {
            ErrorHandler.handle(e);
            return null; // to make the compiler happy - this is never executed
        }
    }
    
    public void set (ExecutionContext ctx, Object o, Object newValue) {
        try {
            if (_pd.getWriteMethod() == null)
                throw new IllegalArgumentException ("no writeable property " + _pd.getName() + " for type " + _owner.getName());
            _pd.getWriteMethod().invoke (o, _converter.backendToJava (newValue));
        } catch (Exception e) {
            ErrorHandler.handle (e);
        }
    }
}