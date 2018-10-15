return org.eclipse.xtend.backend.types.emf.EObjectType.INSTANCE;

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.middleend.xtend.internal;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.List;

import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EDataType;
import org.eclipse.emf.ecore.EEnum;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.type.baseimpl.types.BooleanTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.CollectionTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.IntegerTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.ListTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.ObjectTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.OperationTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.PropertyTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.RealTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.SetTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.StaticPropertyTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.StringTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.TypeTypeImpl;
import org.eclipse.internal.xtend.type.impl.java.JavaTypeImpl;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.BackendTypesystem;
import org.eclipse.xtend.backend.types.CompositeTypesystem;
import org.eclipse.xtend.backend.types.builtin.BooleanType;
import org.eclipse.xtend.backend.types.builtin.CollectionType;
import org.eclipse.xtend.backend.types.builtin.DoubleType;
import org.eclipse.xtend.backend.types.builtin.FunctionType;
import org.eclipse.xtend.backend.types.builtin.ListType;
import org.eclipse.xtend.backend.types.builtin.LongType;
import org.eclipse.xtend.backend.types.builtin.ObjectType;
import org.eclipse.xtend.backend.types.builtin.PropertyType;
import org.eclipse.xtend.backend.types.builtin.SetType;
import org.eclipse.xtend.backend.types.builtin.StaticPropertyType;
import org.eclipse.xtend.backend.types.builtin.StringType;
import org.eclipse.xtend.backend.types.builtin.TypeType;
import org.eclipse.xtend.backend.types.builtin.VoidType;
import org.eclipse.xtend.backend.types.emf.EmfTypesystem;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.typesystem.Type;
import org.eclipse.xtend.typesystem.emf.EClassType;
import org.eclipse.xtend.typesystem.emf.EDataTypeType;
import org.eclipse.xtend.typesystem.emf.EEnumType;
import org.eclipse.xtend.typesystem.emf.EObjectType;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class TypeToBackendType {
    private final BackendTypesystem _backendTypes;
    private final EmfTypesystem _emfTypes;
    private final ExecutionContext _ctx;
    
    public TypeToBackendType (BackendTypesystem backendTypes, ExecutionContext ctx) {
        _backendTypes = backendTypes;
        _ctx = ctx;
        
        EmfTypesystem ets = null;
        for (BackendTypesystem bts: ((CompositeTypesystem) _backendTypes).getInner()) {
            if (bts instanceof EmfTypesystem)
                ets = (EmfTypesystem) bts;
        }
        
        _emfTypes = ets;
    }
    
    public BackendType convertToBackendType (Identifier typeName) {
        return convertToBackendType (Arrays.asList (typeName.getValue().split (SyntaxConstants.NS_DELIM)));
    }
    
    private BackendType convertToBackendType (List<String> segments) {
        final StringBuilder sb = new StringBuilder();
        boolean first = true;
        
        for (String s: segments) {
            if (!first) {
                sb.append (SyntaxConstants.NS_DELIM);
            }
            first = false;
            
            sb.append (s);
        }
        
        final Type t = _ctx.getTypeForName (sb.toString());
        return convertToBackendType(t);
    }

    public BackendType convertToBackendType (Class<?> cls) {
        return _backendTypes.findType (cls);
    }
    
    public BackendType convertToBackendType (Type t) {
        if (t instanceof EClassType)
            return convertEClassType (t);
        if (t instanceof EDataTypeType)
            return convertEDataTypeType (t);
        if (t instanceof EEnumType)
            return convertEEnumType (t);
        if (t instanceof EObjectType)
            return org.eclipse.xtend.backend.types.emf.internal.EObjectType.INSTANCE;
        
        if (t instanceof JavaTypeImpl)
            return convertJavaType (t);
        
        if (t instanceof BooleanTypeImpl)
            return BooleanType.INSTANCE;
        if (t instanceof ListTypeImpl)
            return ListType.INSTANCE;
        if (t instanceof SetTypeImpl)
            return SetType.INSTANCE;
        if (t instanceof CollectionTypeImpl)
            return CollectionType.INSTANCE;
        if (t instanceof IntegerTypeImpl)
            return LongType.INSTANCE;
        if (t instanceof ObjectTypeImpl)
            return ObjectType.INSTANCE;
        if (t instanceof OperationTypeImpl)
            return FunctionType.INSTANCE;
        if (t instanceof PropertyTypeImpl)
            return PropertyType.INSTANCE;
        if (t instanceof RealTypeImpl)
            return DoubleType.INSTANCE;
        if (t instanceof StaticPropertyTypeImpl)
            return StaticPropertyType.INSTANCE;
        if (t instanceof StringTypeImpl)
            return StringType.INSTANCE;
        if (t instanceof TypeTypeImpl)
            return TypeType.INSTANCE;
        if (t instanceof org.eclipse.internal.xtend.type.baseimpl.types.VoidType)
            return VoidType.INSTANCE;
        
        if (t != null)
            throw new IllegalArgumentException ("unable to convert type " + t.getClass().getName());
        else
            throw new IllegalArgumentException ("unable to convert type 'null'");
    }
    
    private BackendType convertJavaType (Type t) {
        final Class<?> cls = (Class<?>) getField (t, "clazz");
        return _backendTypes.findType(cls);
    }
    
    private BackendType convertEClassType (Type t) {
        final EClass eClass = (EClass) getField(t, "eClass");
        return _emfTypes.getTypeForEClassifier(eClass);
    }
    
    private BackendType convertEDataTypeType (Type t) {
        final EDataType eClass = (EDataType) getField(t, "dataType");
        return _emfTypes.getTypeForEClassifier(eClass);
    }
    
    private BackendType convertEEnumType (Type t) {
        final EEnum eClass = (EEnum) getField(t, "eEnum");
        return _emfTypes.getTypeForEClassifier(eClass);
    }
    
    private Object getField (Object o, String fieldName) {
        try {
            final Class<?> cls = o.getClass();
            final Field f = cls.getDeclaredField(fieldName);
            f.setAccessible(true);
            return f.get(o);
        } catch (Exception e) {
            throw new RuntimeException (e);
        }
    }
}