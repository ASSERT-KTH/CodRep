import org.eclipse.xtend.backend.types.java.internal.GlobalJavaBeansTypesystem;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.types;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.Property;
import org.eclipse.xtend.backend.common.StaticProperty;
import org.eclipse.xtend.backend.types.builtin.BooleanType;
import org.eclipse.xtend.backend.types.builtin.CollectionType;
import org.eclipse.xtend.backend.types.builtin.DoubleType;
import org.eclipse.xtend.backend.types.builtin.FunctionType;
import org.eclipse.xtend.backend.types.builtin.ListType;
import org.eclipse.xtend.backend.types.builtin.LongType;
import org.eclipse.xtend.backend.types.builtin.MapType;
import org.eclipse.xtend.backend.types.builtin.ObjectType;
import org.eclipse.xtend.backend.types.builtin.PropertyType;
import org.eclipse.xtend.backend.types.builtin.SetType;
import org.eclipse.xtend.backend.types.builtin.StaticPropertyType;
import org.eclipse.xtend.backend.types.builtin.StringType;
import org.eclipse.xtend.backend.types.builtin.TypeType;
import org.eclipse.xtend.backend.types.builtin.VoidType;
import org.eclipse.xtend.backend.types.java.GlobalJavaBeansTypesystem;
import org.eclipse.xtend.backend.util.Cache;


/**
 * This is the "normal" implementation of a backend type system - it can recursively
 *  contain other type system implementations, and it contributes the built-in types.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class CompositeTypesystem implements BackendTypesystem {
    private BackendTypesystem _rootTypesystem = this;
    private final List<BackendTypesystem> _inner = new ArrayList<BackendTypesystem>();
    
    private final BackendTypesystem _javaBeansTypesystem = new  GlobalJavaBeansTypesystem ();
    {
        _javaBeansTypesystem.setRootTypesystem (_rootTypesystem);
    }
    
    
    private final Cache<Class<?>, BackendType> _cache = new Cache<Class<?>, BackendType>() {
        @Override
        protected BackendType create (Class<?> key) {
            final BackendType builtin = findSimpleBuiltinType (key);
            if (builtin != null)
                return builtin;
            
            for (BackendTypesystem ts : _inner) {
                final BackendType result = ts.findType(key);
                if (result != null)
                    return result;
            }
            
            final BackendType jbResult = _javaBeansTypesystem.findType(key);
            if (jbResult != null)
                return jbResult;
            
            return ObjectType.INSTANCE;
        }
    };

    //TODO remove this - add "asBackendType" to frontend type instead
    public Collection<BackendTypesystem> getInner () {
        final Collection<BackendTypesystem> result = new ArrayList<BackendTypesystem> (_inner);
        result.add (_javaBeansTypesystem);
        return result;
    }
    
    public void register (BackendTypesystem ts) {
        _inner.add(ts);
        ts.setRootTypesystem (getRootTypesystem());
    }

    public BackendType findType (Object o) {
        if (o == null)
            return VoidType.INSTANCE;

        return findType (o.getClass());
    }

    public BackendType findType (Class<?> cls) {
        return _cache.get (cls);
    }

    public BackendTypesystem getRootTypesystem () {
        return _rootTypesystem;
    }

    public void setRootTypesystem (BackendTypesystem ts) {
        _rootTypesystem = ts;
        for (BackendTypesystem child : _inner)
            child.setRootTypesystem(ts);
        
        _javaBeansTypesystem.setRootTypesystem (ts);
    }
        
    private BackendType findSimpleBuiltinType (Class<?> cls) {
        if (cls == null)
            return ObjectType.INSTANCE; // convenience handling e.g. for interface types whose Java supertype is 'null' 
        
        if (List.class.isAssignableFrom (cls))
            return ListType.INSTANCE;
        if (Set.class.isAssignableFrom(cls))
            return SetType.INSTANCE;
        if (Collection.class.isAssignableFrom(cls))
            return CollectionType.INSTANCE;
        
        if (Map.class.isAssignableFrom(cls))
            return MapType.INSTANCE;
        
        if (CharSequence.class.isAssignableFrom(cls))
            return StringType.INSTANCE;
        
        if (cls == Boolean.class || cls == Boolean.TYPE)
            return BooleanType.INSTANCE;
        
        if (cls == Long.class || cls == Long.TYPE)
            return LongType.INSTANCE;
        if (cls == Double.class || cls == Double.TYPE)
            return DoubleType.INSTANCE;

        if (Function.class.isAssignableFrom(cls))
            return FunctionType.INSTANCE;
        
        if (cls == Void.TYPE)
            return VoidType.INSTANCE;
        
        if (BackendType.class.isAssignableFrom(cls))
            return TypeType.INSTANCE;
        if (Property.class.isAssignableFrom(cls))
            return PropertyType.INSTANCE;
        if (StaticProperty.class.isAssignableFrom(cls))
            return StaticPropertyType.INSTANCE;

        return null;
    }
}

