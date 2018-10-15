final Expression e = parse("String.getOperation('length',(List[xpand2::Type]){})");

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

package org.eclipse.xtend.expression.ast;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import junit.framework.TestCase;

import org.eclipse.internal.xtend.expression.ast.ChainExpression;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.Identifier;
import org.eclipse.internal.xtend.expression.ast.SwitchExpression;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.internal.xtend.type.impl.java.beans.JavaBeansStrategy;
import org.eclipse.internal.xtend.xtend.ast.ExtensionFile;
import org.eclipse.internal.xtend.xtend.ast.ImportStatement;
import org.eclipse.internal.xtend.xtend.parser.ParseFacade;
import org.eclipse.xtend.expression.AnalysationIssue;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.Resource;
import org.eclipse.xtend.expression.Type1;
import org.eclipse.xtend.expression.Type2;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.Callable;
import org.eclipse.xtend.typesystem.ParameterizedType;
import org.eclipse.xtend.typesystem.Property;
import org.eclipse.xtend.typesystem.Type;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class AnalyzationTest extends TestCase {

	private Set<AnalysationIssue> issues;

	private ExecutionContextImpl ec;

	@Override
	protected void setUp() throws Exception {
		ec = new ExecutionContextImpl();
		ec
				.registerMetaModel(new JavaMetaModel("asdf",
						new JavaBeansStrategy()));
		issues = new HashSet<AnalysationIssue>();
	}

	private Expression parse(final String expression) {
		return ParseFacade.expression(expression);
	}

	private void dumpIssues() {
		for (final Iterator<AnalysationIssue> iter = issues.iterator(); iter
				.hasNext();) {
			final AnalysationIssue element = iter.next();
			System.out.println(element.getType().toString() + " - "
					+ element.getMessage());
		}
	}

	public final void testEquals() {
		final Expression expr = parse("true == null");
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getBooleanType(), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testStaticPropertyCall() {
		final Expression expr = parse("org::eclipse::xtend::expression::Type1::TYPE1_OBJECT_OBJECT");
		final Type result = expr.analyze(ec, issues);
		assertTrue(issues.toString(), issues.isEmpty());
		assertNotNull("Static property not resolved. ", result);
		dumpIssues();
		assertEquals(ec.getStringType(), result);
	}

	public final void testCollectionLiteral1() {
		final Expression expr = parse("{\"hallo\"}");
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getListType(ec.getStringType()), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testCollectionLiteral3() {
		final Expression expr = parse("{3}");
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getListType(ec.getIntegerType()), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testCollectionLiteral2() {
		final Expression expr = parse("{\"hallo\",3}");
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getListType(ec.getObjectType()), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testFeatureCall() {
		final Expression expr = parse("test");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertTrue(issues.toString(), issues.isEmpty());
		assertEquals(ec.getStringType(), result);
	}

	public final void testFeatureCall1() {
		final Expression expr = parse("this.test");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getStringType(), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testOperationCall1() {
		final Expression expr = parse("myOperation()");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getStringType(), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testOperationCall2() {
		final Expression expr = parse("myOperation(\"Test\")");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getIntegerType(), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testOperationCall3() {
		final Expression expr = parse("this.myOperation()");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getStringType(), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testOperationCall4() {
		final Expression expr = parse("this.myOperation(\"Test\")");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(ec.getIntegerType(), result);
		assertTrue(issues.toString(), issues.isEmpty());
	}

	public final void testSwitchExpr() {
		final SwitchExpression expr = (SwitchExpression) parse("switch (3) { case \"Test\" : true default : false }");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(1, issues.size());
		assertEquals(ec.getBooleanType(), result);

	}

	public final void testSwitchExpr1() {
		final SwitchExpression expr = (SwitchExpression) parse("switch (\"Horst\") { case \"Test\" : true default : 3 }");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getObjectType(), result);

	}

	public final void testSwitchExpr2() {
		final SwitchExpression expr = (SwitchExpression) parse("switch { case \"Test\"==null : true default : false }");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getBooleanType(), result);

	}

	public final void testChainExpr() {
		final ChainExpression expr = (ChainExpression) parse("switch { case \"Test\"==null : true default : false } -> 3");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getIntegerType(), result);
	}

	public final void testChainExpr1() {
		final ChainExpression expr = (ChainExpression) parse("true -> List -> 3 -> \"Test\"");
		ec = (ExecutionContextImpl) ec.cloneWithVariable(new Variable(
				ExecutionContext.IMPLICIT_VARIABLE, ec
						.getTypeForName(getATypeName())));
		final Type result = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getStringType(), result);
	}

	public final void testTypeLiteral1() {
		assertEquals(ec.getTypeType(), parse("String").analyze(ec,
				new HashSet<AnalysationIssue>()));
	}

	public final void testTypeLiteral2() {
		final Expression e = parse("String.getOperation('length',(List[oaw::Type]){})");
		assertEquals(ec.getOperationType(), e.analyze(ec,
				new HashSet<AnalysationIssue>()));
	}

	public final void testTypeLiteral3() {
		final Expression e = parse(getATypeName() + "::TEST");
		assertEquals(ec.getStringType(), e.analyze(ec,
				new HashSet<AnalysationIssue>()));
	}

	private String getATypeName() {
		return AType.class.getName()
				.replaceAll("\\.", SyntaxConstants.NS_DELIM);
	}

	public final void testSelect() {
		final Expression expr = parse("String.allProperties.select(element.name=='length').toList().get(0)");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getPropertyType(), t);
	}

	public final void testTypeSelect() {
		final Expression expr = parse("{3.4,3}.typeSelect(Integer)");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getIntegerType()), t);
	}

	public final void testPath1() {
		final Expression expr = parse("{'a','b','c'}.toUpperCase()");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getStringType()), t);
	}

	public final void testPath2() {
		final Expression expr = parse("{'a','b','c'}.size");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getIntegerType(), t);
	}

	public final void testPath3() {
		final Expression expr = parse("{'a','b','c'}.toUpperCase().length");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getIntegerType()), t);
	}

	public final void testPath4() {
		final Expression expr = parse("{'a,b,c','a,b,c','a,b,c'}.split(',').length");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getIntegerType()), t);
	}

	public final void testImplies() {
		final Expression expr = parse("true implies false");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getBooleanType(), t);
	}

	public final void testImplies1() {
		final Expression expr = parse("true implies null");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(1, issues.size());
		assertEquals(ec.getBooleanType(), t);
	}

	public final void testLet1() {
		final Expression expr = parse("let x = true : x");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getBooleanType(), t);
	}

	public final void testLet2() {
		final Expression expr = parse("let x = true : 'test'+x");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getStringType(), t);
	}

	public final void testLet3() {
		final Expression expr = parse("let x = stuff : true");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(1, issues.size());
		assertNull(t);
	}

	public final void testCast1() {
		final Expression expr = parse("(List[String]) {}");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getStringType()), t);
	}

	public final void testCast2() {
		final Expression expr = parse("(Collection[String]) {}");
		final Type t = expr.analyze(ec, issues);
		dumpIssues();
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getStringType()), t);
	}

	public final void testConstruction() {
		Expression expr = parse("new String");
		Type t = expr.analyze(ec, issues);
		assertEquals(0, issues.size());
		assertEquals(ec.getStringType(), t);

		expr = parse("new Unknown");
		t = expr.analyze(ec, issues);
		assertEquals(1, issues.size());
		assertNull(t);
	}

	public void testSelectFirst() throws Exception {
		Expression expr = parse("{'test','holla'}.selectFirst(e|e=='honk')");
		Type t = expr.analyze(ec, issues);
		assertEquals(0, issues.size());
		assertEquals(ec.getStringType(), t);
	}

	public void testSortBy() throws Exception {
		Expression expr = parse("{'test','holla'}.sortBy(e|e)");
		Type t = expr.analyze(ec, issues);
		assertEquals(0, issues.size());
		assertEquals(ec.getListType(ec.getStringType()), t);
	}

	/**
	 * Import of an non-existent extension must lead to an error
	 */
	public void testBug174611() throws Exception {
		// create the lists to initialize an ExtensionFile instance
		// create an erraneous AbstractExtension Import
		List<ImportStatement> importStatements = new ArrayList<ImportStatement>();
		importStatements.add(new ImportStatement(new Identifier(
				"nonsense_import"), false));

		ExtensionFile extensionFile = new ExtensionFile(Collections.EMPTY_LIST,
				importStatements, Collections.EMPTY_LIST,
				Collections.EMPTY_LIST, Collections.EMPTY_LIST);
		extensionFile.analyze(ec, issues);
		assertEquals(1, issues.size());
	}

	public void testCollectShortCutWithFeatureCalls() throws Exception {
		Expression e = parse("x.list.list.strings.toLowerCase()");
		TestMetaModel mm = new TestMetaModel();
		ec.registerMetaModel(mm);
		ExecutionContext ctx = ec.cloneWithVariable(new Variable("x",
				ec.getCollectionType(mm.singleType)));
		Type rt = e.analyze(ctx, issues);
		assertTrue(issues.toString(), issues.isEmpty());
		assertTrue(rt instanceof ParameterizedType);
		assertEquals(ec.getStringType(),
				((ParameterizedType) rt).getInnerType());
	}

	public void testCollectShortCutWithOperationCalls() throws Exception {
		Expression e = parse("x.list().list().strings().toLowerCase()");
		TestMetaModel mm = new TestMetaModel();
		ec.registerMetaModel(mm);
		ExecutionContext ctx = ec.cloneWithVariable(new Variable("x",
				ec.getCollectionType(mm.singleType)));
		Type rt = e.analyze(ctx, issues);
		assertTrue(issues.toString(), issues.isEmpty());
		assertTrue(rt instanceof ParameterizedType);
		assertEquals(ec.getStringType(),
				((ParameterizedType) rt).getInnerType());
	}
	
	public void testCollectShortCutWithExtensionCalls() throws Exception {
		Expression e = parse("x.listExtension().listExtension().strings().toLowerCase()");
		final TestMetaModel mm = new TestMetaModel();
		ec = new ExecutionContextImpl();
		ec.registerMetaModel(mm);
		ec = (ExecutionContextImpl) ec.cloneWithResource(new Resource(){

			public String getFullyQualifiedName() {
				return null;
			}

			public String[] getImportedExtensions() {
				return new String[]{"org::eclipse::xtend::expression::ast::TestExtensions"};
			}

			public String[] getImportedNamespaces() {
				return null;
			}

			public void setFullyQualifiedName(String fqn) {
				
			}});
		ExecutionContext ctx = ec.cloneWithVariable(new Variable("x",
				ec.getCollectionType(mm.singleType)));
		Type rt = e.analyze(ctx, issues);
		System.out.println(issues);
		assertTrue(issues.toString(), issues.isEmpty());
		assertTrue(rt instanceof ParameterizedType);
		assertEquals(ec.getStringType(),
				((ParameterizedType) rt).getInnerType());
	}

	public void testCollectShortCutWithMixedCalls() throws Exception {
		Expression e = parse("x.list.list().list.strings().toLowerCase()");
		TestMetaModel mm = new TestMetaModel();
		ec.registerMetaModel(mm);
		ExecutionContext ctx = ec.cloneWithVariable(new Variable("x",
				ec.getCollectionType(mm.singleType)));
		Type rt = e.analyze(ctx, issues);
		assertTrue(issues.toString(), issues.isEmpty());
		assertTrue(rt instanceof ParameterizedType);
		assertEquals(ec.getStringType(),
				((ParameterizedType) rt).getInnerType());
	}
	
	public void testGetAllFeatures() throws Exception {
		Type1 type2 = new Type2();
		Type type = ec.getType(type2);
		Set<? extends Callable> allFeatures = type.getAllFeatures();
		boolean matched =false;
		for (Callable callable : allFeatures) {
			if (callable instanceof Property) {
				Property p = (Property) callable;
				if (p.getName().equals("test")) {
					assertEquals(type,p.getOwner());
					matched = true;
				}
			}
		}
		assertTrue("no property 'test' found",matched);
	}
}