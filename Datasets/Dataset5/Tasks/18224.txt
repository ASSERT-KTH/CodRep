public void register (Collection<? extends NamedFunction> functions) {

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.functions.internal;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.functions.DuplicateAwareFunctionCollection;
import org.eclipse.xtend.backend.functions.DuplicateAwareNamedFunctionCollection;
import org.eclipse.xtend.backend.functions.FunctionDefContextInternal;
import org.eclipse.xtend.backend.util.Cache;
import org.eclipse.xtend.backend.util.DoubleKeyCache;
import org.eclipse.xtend.backend.util.ErrorHandler;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public final class FunctionDefContextImpl implements FunctionDefContextInternal {
	
	private final Cache<BackendType, Collection<NamedFunction>> _byFirstParameterType = new Cache<BackendType, Collection<NamedFunction>>() {
        @Override
        protected Collection<NamedFunction> create (BackendType key) {
            return new ArrayList<NamedFunction>();
        }
	};
	
    private final DoubleKeyCache<String, Integer, DuplicateAwareNamedFunctionCollection> _functions = new DoubleKeyCache<String, Integer, DuplicateAwareNamedFunctionCollection>() {
        @Override
        protected DuplicateAwareNamedFunctionCollection create(String key1, Integer key2) {
            return new DuplicateAwareNamedFunctionCollection ();
        }
    };
    
    private final DoubleKeyCache<String, List<BackendType>, Collection<Function>> _byParamTypes = new DoubleKeyCache<String, List<BackendType>, Collection<Function>>() {
    	
        @Override
        protected Collection<Function> create (String functionName, List<BackendType> paramTypes) {
            return new PolymorphicResolver(functionName).getBestFitCandidates (findCandidates (functionName, paramTypes)); // TODO go around this cache if there is a dynamically provided function 
        }
        
        private Collection<Function> findCandidates (String functionName, List<BackendType> paramTypes) {
            final int paramCount = paramTypes.size();
            final BackendType firstParamType = paramTypes.isEmpty() ? null : paramTypes.get(0);
            
            final DuplicateAwareFunctionCollection result = new DuplicateAwareFunctionCollection ();
            
            // get built-in operations of the typesystem
            if (firstParamType != null) {
                for (NamedFunction f: firstParamType.getBuiltinOperations())
                    if (functionName.equals (f.getName()) && matchesParamTypes(f.getFunction(), paramTypes))
                        result.register (f.getFunction());
            }
            
            // merge with registered functions
            for (NamedFunction f: _functions.get (functionName, paramCount).getFunctions())
                if (matchesParamTypes (f.getFunction(), paramTypes))
                    result.register (f.getFunction());
            
            return result.getFunctions();
        }
        
        private boolean matchesParamTypes (Function f, List<BackendType> paramTypes) {
            if (f.getParameterTypes().size() != paramTypes.size())
                return false;
            
            for (int i=0; i<f.getParameterTypes().size(); i++) {
                if (! f.getParameterTypes().get(i).isAssignableFrom(paramTypes.get(i)))
                    return false;
            }
            
            return true;
        }
    };

    public void register (Collection<NamedFunction> functions) {
        for (NamedFunction f: functions)
            register (f);
    }
    
    public void register (NamedFunction f) {
        final NamedFunction old = _functions.get (f.getName(), f.getFunction().getParameterTypes().size()).register (f);
        if (old != null && old.getFunction().getParameterTypes().size() > 0)
            _byFirstParameterType.get (old.getFunction().getParameterTypes().get (0)).remove (old);
        
        if (f.getFunction().getParameterTypes().size() > 0)
            _byFirstParameterType.get (f.getFunction().getParameterTypes().get(0)).add (f);
    }
    
    public Object invoke (ExecutionContext ctx, String functionName, List<? extends Object> params) {
    	final Collection<Function> candidates = findFunctionCandidates (ctx, functionName, params);
    	final Function f = new PolymorphicResolver(functionName).evaluateGuards(ctx, candidates);
    	return ctx.getFunctionInvoker().invoke (ctx, f, params);
    }

    /**
     * is public only for testing purposes
     */
    public Collection<Function> findFunctionCandidates (ExecutionContext ctx, String functionName, List<? extends Object> params) {
        final List<BackendType> paramTypes = new ArrayList<BackendType>();
        for (Object o: params)
            paramTypes.add (ctx.getTypesystem().findType(o));

        try {
            return _byParamTypes.get (functionName, paramTypes);
        } catch (RuntimeException e) {
            ErrorHandler.handle ("Failed to resolve function '" + functionName + "' for parameter types " + paramTypes + ".", e);
            return null; // to make the compiler happy - this is never executed
        }
    }
    
    public Collection<NamedFunction> getByFirstParameterType (BackendType firstParameterType) {
        if (firstParameterType.getBuiltinOperations().isEmpty())
            return _byFirstParameterType.get (firstParameterType);
        
        final List<NamedFunction> result = new ArrayList<NamedFunction> (_byFirstParameterType.get (firstParameterType));
        result.addAll (firstParameterType.getBuiltinOperations());
        return result;
    }

    public Function getMatch (ExecutionContext ctx, String name, List<BackendType> params) {
        final Collection<Function> candidates = findFunctionCandidates (ctx, name, params);
        if (candidates.isEmpty())
            return null;
        if (candidates.size() > 1)
            throw new IllegalArgumentException ("several matches for function '" + name + "' and parameter types " + params + ".");
        
        return candidates.iterator().next();
    }
    
    public boolean hasMatch (ExecutionContext ctx, String functionName, List<? extends Object> params) {
        return findFunctionCandidates (ctx, functionName, params).size() > 0;
    }
    
    @Override
    public String toString () {
        return "FunctionDefContextImpl [" + _functions.getMap().values() + "]";
    }
}




