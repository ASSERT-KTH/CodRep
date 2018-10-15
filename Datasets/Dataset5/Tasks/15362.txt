ctx.getResourceManager().setFileEncoding (fileEncoding);

/*
Copyright (c) 2008, 2009 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.middleend.xtend;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.xtend.parser.ParseFacade;
import org.eclipse.xtend.backend.BackendFacade;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.FunctionDefContext;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.backend.functions.FunctionDefContextInternal;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.middleend.LanguageContributor;
import org.eclipse.xtend.middleend.MiddleEnd;
import org.eclipse.xtend.middleend.MiddleEndFactory;
import org.eclipse.xtend.middleend.xtend.internal.OldExpressionConverter;
import org.eclipse.xtend.middleend.xtend.internal.OldHelper;
import org.eclipse.xtend.middleend.xtend.internal.TypeToBackendType;
import org.eclipse.xtend.middleend.xtend.internal.xtendlib.XtendGlobalVarOperations;
import org.eclipse.xtend.middleend.xtend.internal.xtendlib.XtendLibContributor;
import org.eclipse.xtend.middleend.xtend.plugin.OldCheckRegistryFactory;
import org.eclipse.xtend.middleend.xtend.plugin.OldXtendRegistryFactory;
import org.eclipse.xtend.typesystem.MetaModel;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public final class XtendBackendFacade {
    private final String _xtendFile;
    private final MiddleEnd _middleEnd;
    private final Collection<MetaModel> _mms;
    
    /**
     * This method invokes a "stand alone" expression that knows nothing about any functions defined in files. It is useful for
     *  *very* simple use cases, and for testing purposes. <br>
     *  
     * Both mms and localVars may be null.
     */
    public static Object evaluateExpression (String expression, Collection<MetaModel> mms, Map<String, Object> localVars) {
        return evaluateExpression (expression, mms, localVars, null);
    }
        
    public static Object evaluateExpression (String expression, Collection<MetaModel> mms, Map<String, Object> localVars, Map<String, Object> globalVars) {
        return evaluateExpression (expression, null, null, mms, localVars, globalVars, null);
    }

    /**
     * This method invokes an expression that may call functions from an Xtend file.<br>
     * 
     * The fileEncoding may be null, in which case the platform's default encoding is used. Both mms and localVars may be null.
     */
    public static Object evaluateExpression (String expression, String initialXtendFileName, String fileEncoding, Collection<MetaModel> mms, Map<String, Object> localVars) {
        return evaluateExpression (expression, initialXtendFileName, fileEncoding, mms, localVars, null, null);
    }
        
    public static Object evaluateExpression (String expression, String initialXtendFileName, String fileEncoding, Collection<MetaModel> mms, Map<String, Object> localVars, Map<String, Object> globalVars, List<String> adviceResources) {
        return createForFile (initialXtendFileName, fileEncoding, mms).evaluateExpression (expression, localVars, globalVars, adviceResources);
    }
        
    public Object evaluateExpression (String expression, Map<String, Object> localVars) {
        return evaluateExpression (expression, localVars, null, null);
    }
    
    public Object evaluateExpression (String expression, Map<String, Object> localVars, Map<String, Object> globalVars, List<String> adviceResources) {
        if (localVars == null)
            localVars = new HashMap<String, Object> ();
        if (globalVars == null)
            globalVars = new HashMap<String, Object> ();
        if (adviceResources == null)
            adviceResources = new ArrayList<String> ();
        
        for (String a: adviceResources)
            _middleEnd.applyAdvice (a);

        final Expression oldAst = ParseFacade.expression (expression);
        
        ExecutionContextImpl ctx = new ExecutionContextImpl ();
        for (MetaModel mm: _mms)
            ctx.registerMetaModel (mm);
        for (String varName: localVars.keySet())
            ctx = (ExecutionContextImpl) ctx.cloneWithVariable (new Variable (varName, ctx.getType (localVars.get (varName))));
            
        final TypeToBackendType typeConverter = new TypeToBackendType (_middleEnd.getTypesystem(), ctx);
        final ExpressionBase newAst = new OldExpressionConverter (ctx, typeConverter, "<no file>").convert (oldAst);

        _middleEnd.getExecutionContext().setFunctionDefContext (createFdc ());
        //TODO configure isLogStacktrace
        _middleEnd.getExecutionContext().getLocalVarContext().getLocalVars().putAll (localVars);
        _middleEnd.getExecutionContext().getContributionStateContext().storeState (XtendGlobalVarOperations.GLOBAL_VAR_VALUES_KEY, globalVars);

        return newAst.evaluate (_middleEnd.getExecutionContext());
    }

    
    private FunctionDefContext createFdc () {
        if (_xtendFile != null) 
            return _middleEnd.getFunctions (_xtendFile);

        final FunctionDefContextInternal result = _middleEnd.createEmptyFdc();
        
        for (NamedFunction f: new XtendLibContributor (_middleEnd).getContributedFunctions())
            result.register (f, false);
        return result;
    }
    
    
    /**
     * This function invokes a single Xtend function, returning the result. The fileEncoding may be null, in which case the platform's default file
     *  encoding is used.
     */
    public static Object invokeXtendFunction (String xtendFileName, String fileEncoding, Collection<MetaModel> mms, QualifiedName functionName, Object... parameters) {
        return createForFile (xtendFileName, fileEncoding, mms).invokeXtendFunction (functionName, parameters);
    }
        
    public Object invokeXtendFunction (QualifiedName functionName, Object... parameters) {
        final FunctionDefContext fdc = _middleEnd.getFunctions (_xtendFile);
        final ExecutionContext ctx = BackendFacade.createExecutionContext (fdc, _middleEnd.getTypesystem(), true); //TODO configure isLogStacktrace
        return fdc.invoke (ctx, functionName, Arrays.asList (parameters));
    }
    
    
    public static XtendBackendFacade createForFile (String xtendFileName, String fileEncoding, Collection<MetaModel> mms) {
        return new XtendBackendFacade (xtendFileName, fileEncoding, mms);
    }

    private Map<Class<?>, Object> getSpecificParameters (String fileEncoding, Collection<MetaModel> mms) {
        fileEncoding = OldHelper.normalizedFileEncoding (fileEncoding);

        final ExecutionContextImpl ctx = new ExecutionContextImpl ();
        ctx.setFileEncoding (fileEncoding);
        for (MetaModel mm: mms)
            ctx.registerMetaModel (mm);
        
        final Map<Class<?>, Object> result = new HashMap<Class<?>, Object> ();
        result.put (OldXtendRegistryFactory.class, ctx);
        result.put (OldCheckRegistryFactory.class, ctx);
        return result;
    }
    
    
    private XtendBackendFacade (String xtendFileName, String fileEncoding, Collection<MetaModel> mms) {
        if (mms == null)
            mms = new ArrayList<MetaModel> ();
        
        _xtendFile = OldHelper.normalizeXtendResourceName (xtendFileName);
        _mms = mms;
        if (MiddleEndFactory.canCreateFromExtentions()) {
        	_middleEnd = MiddleEndFactory.createFromExtensions (OldHelper.guessTypesystem (mms), getSpecificParameters (fileEncoding, mms));
        } else {
        	_middleEnd = MiddleEndFactory.create (OldHelper.guessTypesystem (mms), LanguageContributor.INSTANCE.getFreshMiddleEnds (getSpecificParameters (fileEncoding, mms)));
        }
    }

    public FunctionDefContext getFunctionDefContext () {
        return _middleEnd.getFunctions (_xtendFile);
    }
}

