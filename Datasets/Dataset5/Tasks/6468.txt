super ("Type", "{builtin}Type");

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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.FunctionDefContext;
import org.eclipse.xtend.backend.types.AbstractProperty;
import org.eclipse.xtend.backend.types.AbstractType;
import org.eclipse.xtend.backend.util.ReflectionHelper;


/**
 * This class represents the type of a type. It serves as an entry point for meta programming.
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class TypeType extends AbstractType {
    public static final TypeType INSTANCE = new TypeType ();
    
    private TypeType () {
        super ("Type");
        
        register (new BuiltinProperty (this, StringType.INSTANCE, "name", ReflectionHelper.getKnownMethod (BackendType.class, "getName"), null));
        register (new BuiltinProperty (this, ListType.INSTANCE, "superTypes", ReflectionHelper.getKnownMethod (BackendType.class, "getSuperTypes"), null));
        register (new BuiltinProperty (this, ListType.INSTANCE, "allProperties", ReflectionHelper.getKnownMethod (BackendType.class, "getProperties"), null));
        register (new BuiltinProperty (this, ListType.INSTANCE, "allStaticProperties", ReflectionHelper.getKnownMethod (BackendType.class, "getStaticProperties"), null));
        
        register (new AbstractProperty (this, ListType.INSTANCE, java.util.List.class, "allOperations", false) {
            @Override
            public Object getRaw (ExecutionContext ctx, Object o) {
                final BackendType t = (BackendType) o;
                final List<Object> result = new ArrayList<Object>();
                result.addAll (ctx.getFunctionDefContext().getByFirstParameterType(t));
                result.addAll (t.getBuiltinOperations());
                return result;
            } 
        });
        
        register ("getProperty", new Function () {
            final List<? extends BackendType> _paramTypes = Arrays.asList (TypeType.this, StringType.INSTANCE);
            
            public ExpressionBase getGuard () {
                return null;
            }

            public List<? extends BackendType> getParameterTypes () {
                return _paramTypes;
            }

            public Object invoke (ExecutionContext ctx, Object[] params) {
                final BackendType t = (BackendType) params[0];
                final String propname = (String) params[1];
                
                return t.getProperties().get(propname);
            }

            public boolean isCached () {
                return false;
            }

            public FunctionDefContext getFunctionDefContext () {
                return null;
            }

            public void setFunctionDefContext (FunctionDefContext fdc) {
                throw new UnsupportedOperationException ();
            }
        });
    }
}

