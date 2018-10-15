return new SourceDefinedFunction (new QualifiedName (def.getFileName().replaceAll("/", SyntaxConstants.NS_DELIM), def.getName()), paramNames, paramTypes, convertStatementSequence (def.getBody(), def, referencedDefinitions), false, null);

/*
Copyright (c) 2008 Arno Haase, André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
    André Arnold
 */
package org.eclipse.xtend.middleend.xpand.internal;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.internal.xpand2.ast.Advice;
import org.eclipse.internal.xpand2.ast.Definition;
import org.eclipse.internal.xpand2.ast.ErrorStatement;
import org.eclipse.internal.xpand2.ast.ExpandStatement;
import org.eclipse.internal.xpand2.ast.ExpressionStatement;
import org.eclipse.internal.xpand2.ast.FileStatement;
import org.eclipse.internal.xpand2.ast.ForEachStatement;
import org.eclipse.internal.xpand2.ast.IfStatement;
import org.eclipse.internal.xpand2.ast.LetStatement;
import org.eclipse.internal.xpand2.ast.ProtectStatement;
import org.eclipse.internal.xpand2.ast.Statement;
import org.eclipse.internal.xpand2.ast.TextStatement;
import org.eclipse.internal.xpand2.model.XpandAdvice;
import org.eclipse.internal.xpand2.model.XpandDefinition;
import org.eclipse.internal.xpand2.type.IteratorType;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.xpand2.XpandExecutionContext;
import org.eclipse.xpand2.output.Outlet;
import org.eclipse.xtend.backend.aop.AroundAdvice;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.Function;
import org.eclipse.xtend.backend.common.NamedFunction;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.backend.common.SourcePos;
import org.eclipse.xtend.backend.common.SyntaxConstants;
import org.eclipse.xtend.backend.expr.ConcatExpression;
import org.eclipse.xtend.backend.expr.HidingLocalVarDefExpression;
import org.eclipse.xtend.backend.expr.IfExpression;
import org.eclipse.xtend.backend.expr.InitClosureExpression;
import org.eclipse.xtend.backend.expr.InvocationOnObjectExpression;
import org.eclipse.xtend.backend.expr.LiteralExpression;
import org.eclipse.xtend.backend.expr.LocalVarEvalExpression;
import org.eclipse.xtend.backend.expr.NewLocalVarDefExpression;
import org.eclipse.xtend.backend.expr.SequenceExpression;
import org.eclipse.xtend.backend.functions.SourceDefinedFunction;
import org.eclipse.xtend.backend.syslib.FileIoOperations;
import org.eclipse.xtend.backend.syslib.SysLibNames;
import org.eclipse.xtend.backend.types.builtin.ObjectType;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.TypeSystem;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.middleend.xpand.internal.xpandlib.XpandLibNames;
import org.eclipse.xtend.middleend.xpand.plugin.XpandDefinitionName;
import org.eclipse.xtend.middleend.xtend.internal.OldExpressionConverter;
import org.eclipse.xtend.middleend.xtend.internal.OldTypeAnalyzer;
import org.eclipse.xtend.middleend.xtend.internal.TypeToBackendType;
import org.eclipse.xtend.middleend.xtend.internal.xtendlib.XpandIsDeleteLine;
import org.eclipse.xtend.middleend.xtend.internal.xtendlib.XtendIterator;
import org.eclipse.xtend.middleend.xtend.internal.xtendlib.XtendLibNames;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Type;


/**
 * converts a single template
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 */
public final class OldDefinitionConverter {

    public static final List<String> ADVICE_LOCAL_VAR_NAMES = Arrays.asList (Advice.DEF_VAR_NAME, SyntaxConstants.THIS_JOINPOINT_STATICPART);
	
    private XpandExecutionContext _ctx;
    private final TypeToBackendType _typeConverter;
    
    private String _definitionName;
    
