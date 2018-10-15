_properties.put (pd.getName(), new JavaBeansProperty (pd, this, ts.getRootTypesystem().findType (pd.getPropertyType())));

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

import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.beans.PropertyDescriptor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.common.Property;
import org.eclipse.xtend.backend.common.StaticProperty;
import org.eclipse.xtend.backend.functions.java.internal.JavaBuiltinConverterFactory;
import org.eclipse.xtend.backend.types.builtin.VoidType;
import org.eclipse.xtend.backend.util.ErrorHandler;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class JavaBeansType implements BackendType {
    private final Class<?> _javaClass;
    private final List<NamedFunction> _operations = new ArrayList<NamedFunction>();
    private final Map<String, JavaBeansProperty> _properties = new HashMap<String, JavaBeansProperty> ();
    private final Map<String, StaticProperty> _staticProperties = new HashMap<String, StaticProperty> ();
    
    private Collection<BackendType> _superTypes;
    
    public JavaBeansType (Class<?> cls) {
        _javaClass = cls;
    }

    /** 
     * the actual initialization is separated to deal with circular dependencies of operations and/or 
     *  properties referring to this very same type.
     */
    void init (BackendTypesystem ts) throws IntrospectionException {
        _superTypes = Collections.singleton (ts.getRootTypesystem().findType (_javaClass.getSuperclass()));

        for (Method mtd: _javaClass.getMethods()) {
            if (mtd.getDeclaringClass() == Object.class) // toString is added as a syslib function
                continue;
            
            final List<BackendType> paramTypes = new ArrayList<BackendType> ();
            
            paramTypes.add (this); // first parameter is the object on which the method is called
            for (Class<?> cls: mtd.getParameterTypes()) {
                paramTypes.add (ts.getRootTypesystem().findType(cls));
            }
            
            _operations.add (new NamedFunction (mtd.getName(), new JavaOperation (mtd, paramTypes, null)));
        }
        
        for (PropertyDescriptor pd: Introspector.getBeanInfo(_javaClass).getPropertyDescriptors()) {
            if (pd.getReadMethod().getDeclaringClass() == Object.class)
                continue;
            
            _properties.put (pd.getName(), new JavaBeansProperty (pd, this, ts.getRootTypesystem().findType (pd.getPropertyType()), JavaBuiltinConverterFactory.getConverter (pd.getPropertyType ())));
        }
        
        // static properties
        for (Field field: _javaClass.getFields()) {
            final int mod = field.getModifiers();
            if (Modifier.isPublic(mod) && Modifier.isStatic(mod) && Modifier.isFinal(mod)) {
                try {
                    _staticProperties.put (field.getName(), new JavaBeansStaticProperty (field, this, ts.getRootTypesystem().findType (field.getType()), JavaBuiltinConverterFactory.getConverter (field.getType())));
                } catch (Exception e) {
                    ErrorHandler.handle (e);
                }
            }
        }

        // Java 5 enums
        final Object[] enumValues = _javaClass.getEnumConstants();
        if (enumValues != null) {
            for (Object o : enumValues) {
                final Enum<?> curEnum = (Enum<?>) o;
                _staticProperties.put (curEnum.name(), new JavaBeansStaticProperty (this, ts.getRootTypesystem().findType(curEnum), curEnum.name(), curEnum));
            }
        }
    }
    
    public Object create () {
        try {
            return _javaClass.newInstance();
        } catch (Exception e) {
            ErrorHandler.handle (e);
            return null; // to make the compiler happy - this is never executed
        }
    }

    public List<NamedFunction> getBuiltinOperations () {
        return _operations;
    }

    public Object getProperty (ExecutionContext ctx, Object o, String name) {
        return findProperty(name).get (ctx, o);
    }

    private Property findProperty (String name) {
        final Property result = _properties.get (name);
        if (result == null)
            throw new IllegalArgumentException (" no property " + name + " for type " + getName());
        
        return result;
    }
    
    public void setProperty (ExecutionContext ctx, Object o, String name, Object value) {
        findProperty(name).set (ctx, o, value);
    }

    public boolean isAssignableFrom (BackendType other) {
        if (other == VoidType.INSTANCE)
            return true;
        
        if (! (other instanceof JavaBeansType))
            return false;
        
        final JavaBeansType jbt = (JavaBeansType) other;
        return _javaClass.isAssignableFrom(jbt._javaClass);
    }

    public String getName () {
        return _javaClass.getCanonicalName().replace(".", "::");
    }

    public Map<String, ? extends Property> getProperties () {
        return _properties;
    }

    public Map<String, ? extends StaticProperty> getStaticProperties () {
        return _staticProperties;
    }

    public Collection<BackendType> getSuperTypes () {
        return _superTypes;
    }
    
    @Override
    public String toString () {
        return "JavaBeansType[" + _javaClass.getName()  + "]";
    }
}

