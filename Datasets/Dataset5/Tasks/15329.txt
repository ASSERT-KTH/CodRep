Object x = iter.next();

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.internal.xtend.expression.parser;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.internal.xtend.expression.ast.BooleanLiteral;
import org.eclipse.internal.xtend.expression.ast.BooleanOperation;
import org.eclipse.internal.xtend.expression.ast.Case;
import org.eclipse.internal.xtend.expression.ast.Cast;
import org.eclipse.internal.xtend.expression.ast.ChainExpression;
import org.eclipse.internal.xtend.expression.ast.CollectionExpression;
import org.eclipse.internal.xtend.expression.ast.ConstructorCallExpression;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.FeatureCall;
import org.eclipse.internal.xtend.expression.ast.GlobalVarExpression;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.internal.xtend.expression.ast.IfExpression;
import org.eclipse.internal.xtend.expression.ast.IntegerLiteral;
import org.eclipse.internal.xtend.expression.ast.LetExpression;
import org.eclipse.internal.xtend.expression.ast.ListLiteral;
import org.eclipse.internal.xtend.expression.ast.NullLiteral;
import org.eclipse.internal.xtend.expression.ast.OperationCall;
import org.eclipse.internal.xtend.expression.ast.RealLiteral;
import org.eclipse.internal.xtend.expression.ast.StringLiteral;
import org.eclipse.internal.xtend.expression.ast.SwitchExpression;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;
import org.eclipse.internal.xtend.expression.ast.TypeSelectExpression;
import org.eclipse.internal.xtend.xtend.ast.ExtensionFile;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class ExpressionFactory {

	private String fileName;

	public ExpressionFactory(final String string) {
		fileName = string;
	}

	public ExpressionFactory() {
		fileName = "nofile";
	}

	public Identifier createIdentifier(String text) {
		return handle(new Identifier(text));
	}

	public StringLiteral createStringLiteral(final Identifier t) {
		return handle(new StringLiteral(t));
	}

	public IntegerLiteral createIntegerLiteral(final Identifier t) {
		return handle(new IntegerLiteral(t));
	}

	public BooleanLiteral createBooleanLiteral(final Identifier t) {
		return handle(new BooleanLiteral(t));
	}

	public NullLiteral createNullLiteral(final Identifier t) {
		return handle(new NullLiteral(t));
	}

	public ListLiteral createListLiteral(List<Expression> paramExpr) {
		if (paramExpr == null)
			paramExpr = new ArrayList<Expression>();
		return handle(new ListLiteral(paramExpr
				.toArray(new Expression[paramExpr.size()])));
	}

	public FeatureCall createFeatureCall(final Identifier name,
			final Expression target) {
		return handle(new FeatureCall(name, target));
	}

	public OperationCall createOperationCall(final Identifier name,
			final Expression singleParam) {
		return handle(new OperationCall(name, singleParam));
	}

	public OperationCall createOperationCall(final Identifier name,
			List<Expression> parameterExpressions) {
		if (parameterExpressions == null)
			parameterExpressions = new ArrayList<Expression>();
		final Expression[] params = parameterExpressions
				.toArray(new Expression[parameterExpressions.size()]);
		return handle(new OperationCall(name, null, params));
	}

	public Expression createBinaryOperation(Identifier name, Expression left,
			Expression right) {
		return handle(new OperationCall(name, left, right));
	}

	public IfExpression createIf(final Expression cond, final Expression then,
			final Expression elseExpr) {
		return handle(new IfExpression(cond, then, elseExpr));
	}

	public CollectionExpression createCollectionExpression(
			final Identifier opName, final Identifier elementName,
			final Expression closure) {
		return handle(new CollectionExpression(opName,
				elementName, closure));
	}

	public DeclaredParameter createDeclaredParameter(final Identifier type,
			final Identifier name) {
		return handle(new DeclaredParameter(type, name));
	}

	public Expression createCast(final Identifier t, final Expression e) {
		return handle(new Cast(t, e));
	}

	protected <T extends SyntaxElement> T handle(final T expr) {
		expr.setFileName(fileName);
		return expr;
	}
	protected SyntaxElement handle(final ExtensionFile expr) {
		expr.setFileName(fileName);
		expr.setFullyQualifiedName(fileName);
		return expr;
	}

	public Case createCase(final Expression cond, final Expression then) {
		return handle(new Case(cond, then));
	}

	public SwitchExpression createSwitchExpression(final Expression switchExpr,
			final List<Case> cases, final Expression defaultExpr) {
		return handle(new SwitchExpression(switchExpr,
				nonNull(cases), defaultExpr));
	}

	public ChainExpression createChainExpression(final Expression head,
			final Expression next) {
		return handle(new ChainExpression(head, next));
	}

	public RealLiteral createRealLiteral(final Identifier lit) {
		return handle(new RealLiteral(lit));
	}

	public FeatureCall createTypeSelectExpression(final Identifier id,
			final Identifier ident) {
		return handle(new TypeSelectExpression(id, ident));
	}

	public BooleanOperation createBooleanOperation(final Identifier name,
			final Expression e, final Expression r) {
		return handle(new BooleanOperation(name, e, r));
	}

	public LetExpression createLetExpression(final Identifier v,
			final Expression varExpr, final Expression target) {
		return handle(new LetExpression(v, varExpr, target));
	}

	public Expression createConstructorCall(final Identifier type) {
		return handle(new ConstructorCallExpression(
				type));
	}

	public GlobalVarExpression createGlobalVarExpression(Identifier name) {
		return handle(new GlobalVarExpression(name));
	}

	public Expression createParanthesizedExpression(Expression x) {
		return x; // TODO create an AST element (when needed)
	}
	
	protected <T> List<T> nonNull(List<T> l) {
		if (l == null)
			return new ArrayList<T>();
		for (Iterator<T> iter = l.iterator(); iter.hasNext();) {
			Object x = (Object) iter.next();
			if (x==null)
				iter.remove();
		}
		return l;
	}
}