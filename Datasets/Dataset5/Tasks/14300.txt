public ExtensionImportDeclaration anExtensionImport() throws RecognitionException {

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.internal.xpand2.parser;

import org.antlr.runtime.CommonToken;
import org.antlr.runtime.RecognitionException;
import org.antlr.runtime.TokenStream;
import org.eclipse.internal.xpand2.ast.*;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.FeatureCall;
import org.eclipse.internal.xtend.expression.ast.GlobalVarExpression;
import org.eclipse.internal.xtend.expression.ast.SyntaxElement;

public class XpandLocationAddingParser extends XpandParser {

	XpandLocationAddingParser(final TokenStream stream) {
		super(stream, new XpandFactory("nofile"));
	}

	XpandLocationAddingParser(final TokenStream stream, final String fileName) {
		super(stream, new XpandFactory(fileName));
	}

	private static <T extends SyntaxElement> T addLocation(final int[] startAndLine, final T ele, final int end) {
		if (ele != null) {
			ele.setStart(startAndLine[0]);
			ele.setLine(startAndLine[1]);
			ele.setEnd(end);
		}
		return ele;
	}

	private int[] start() {
		final CommonToken t = (CommonToken) input.LT(1);
		if (t == null)
			return new int[] { 0, 0 };
		return new int[] { t.getStartIndex(), t.getLine() };
	}

	private int end() {
		final CommonToken t = (CommonToken) input.LT(-1);
		if (t == null)
			return -1;
		return t.getStopIndex() + 1;
	}

	@Override
	public void reportError(final RecognitionException e) {
		System.out.println(super.getErrorMessage(e, tokenNames));
		throw new RuntimeException(e);
	}

	@Override
	public Expression additiveExpression() throws RecognitionException {
		return addLocation(start(), super.additiveExpression(), end());
	}

	@Override
	public Expression andExpression() throws RecognitionException {
		return addLocation(start(), super.andExpression(), end());
	}

	@Override
	public ImportDeclaration anExtensionImport() throws RecognitionException {
		return addLocation(start(), super.anExtensionImport(), end());
	}

	@Override
	public ImportDeclaration anImport() throws RecognitionException {
		return addLocation(start(), super.anImport(), end());
	}

	@Override
	public Advice around() throws RecognitionException {
		return addLocation(start(), super.around(), end());
	}

	@Override
	public Expression booleanLiteral() throws RecognitionException {
		return addLocation(start(), super.booleanLiteral(), end());
	}

	@Override
	public Expression castedExpression() throws RecognitionException {
		return addLocation(start(), super.castedExpression(), end());
	}

	@Override
	public Expression chainExpression() throws RecognitionException {
		return addLocation(start(), super.chainExpression(), end());
	}

	@Override
	public FeatureCall collectionExpression() throws RecognitionException {
		return addLocation(start(), super.collectionExpression(), end());
	}

	@Override
	public org.eclipse.internal.xtend.expression.ast.Identifier collectionType() throws RecognitionException {
		return addLocation(start(), super.collectionType(), end());
	}

	@Override
	public Expression constructorCall() throws RecognitionException {
		return addLocation(start(), super.constructorCall(), end());
	}

	@Override
	public DeclaredParameter declaredParameter() throws RecognitionException {
		return addLocation(start(), super.declaredParameter(), end());
	}

	@Override
	public Definition define() throws RecognitionException {
		return addLocation(start(), super.define(), end());
	}

	@Override
	public org.eclipse.internal.xtend.expression.ast.Identifier definitionName() throws RecognitionException {
		return addLocation(start(), super.definitionName(), end());
	}

	@Override
	public IfStatement elseIfStatement() throws RecognitionException {
		return addLocation(start(), super.elseIfStatement(), end());
	}

	@Override
	public IfStatement elseStatement() throws RecognitionException {
		return addLocation(start(), super.elseStatement(), end());
	}

	@Override
	public ErrorStatement errorStatement() throws RecognitionException {
		return addLocation(start(), super.errorStatement(), end());
	}

	@Override
	public ExpandStatement expandStatement() throws RecognitionException {
		return addLocation(start(), super.expandStatement(), end());
	}

	@Override
	public Expression expression() throws RecognitionException {
		return addLocation(start(), super.expression(), end());
	}

	@Override
	public ExpressionStatement expressionStmt() throws RecognitionException {
		return addLocation(start(), super.expressionStmt(), end());
	}

	@Override
	public FeatureCall featureCall() throws RecognitionException {
		return addLocation(start(), super.featureCall(), end());
	}

	@Override
	public FileStatement fileStatement() throws RecognitionException {
		return addLocation(start(), super.fileStatement(), end());
	}

	@Override
	public ForEachStatement foreachStatement() throws RecognitionException {
		return addLocation(start(), super.foreachStatement(), end());
	}

	@Override
	public GlobalVarExpression globalVarExpression() throws RecognitionException {
		return addLocation(start(), super.globalVarExpression(), end());
	}

	@Override
	public org.eclipse.internal.xtend.expression.ast.Identifier identifier() throws RecognitionException {
		return addLocation(start(), super.identifier(), end());
	}

	@Override
	public Expression ifExpression() throws RecognitionException {
		return addLocation(start(), super.ifExpression(), end());
	}

	@Override
	public IfStatement ifStatement() throws RecognitionException {
		return addLocation(start(), super.ifStatement(), end());
	}

	@Override
	public Expression impliesExpression() throws RecognitionException {
		return addLocation(start(), super.impliesExpression(), end());
	}

	@Override
	public Expression infixExpression() throws RecognitionException {
		return addLocation(start(), super.infixExpression(), end());
	}

	@Override
	public Expression letExpression() throws RecognitionException {
		return addLocation(start(), super.letExpression(), end());
	}

	@Override
	public LetStatement letStatement() throws RecognitionException {
		return addLocation(start(), super.letStatement(), end());
	}

	@Override
	public Expression listLiteral() throws RecognitionException {
		return addLocation(start(), super.listLiteral(), end());
	}

	@Override
	public Expression multiplicativeExpression() throws RecognitionException {
		return addLocation(start(), super.multiplicativeExpression(), end());
	}

	@Override
	public Expression nullLiteral() throws RecognitionException {
		return addLocation(start(), super.nullLiteral(), end());
	}

	@Override
	public Expression numberLiteral() throws RecognitionException {
		return addLocation(start(), super.numberLiteral(), end());
	}

	@Override
	public Expression orExpression() throws RecognitionException {
		return addLocation(start(), super.orExpression(), end());
	}

	@Override
	public Expression paranthesizedExpression() throws RecognitionException {
		return addLocation(start(), super.paranthesizedExpression(), end());
	}

	@Override
	public org.eclipse.internal.xtend.expression.ast.Identifier pointcut() throws RecognitionException {
		return addLocation(start(), super.pointcut(), end());
	}

	@Override
	public Expression primaryExpression() throws RecognitionException {
		return addLocation(start(), super.primaryExpression(), end());
	}

	@Override
	public ProtectStatement protectStatement() throws RecognitionException {
		return addLocation(start(), super.protectStatement(), end());
	}

	@Override
	public Expression relationalExpression() throws RecognitionException {
		return addLocation(start(), super.relationalExpression(), end());
	}

	@Override
	public Statement simpleStatement() throws RecognitionException {
		return addLocation(start(), super.simpleStatement(), end());
	}

	@Override
	public org.eclipse.internal.xtend.expression.ast.Identifier simpleType() throws RecognitionException {
		return addLocation(start(), super.simpleType(), end());
	}

	@Override
	public Statement statement() throws RecognitionException {
		return addLocation(start(), super.statement(), end());
	}

	@Override
	public Expression switchExpression() throws RecognitionException {
		return addLocation(start(), super.switchExpression(), end());
	}

	@Override
	public Template template() throws RecognitionException {
		return addLocation(start(), super.template(), end());
	}

	@Override
	public Statement text() throws RecognitionException {
		return addLocation(start(), super.text(), end());
	}

	@Override
	public org.eclipse.internal.xtend.expression.ast.Identifier type() throws RecognitionException {
		return addLocation(start(), super.type(), end());
	}

	@Override
	public Expression unaryExpression() throws RecognitionException {
		return addLocation(start(), super.unaryExpression(), end());
	}

}