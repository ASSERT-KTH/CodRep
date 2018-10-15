return new org.eclipse.xtend.backend.expr.GlobalParamExpression (((GlobalVarExpression) expr).getVarName(), getSourcePos(expr));

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.middleend.old;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;

import org.eclipse.internal.xtend.expression.ast.BooleanLiteral;
import org.eclipse.internal.xtend.expression.ast.BooleanOperation;
import org.eclipse.internal.xtend.expression.ast.Case;
import org.eclipse.internal.xtend.expression.ast.ChainExpression;
import org.eclipse.internal.xtend.expression.ast.CollectionExpression;
import org.eclipse.internal.xtend.expression.ast.ConstructorCallExpression;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.FeatureCall;
import org.eclipse.internal.xtend.expression.ast.GlobalVarExpression;
import org.eclipse.internal.xtend.expression.ast.IfExpression;
import org.eclipse.internal.xtend.expression.ast.IntegerLiteral;
import org.eclipse.internal.xtend.expression.ast.LetExpression;
import org.eclipse.internal.xtend.expression.ast.ListLiteral;
import org.eclipse.internal.xtend.expression.ast.Literal;
import org.eclipse.internal.xtend.expression.ast.NullLiteral;
import org.eclipse.internal.xtend.expression.ast.OperationCall;
import org.eclipse.internal.xtend.expression.ast.RealLiteral;
import org.eclipse.internal.xtend.expression.ast.StringLiteral;
import org.eclipse.internal.xtend.expression.ast.SwitchExpression;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.internal.xtend.expression.ast.TypeSelectExpression;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.type.baseimpl.types.CollectionTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.ListTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.ObjectTypeImpl;
import org.eclipse.internal.xtend.type.baseimpl.types.SetTypeImpl;
import org.eclipse.xtend.backend.common.BackendType;
import org.eclipse.xtend.backend.common.ExpressionBase;
import org.eclipse.xtend.backend.common.SourcePos;
import org.eclipse.xtend.backend.expr.AndExpression;
import org.eclipse.xtend.backend.expr.CreateUncachedExpression;
import org.eclipse.xtend.backend.expr.HidingLocalVarDefExpression;
import org.eclipse.xtend.backend.expr.InitClosureExpression;
import org.eclipse.xtend.backend.expr.InvocationOnCollectionExpression;
import org.eclipse.xtend.backend.expr.InvocationOnObjectExpression;
import org.eclipse.xtend.backend.expr.InvocationOnWhateverExpression;
import org.eclipse.xtend.backend.expr.ListLiteralExpression;
import org.eclipse.xtend.backend.expr.LiteralExpression;
import org.eclipse.xtend.backend.expr.LocalVarEvalExpression;
import org.eclipse.xtend.backend.expr.NewLocalVarDefExpression;
import org.eclipse.xtend.backend.expr.OrExpression;
import org.eclipse.xtend.backend.expr.PropertyOnCollectionExpression;
import org.eclipse.xtend.backend.expr.PropertyOnObjectExpression;
import org.eclipse.xtend.backend.expr.PropertyOnWhateverExpression;
import org.eclipse.xtend.backend.expr.SequenceExpression;
import org.eclipse.xtend.backend.syslib.SysLibNames;
import org.eclipse.xtend.backend.types.builtin.ObjectType;
import org.eclipse.xtend.backend.util.Pair;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.StaticProperty;
import org.eclipse.xtend.typesystem.Type;