    private int _localVarCounter = 0;
    
    
    public OldDefinitionConverter (XpandExecutionContext ctx, TypeToBackendType typeConverter) {
        _ctx = ctx;
        _typeConverter = typeConverter;
    }
    
    
    public AroundAdvice create (Advice a, Set<XpandDefinitionName> referencedDefinitions) {
        final XpandExecutionContext oldCtx = _ctx;
        
        try {
            final OldExpressionConverter exprConv = new OldExpressionConverter (_ctx, _typeConverter, "<around>");

            _ctx = (XpandExecutionContext) _ctx.cloneWithoutVariables();
            
            final List<String> localAdviceVarNames = ADVICE_LOCAL_VAR_NAMES;
            final List<Type> localAdviceVarTypes = getAdviceLocalVarTypes (oldCtx);
            for (int i=0; i<localAdviceVarNames.size(); i++)
                _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (localAdviceVarNames.get(i), localAdviceVarTypes.get(i)));
            final List<DeclaredParameter> localVarNames = a.getParamsAsList();
            for (DeclaredParameter declaredParameter : localVarNames) {
				_ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (declaredParameter.getName().getValue(), declaredParameter.getType()));
			}
            
            final ExpressionBase body = convertStatementSequence (a.getBody(), a, referencedDefinitions);
            return exprConv.convertAdvice (body, a.getPointCut().getValue(), a.getType(), Arrays.asList (a.getParams()), a.isWildcardParams());
        }
        finally {
            _ctx = oldCtx;
        }
    }
    
    public NamedFunction createUnregistered (XpandDefinition def, Set<XpandDefinitionName> referencedDefinitions) {
        if (def instanceof Definition) {
            final String canonicalName = new XpandDefinitionName (def).getCanonicalDefinitionName();
            return new NamedFunction (new QualifiedName (canonicalName.replaceAll ("/", SyntaxConstants.NS_DELIM)), createNormalDefinition ((Definition) def, referencedDefinitions));
        }
        
        throw new IllegalArgumentException ("unsupported definition type " + def.getClass().getName());
    }

    
    private Function createNormalDefinition (Definition def, Set<XpandDefinitionName> referencedDefinitions) {
        final XpandExecutionContext oldCtx = _ctx;
        
        try {
            final List<String> paramNames = new ArrayList<String>();
            final List<BackendType> paramTypes = new ArrayList<BackendType>();
            
            final Type ft = _ctx.getTypeForName (def.getTargetType());
            _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (ExecutionContext.IMPLICIT_VARIABLE, ft));
            paramNames.add (SyntaxConstants.THIS);
            paramTypes.add (_typeConverter.convertToBackendType(ft));
            
            for (DeclaredParameter dp: def.getParams()) {
                final Type pt = _ctx.getTypeForName (dp.getType().getValue());
                _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (dp.getName().getValue(), pt));
                paramNames.add (dp.getName().getValue());
                paramTypes.add (_typeConverter.convertToBackendType (pt));
            }

            return new SourceDefinedFunction (new QualifiedName (def.getName()), paramNames, paramTypes, convertStatementSequence (def.getBody(), def, referencedDefinitions), false, null);
        }
        finally {
            _ctx = oldCtx;
        }
    }
    
    public ExpressionBase convertStatementSequence (Statement[] statements, SyntaxElement oldPos, Set<XpandDefinitionName> referencedDefinitions) {
        final List<ExpressionBase> parts = new ArrayList<ExpressionBase> ();

        for (Statement stmt: statements)
            parts.add (convertStatement (stmt, referencedDefinitions));

        if (parts.size() == 1)
            return parts.get (0);
        else
            return new ConcatExpression (parts, getSourcePos(oldPos));
    }

    
    public ExpressionBase convertStatement (Statement stmt, Set<XpandDefinitionName> referencedDefinitions) {
        if (stmt instanceof ErrorStatement)
            return convertErrorStatement((ErrorStatement) stmt);
        if (stmt instanceof ExpandStatement)
            return convertExpandStatement ((ExpandStatement) stmt, referencedDefinitions);
        if (stmt instanceof ExpressionStatement)
            return convertExpressionStatement ((ExpressionStatement) stmt);
        if (stmt instanceof FileStatement)
            return convertFileStatement ((FileStatement) stmt, referencedDefinitions);
        if (stmt instanceof ForEachStatement)
            return convertForEachStatement ((ForEachStatement) stmt, referencedDefinitions);
        if (stmt instanceof IfStatement)
            return convertIfStatement ((IfStatement) stmt, referencedDefinitions);
        if (stmt instanceof LetStatement)
            return convertLetStatement ((LetStatement) stmt, referencedDefinitions);
        if (stmt instanceof ProtectStatement)
            return convertProtectStatement ((ProtectStatement) stmt, referencedDefinitions);
        if (stmt instanceof TextStatement)
            return convertTextStatement ((TextStatement) stmt);
        
        throw new IllegalArgumentException ("unknown statement type " + stmt.getClass().getName());
    }
    
    private ExpressionBase convertErrorStatement (ErrorStatement stmt) {
        final ExpressionBase msg = convertExpression (stmt.getMessage());
        
        return new ExpressionBase (OldExpressionConverter.getSourcePos (stmt, stmt.getFileName())) {
            @Override
            protected Object evaluateInternal (org.eclipse.xtend.backend.common.ExecutionContext ctx) {
                System.err.println (msg.evaluate (ctx)); // TODO throw an exception instead?
                return null;
            }
        };
    }
    
    private ExpressionBase convertExpandStatement (ExpandStatement stmt, Set<XpandDefinitionName> referencedDefinitions) {
        if (stmt.isForeach()) {
            final ExpressionBase separator = (stmt.getSeparator() != null) ? convertExpression (stmt.getSeparator()) : null;
            final ExpressionBase target = convertExpression (stmt.getTarget());
            
            final String closureParamName = createUniqueLocalVarName();
            final List<ExpressionBase> params = new ArrayList<ExpressionBase> ();
            params.add (new LocalVarEvalExpression (closureParamName, getSourcePos(stmt)));
            for (Expression e: stmt.getParameters())
                params.add (convertExpression (e));
            
            final Type rawTargetType = new OldTypeAnalyzer().analyze(_ctx, stmt.getTarget());
            final Type targetType = (rawTargetType instanceof ParameterizedType) ? ((ParameterizedType) rawTargetType).getInnerType() : _ctx.getObjectType();
            
            final Type[] argTypes = new Type[stmt.getParametersAsList().size()];
            for (int i=0; i<stmt.getParametersAsList().size(); i++)
                argTypes[i] = stmt.getParametersAsList().get(i).analyze (_ctx, new HashSet<AnalysationIssue> ());

            final XpandDefinitionName called = new XpandDefinitionName (stmt.getDefinition().getValue(), targetType, argTypes, _ctx);
            referencedDefinitions.add (called);
            
            
            final ExpressionBase invocationExpression = new InvocationOnObjectExpression (new QualifiedName (called.getCanonicalDefinitionName()), params, false, getSourcePos(stmt));
            final ExpressionBase loopBody = new InitClosureExpression (Arrays.asList(closureParamName), Arrays.asList(ObjectType.INSTANCE), invocationExpression, getSourcePos(stmt));
            
            if (separator == null)
                return new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.FOREACH_WITHOUT_ITERATOR), Arrays.asList(target, loopBody), true, getSourcePos (stmt));
            else
                return new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.FOREACH_WITHOUT_ITERATOR), Arrays.asList(target, loopBody, separator), true, getSourcePos (stmt));
        }
        else {
            final List<ExpressionBase> params = new ArrayList<ExpressionBase>();
            if (stmt.getTarget() != null)
                params.add (convertExpression(stmt.getTarget()));
            else
                params.add (new LocalVarEvalExpression (SyntaxConstants.THIS, getSourcePos(stmt)));
            
            for (Expression e: stmt.getParameters())
                params.add (convertExpression (e));
            
            final XpandDefinitionName called = new XpandDefinitionName (stmt.getDefinition().getValue(), stmt.getTarget(), stmt.getParametersAsList(), _ctx);
            referencedDefinitions.add (called);
            return new InvocationOnObjectExpression (new QualifiedName (called.getCanonicalDefinitionName().replaceAll("/", SyntaxConstants.NS_DELIM)), params, true, getSourcePos(stmt));
        }
    }
    
    private String createUniqueLocalVarName () {
        return "$localVar_" + _localVarCounter++;
    }
    
    
    private ExpressionBase convertExpressionStatement (ExpressionStatement stmt) {
        return convertExpression (stmt.getExpression());
    }
    
    private ExpressionBase convertForEachStatement (ForEachStatement stmt, Set<XpandDefinitionName> referencedDefinitions) {
        final XpandExecutionContext oldContext = _ctx;
        
        final ExpressionBase separator = (stmt.getSeparator() != null) ? convertExpression (stmt.getSeparator()) : null;
        final ExpressionBase target = convertExpression (stmt.getTarget());
        
        final Type collType = new OldTypeAnalyzer().analyze (oldContext, stmt.getTarget());
        final Type eleType = (collType instanceof ParameterizedType) ? ((ParameterizedType) collType).getInnerType() : _ctx.getObjectType(); 

        final String varName = stmt.getVariable().getValue();

        ExpressionBase body;

        if (stmt.getIteratorName() == null) {
            // forEach without an iterator
            _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (varName, eleType));
            try {
                body = convertStatementSequence (stmt.getBody(), stmt, referencedDefinitions);
            }
            finally {
                _ctx = oldContext;
            }
            final ExpressionBase closureCreation = new InitClosureExpression (Arrays.asList (varName), Arrays.asList (_typeConverter.convertToBackendType(eleType)), body, getSourcePos (stmt));

            if (separator == null)
                return new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.FOREACH_WITHOUT_ITERATOR), Arrays.asList(target, closureCreation), true, getSourcePos (stmt));
            else
                return new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.FOREACH_WITHOUT_ITERATOR), Arrays.asList(target, closureCreation, separator), true, getSourcePos (stmt));
        }
        else {
            // forEach with an iterator
            _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (varName, eleType));
            _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (stmt.getIteratorName().getValue(), _ctx.getTypeForName (IteratorType.TYPE_NAME)));
            try {
                body = convertStatementSequence (stmt.getBody(), stmt, referencedDefinitions);
            }
            finally {
                _ctx = oldContext;
            }
            
            final List<String> paramNames = Arrays.asList (varName, stmt.getIteratorName().getValue());
            final List<BackendType> paramTypes = Arrays.asList (_typeConverter.convertToBackendType (eleType), _typeConverter.convertToBackendType (XtendIterator.class));
            
            final ExpressionBase closureCreation = new InitClosureExpression (paramNames, paramTypes, body, getSourcePos (stmt));

            if (separator == null)
                return new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.FOREACH_WITH_ITERATOR), Arrays.asList(target, closureCreation), true, getSourcePos (stmt));
            else
                return new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.FOREACH_WITH_ITERATOR), Arrays.asList(target, closureCreation, separator), true, getSourcePos (stmt));
        }
    }
    
    private ExpressionBase convertIfStatement (IfStatement stmt, Set<XpandDefinitionName> referencedDefinitions) {
        if (stmt.getCondition() != null) {
            final ExpressionBase condExpr = convertExpression (stmt.getCondition());
            final ExpressionBase ifExpr = convertStatementSequence(stmt.getBody(), stmt, referencedDefinitions);
            final ExpressionBase elseExpr = stmt.getElseIf() != null ? convertStatement (stmt.getElseIf(), referencedDefinitions) : new LiteralExpression (null, getSourcePos (stmt));
            
            return new IfExpression (condExpr, ifExpr, elseExpr, getSourcePos (stmt));
        }
        else {
            // the else part is an IfStatement with null condition
            return convertStatementSequence (stmt.getBody(), stmt, referencedDefinitions);
        }
    }
    
    
    private ExpressionBase convertLetStatement (LetStatement stmt, Set<XpandDefinitionName> referencedDefinitions) {
        final String varName = stmt.getVarName().getValue();
        final Type type = new OldTypeAnalyzer().analyze (_ctx, stmt.getVarValue());
        
        final XpandExecutionContext oldContext = _ctx;
        _ctx = (XpandExecutionContext) _ctx.cloneWithVariable (new Variable (varName, type));
        
        try {
            final ExpressionBase def = convertExpression (stmt.getVarValue());
            final ExpressionBase body = convertStatementSequence (stmt.getBody(), stmt, referencedDefinitions);
            
            if (oldContext.getVisibleVariables().containsKey (varName))
                return new HidingLocalVarDefExpression (varName, def, body, getSourcePos (stmt));
            else
                return new NewLocalVarDefExpression (varName, def, body, getSourcePos (stmt));
        }
        finally {
            _ctx = oldContext;
        }
    }
    
    private ExpressionBase convertFileStatement (FileStatement stmt, Set<XpandDefinitionName> referencedDefinitions) {
        final ExpressionBase body = convertStatementSequence (stmt.getBody(), stmt, referencedDefinitions);
        final ExpressionBase filename = convertExpression (stmt.getTargetFileName());
  
        final Outlet outlet = _ctx.getOutput().getOutlet (stmt.getOutletName());
        if (outlet == null) {
            if (stmt.getOutletName() == null)
                throw new IllegalStateException ("no default outlet was registered");
            else
                throw new IllegalStateException ("no outlet for name '" + stmt.getOutletName() + "' was registered");
        }
        
        final ExpressionBase outletName = new LiteralExpression ((stmt.getOutletName() != null) ? stmt.getOutletName() : FileIoOperations.DEFAULT_OUTLET_NAME, getSourcePos(stmt));
        final ExpressionBase append = new LiteralExpression (outlet.isAppend(), getSourcePos(stmt));
        
        final List<ExpressionBase> emptyParamList = Collections.emptyList();
        final ExpressionBase initIsDeleteLineExpression = new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.DELETE_LINE_INIT), emptyParamList, false, getSourcePos (stmt));

        final ExpressionBase postprocessIsDeleteLineExpression = new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.DELETE_LINE_POSTPROCESS), Arrays.asList(body), false, getSourcePos (stmt));
        final ExpressionBase writeToFileExpression = new InvocationOnObjectExpression (new QualifiedName (SysLibNames.WRITE_TO_FILE), Arrays.asList(outletName, filename, append, postprocessIsDeleteLineExpression), false, getSourcePos (stmt));
        
        return new SequenceExpression (Arrays.asList (initIsDeleteLineExpression, writeToFileExpression), getSourcePos (stmt));
    }
    
    private ExpressionBase convertProtectStatement (ProtectStatement stmt, Set<XpandDefinitionName> referencedDefinitions) {
    	ExpressionBase body = convertStatementSequence(stmt.getBody(), stmt, referencedDefinitions);
    	final ExpressionBase id = convertExpression(stmt.getId());
    	final ExpressionBase startComment = convertExpression(stmt.getCommentStart());
    	final ExpressionBase endComment = convertExpression(stmt.getCommentEnd());
    	final ExpressionBase isDisabled = new LiteralExpression(stmt.getDisable(), getSourcePos(stmt));
        final ExpressionBase protectExpr = new InvocationOnObjectExpression (new QualifiedName(XpandLibNames.PROTECT), Arrays.asList(id, startComment, endComment, isDisabled, body), true, getSourcePos(stmt));
        return protectExpr; //TODO implement ProtectStatement
    }
    
    private ExpressionBase convertTextStatement (TextStatement stmt) {
        if (stmt.isDeleteLine()) {
            final List<ExpressionBase> emptyParamList = Collections.emptyList();
            final ExpressionBase registerExpression = new InvocationOnObjectExpression (new QualifiedName (XtendLibNames.DELETE_LINE_REGISTER), emptyParamList, false, getSourcePos(stmt));
            
            final ExpressionBase markerExpression = new LiteralExpression (XpandIsDeleteLine.MARKER_FOR_IS_DELETE_LINE, getSourcePos(stmt));
            final ExpressionBase contentExpression = new LiteralExpression (stmt.getValue(), getSourcePos (stmt));
            final ExpressionBase concatExpression = new ConcatExpression (Arrays.asList(markerExpression, contentExpression), getSourcePos (stmt));
            
            return new SequenceExpression (Arrays.asList(registerExpression, concatExpression), getSourcePos (stmt));
        }
        else
            return new LiteralExpression (stmt.getValue(), getSourcePos(stmt));
    }
    
    
    private SourcePos getSourcePos (SyntaxElement stmt) {
        return OldExpressionConverter.getSourcePos(stmt, _definitionName);
    }
    
    private ExpressionBase convertExpression (Expression expr) {
        final OldExpressionConverter exprConverter = new OldExpressionConverter (_ctx, _typeConverter, _definitionName);
        return exprConverter.convert (expr);
    }
    
    private List<Type> getAdviceLocalVarTypes (TypeSystem ts) {
        return Arrays.asList (ts.getStringType(), ts.getStringType()); // any type other than Object will do - as a hint for the right optimizations
    }

}