/**
 * converts a single expression
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
final class OldExpressionConverter {
    private final TypeToBackendType _typeConverter;
    private ExecutionContext _ctx;
    private final String _extensionName;
    
    public OldExpressionConverter (ExecutionContext ctx, TypeToBackendType typeConverter, String extensionName) {
        _typeConverter = typeConverter;
        _ctx = ctx;
        _extensionName = extensionName;
    }
    
    public ExpressionBase convert (Expression expr) {
        if (expr instanceof BooleanLiteral)
            return new LiteralExpression ("true".equals (((Literal) expr).getLiteralValue().getValue()), getSourcePos (expr));
        if (expr instanceof IntegerLiteral)
            return new LiteralExpression (new Long (((Literal) expr).getLiteralValue().getValue()), getSourcePos(expr));
        if (expr instanceof NullLiteral)
            return new LiteralExpression (null, getSourcePos (expr));
        if (expr instanceof RealLiteral)
            return new LiteralExpression (new Double (((Literal) expr).getLiteralValue().getValue()), getSourcePos(expr));
        if (expr instanceof StringLiteral)
            return new LiteralExpression (((StringLiteral) expr).getValue(), getSourcePos(expr));
        if (expr instanceof ListLiteral)
            return convertListLiteral ((ListLiteral) expr);

        if (expr instanceof OperationCall)
            return convertOperationCall ((OperationCall) expr);
        if (expr instanceof CollectionExpression)
            return convertCollectionExpression ((CollectionExpression) expr);
        if (expr instanceof TypeSelectExpression)
            return convertTypeSelectExpression ((TypeSelectExpression) expr);
        
        // This case must come *after* OperationCall etc. because of implementation inheritance in the Xtend AST!
        if (expr instanceof FeatureCall)
            return convertFeatureCallExpression ((FeatureCall) expr);
        
        if (expr instanceof BooleanOperation)
            return convertBooleanOperation ((BooleanOperation) expr);
        
        if (expr instanceof GlobalVarExpression)
            return new org.eclipse.xtend.backend.expr.GlobalVarExpression (((GlobalVarExpression) expr).getVarName(), getSourcePos(expr));
        if (expr instanceof LetExpression)
            return convertLetExpression((LetExpression) expr);
        if (expr instanceof ChainExpression)
            return convertChainExpression ((ChainExpression) expr);

        if (expr instanceof ConstructorCallExpression)
            return convertConstructorCallExpression ((ConstructorCallExpression) expr);
        if (expr instanceof IfExpression)
            convertIfExpression((IfExpression) expr);
        if (expr instanceof SwitchExpression)
            return convertSwitchExpression ((SwitchExpression) expr);
        
        throw new IllegalArgumentException ("unsupported expression type: " + expr.getClass().getName());
    }

    private ExpressionBase convertOperationCall (OperationCall expr) {
        final SourcePos sourcePos = getSourcePos (expr);
        final String functionName = transformFunctionName (expr.getName().getValue());
        
        final List<ExpressionBase> params = new ArrayList<ExpressionBase> ();
        for (Expression e: expr.getParams ()) 
            params.add (convert (e));

        final List<Type> paramTypes = new ArrayList<Type>();
        for (Expression e: expr.getParams())
            paramTypes.add (e.analyze(_ctx, new HashSet<AnalysationIssue>()));
        
        if (expr.getTarget() == null) {
            if (hasThis()) {
                // if a function matches directly (i.e. without implicitly passing 'this' as a first parameter), that
                //  has precedence in matching
                if (_ctx.getExtensionForTypes (functionName, paramTypes.toArray (new Type[0])) != null) 
                    return new InvocationOnObjectExpression (functionName, params, sourcePos);
                else {
                    final ExpressionBase thisExpression = new LocalVarEvalExpression (org.eclipse.xtend.backend.util.SyntaxConstants.THIS, sourcePos);
                    final Type thisType = (Type) _ctx.getVariable (ExecutionContext.IMPLICIT_VARIABLE).getValue();
                    return createInvocationOnTargetExpression(functionName, thisExpression, thisType, params, paramTypes, sourcePos);
                }
            }
            else 
                return new InvocationOnObjectExpression (functionName, params, sourcePos);
        }
        else
            return createInvocationOnTargetExpression(functionName, convert (expr.getTarget()), expr.getTarget ().analyze (_ctx, new HashSet<AnalysationIssue> ()), params, paramTypes, sourcePos);
    }
    
    /**
     * transform built-in operator names from the old to the new special names
     */
    private String transformFunctionName (String functionName) {
        if ("+".equals (functionName))
            return SysLibNames.OPERATOR_PLUS;
        if ("-".equals (functionName))
            return SysLibNames.OPERATOR_MINUS;
        if ("*".equals (functionName))
            return SysLibNames.OPERATOR_MULT;
        if ("/".equals (functionName))
            return SysLibNames.OPERATOR_DIV;
        if ("%".equals (functionName))
            return SysLibNames.OPERATOR_MOD;

        if ("==".equals (functionName))
            return SysLibNames.OPERATOR_EQUALS;
        if ("!=".equals (functionName))
            return SysLibNames.OPERATOR_NOT_EQUALS;
        if ("<".equals (functionName))
            return SysLibNames.OPERATOR_LESS;
        if ("<=".equals (functionName))
            return SysLibNames.OPERATOR_LESS_OR_EQUALS;
        if (">=".equals (functionName))
            return SysLibNames.OPERATOR_GREATER_OR_EQUALS;
        if (">".equals (functionName))
            return SysLibNames.OPERATOR_GREATER;
        
        if ("!".equals (functionName))
            return SysLibNames.OPERATOR_NOT;
        
        return functionName;
    }
    
    private ExpressionBase createInvocationOnTargetExpression (String functionName, ExpressionBase targetExpression, Type targetType, List<ExpressionBase> params, List<Type> paramTypes, SourcePos sourcePos) {
        final List<ExpressionBase> paramsWithoutFirst = params;
        final List<ExpressionBase> allParams = new ArrayList<ExpressionBase> ();
        allParams.add (targetExpression);
        allParams.addAll (params);
        
        if (isCollectionType (targetType)) {
            paramTypes.add (0, targetType);
            final Type[] paramTypeArray = paramTypes.toArray(new Type[0]);
            
            if (_ctx.getExtensionForTypes (functionName, paramTypeArray) != null) 
                // check if there is a function that directly matches the collection
                return new InvocationOnObjectExpression (functionName, allParams, sourcePos);
            else
                // otherwise, do a 'collect' and call the function on all elements of the collection
                return new InvocationOnCollectionExpression (targetExpression, functionName, paramsWithoutFirst, sourcePos);
        }
        
        if (isObjectType (targetType))
            // if the static type is "Object", we do not know if it is a collection, so we do the logic at runtime
            return new InvocationOnWhateverExpression (functionName, allParams, sourcePos);
        
        // otherwise we know that it is not a collection and can avoid repeating this logic at runtime
        return new InvocationOnObjectExpression (functionName, allParams, sourcePos);
    }
    
    private ExpressionBase convertTypeSelectExpression (TypeSelectExpression expr) {
        final SourcePos sourcePos = getSourcePos (expr);
        
        final Type t = _ctx.getTypeForName (expr.getTypeName());
        final ExpressionBase typeExpr = new LiteralExpression (_typeConverter.convertToBackendType(t), sourcePos);
        
        if (expr.getTarget() == null) {
            if (! hasThis())
                throw new IllegalStateException ("typeSelect with neither a target nor an implicit 'this'");
            
            final ExpressionBase thisExpr = new LocalVarEvalExpression (org.eclipse.xtend.backend.util.SyntaxConstants.THIS, sourcePos);
            return new InvocationOnObjectExpression ("typeSelect", Arrays.asList (thisExpr, typeExpr), sourcePos);
        }
        else
            return new InvocationOnObjectExpression ("typeSelect", Arrays.asList(convert (expr.getTarget()), typeExpr), sourcePos);
    }
    
    private ExpressionBase convertSwitchExpression (SwitchExpression expr) {
        final List<Pair<ExpressionBase, ExpressionBase>> cases = new ArrayList<Pair<ExpressionBase,ExpressionBase>>();
        for (Case c: expr.getCases())
            cases.add (new Pair<ExpressionBase, ExpressionBase> (convert (c.getCondition()), convert (c.getThenPart())));
        
        return new org.eclipse.xtend.backend.expr.SwitchExpression (convert (expr.getSwitchExpr()), cases, convert (expr.getDefaultExpr()), getSourcePos(expr));
    }
    
    private ExpressionBase convertListLiteral (ListLiteral expr) {
        final List<ExpressionBase> inner = new ArrayList<ExpressionBase>();
        
        for (Expression e: expr.getElements ())
            inner.add (convert (e));
        
        return new ListLiteralExpression (inner, getSourcePos(expr));
    }
    
    private ExpressionBase convertLetExpression (LetExpression expr) {
        final ExpressionBase varExpr = convert (expr.getVarExpression());
        final Type varType = expr.getVarExpression().analyze(_ctx, new HashSet<AnalysationIssue>());
        
        final ExecutionContext oldCtx = _ctx;
        _ctx = _ctx.cloneWithVariable (new Variable (expr.getName(), varType));
        
        try {
            if (oldCtx.getVisibleVariables().containsKey(expr.getName()))
                return new HidingLocalVarDefExpression (expr.getName(), varExpr, convert (expr.getTargetExpression()), getSourcePos(expr));
            else
                return new NewLocalVarDefExpression (expr.getName(), varExpr, convert (expr.getTargetExpression()), getSourcePos(expr));
        }
        finally {
            _ctx = oldCtx;
        }
    }
    
    private ExpressionBase convertIfExpression (IfExpression expr) {
        return new org.eclipse.xtend.backend.expr.IfExpression (
                convert (expr.getCondition()),
                convert (expr.getThenPart()),
                convert (expr.getElsePart()),
                getSourcePos(expr));
    }
    
    private ExpressionBase convertFeatureCallExpression (FeatureCall expr) {
        final SourcePos sourcePos = getSourcePos(expr);
        
        if (expr.getTarget() == null) {
            // 1. check for a static property
            final StaticProperty staticProp = expr.getEnumLiteral (_ctx);
            if (staticProp != null)
                return new LiteralExpression (staticProp.get(), sourcePos);
            
            // 2. check for a local variable
            if (_ctx.getVisibleVariables().containsKey (expr.getName().getValue())) 
                return new LocalVarEvalExpression (expr.getName().getValue(), sourcePos);
            
            // 3. check for a type literal
            try {
                return new LiteralExpression (_typeConverter.convertToBackendType (Arrays.asList (expr.getName().getValue().split(SyntaxConstants.NS_DELIM))), sourcePos);
            }
            catch (IllegalArgumentException exc) {} // do nothing - this means it is not a type literal
            
            // 4. check for "this"
            if (hasThis()) {
                final ExpressionBase thisExpr = new LocalVarEvalExpression (org.eclipse.xtend.backend.util.SyntaxConstants.THIS, sourcePos);
                return createPropertyExpression (thisExpr, (Type) _ctx.getVisibleVariables().get (ExecutionContext.IMPLICIT_VARIABLE).getValue(), expr.getName().getValue(), sourcePos);
            }
            
            throw new IllegalArgumentException ("feature call " + expr.toString() + " does not match any feature: " + sourcePos);
        }
        else {
            // evaluate the target and evaluate the property on the result
            final Type t = expr.getTarget().analyze (_ctx, new HashSet<AnalysationIssue>());
            return createPropertyExpression(convert (expr.getTarget()), t, expr.getName().getValue(), sourcePos);
        }
    }
    
    private ExpressionBase createPropertyExpression (ExpressionBase target, Type type, String varName, SourcePos sourcePos) {
        if (isCollectionType (type)) {
            if ("size".equals (varName) || "isEmpty".equals (varName)) 
                return new PropertyOnObjectExpression (target, varName, sourcePos);
            else
                return new PropertyOnCollectionExpression (target, varName, sourcePos);
        }
        
        if (isObjectType (type))
            return new PropertyOnWhateverExpression (target, varName, sourcePos);
        
        return new PropertyOnObjectExpression (target, varName, sourcePos);
    }
    
    private ExpressionBase convertConstructorCallExpression (ConstructorCallExpression expr) {
        final BackendType t = _typeConverter.convertToBackendType (Arrays.asList(expr.getTypeName()));
        return new CreateUncachedExpression (t, getSourcePos(expr));
    }
    
    private ExpressionBase convertCollectionExpression (CollectionExpression expr) {
        final SourcePos sourcePos = getSourcePos (expr);

        final String functionName = expr.getName().getValue();
        
        final ExecutionContext oldCtx = _ctx;
        _ctx = _ctx.cloneWithVariable (new Variable (expr.getElementName(), new ObjectTypeImpl (_ctx, "Object")));
        final ExpressionBase bodyExpr = convert (expr.getClosure());
        _ctx = oldCtx;

        final InitClosureExpression closureExpr = new InitClosureExpression (Arrays.asList(expr.getElementName()), Arrays.asList(ObjectType.INSTANCE), bodyExpr, sourcePos);
        
        if (expr.getTarget() == null) {
            if (! hasThis())
                throw new IllegalStateException (functionName + " with neither a target nor an implicit 'this'");
            
            final ExpressionBase thisExpr = new LocalVarEvalExpression (org.eclipse.xtend.backend.util.SyntaxConstants.THIS, sourcePos);
            return new InvocationOnObjectExpression (functionName, Arrays.asList (thisExpr, closureExpr), sourcePos);
        }
        else
            return new InvocationOnObjectExpression (functionName, Arrays.asList(convert (expr.getTarget()), closureExpr), sourcePos);
    }
    
    private ExpressionBase convertChainExpression (ChainExpression expr) {
        return new SequenceExpression (getInner(expr), getSourcePos(expr));
    }
    
    /**
     * extract the inner expressions as a "flat" list - they are stored as a 
     *  binary tree in the ChainExpression...
     */
    private List<ExpressionBase> getInner (ChainExpression expr) {
        final List<ExpressionBase> result = new ArrayList<ExpressionBase>();
        
        if (expr.getFirst() instanceof ChainExpression) 
            result.addAll (getInner ((ChainExpression) expr.getFirst()));
        else
            result.add (convert (expr.getFirst()));

        if (expr.getNext() instanceof ChainExpression) 
            result.addAll (getInner ((ChainExpression) expr.getNext()));
        else
            result.add (convert (expr.getNext()));
        
        return result;
    }
    
    private ExpressionBase convertBooleanOperation (BooleanOperation expr) {
        final ExpressionBase left = convert (expr.getLeft());
        final ExpressionBase right = convert (expr.getRight());
        
        if ("&&".equals (expr.getOperator().getValue()))
            return new AndExpression (left, right, getSourcePos(expr));
        if ("||".equals (expr.getOperator().getValue()))
            return new OrExpression (left, right, getSourcePos(expr));
        if ("implies".equals (expr.getOperator().getValue()))
            return new InvocationOnObjectExpression ("implies", Arrays.asList(left, right), getSourcePos(expr));
        
        throw new IllegalArgumentException ("unknown boolean operator " + expr.getOperator().getValue());
    }
    
    public SourcePos getSourcePos (SyntaxElement se) {
        return getSourcePos (se, _extensionName);
    }
    
    public static SourcePos getSourcePos (SyntaxElement se, String extensionName) {
        return new SourcePos (se.getFileName(), extensionName, se.getLine());
    }
    
    private boolean isObjectType (Type t) {
        return t instanceof ObjectTypeImpl;
    }
    
    private boolean isCollectionType (Type t) {
        return t instanceof CollectionTypeImpl ||
            t instanceof ListTypeImpl ||
            t instanceof SetTypeImpl;
    }
    
    private boolean hasThis () {
        return _ctx.getVisibleVariables().containsKey (ExecutionContext.IMPLICIT_VARIABLE);
    }
}
