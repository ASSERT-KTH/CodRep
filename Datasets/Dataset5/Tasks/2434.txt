import org.eclipse.xtend.middleend.old.XtendBackendFacade;

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
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import junit.framework.TestCase;

import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.parser.SyntaxConstants;
import org.eclipse.internal.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.internal.xtend.type.impl.java.beans.JavaBeansStrategy;
import org.eclipse.internal.xtend.xtend.parser.ParseFacade;
import org.eclipse.xtend.backend.types.builtin.StringType;
import org.eclipse.xtend.expression.EvaluationException;
import org.eclipse.xtend.expression.ExecutionContext;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.Type1;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.middleend.old.xtend.XtendBackendFacade;
import org.eclipse.xtend.typesystem.Property;

/**
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Arno Haase
 */
public class EvaluationTest extends TestCase {

	private ExecutionContextImpl ec;

	@Override
	protected void setUp() {
		ec = new ExecutionContextImpl();
		ec.registerMetaModel (new JavaMetaModel("asdf", new JavaBeansStrategy()));
	}

	private Object eval (String expression) {
	    final Object oldResult = evalOld (expression);
	    final Object newResult = evalNew (expression);

	    checkEquals (oldResult, newResult);
	    
	    setUp (); // re-init ec
	    
	    return oldResult;
	}

	private Object evalOld (String expression) {
        final Expression expr = ParseFacade.expression(expression);
        return expr.evaluate (ec);
	}
	
	private Object evalNew (String expression) {
        final Map<String, Object> newLocalVars = new HashMap<String, Object> ();
        for (String vn: ec.getVisibleVariables().keySet())
            newLocalVars.put (vn, ec.getVisibleVariables().get(vn).getValue());
        
        final Map<String, Object> newGlobalVars = new HashMap<String, Object> ();
        for (String vn: ec.getGlobalVariables().keySet())
            newGlobalVars.put (vn, ec.getGlobalVariables().get(vn).getValue());
        
        return XtendBackendFacade.evaluateExpression (expression, ec.getMetaModels(), newLocalVars, newGlobalVars);
	}
	
	// be lenient about type equality - the new backend is more consistent at converting types than the old runtime is...
    private void checkEquals (Object o1, Object o2) {
        if (o1 == null) {
            assertTrue (o2 == null);
            return;
        }
        
        if (o1 instanceof Double && o2 instanceof Double) {
            assertEquals ((Double) o1, (Double) o2, .0000001);
            return;
        }
        
        if (o1 instanceof Number && o2 instanceof Number) {
            assertEquals (((Number) o1).longValue(), ((Number) o2).longValue());
            return;
        }
        
        if (o1 instanceof CharSequence && o2 instanceof CharSequence) {
                assertEquals (o1.toString(), o2.toString());
                return;
        }

        assertEquals (o1, o2);
    }

	
	private Object eval (String expression, String localVarName, Object localVarValue) {
	    ec = (ExecutionContextImpl) ec.cloneWithVariable (new Variable (localVarName, localVarValue));
	    return eval (expression);
	}
	
	public final void testSimple() {
		final Object result = eval ("true == null");
		assertFalse(((Boolean) result).booleanValue());
	}

	public final void testStaticPropertyCall() {
		final Object result = eval ("org::eclipse::xtend::expression::Type1::TYPE1_OBJECT_OBJECT");
		assertEquals(Type1.TYPE1_OBJECT_OBJECT, result);
	}

	@SuppressWarnings("unchecked")
    public final void testCollectionLiteral1() {
		assertEquals(Arrays.asList("hallo"), eval ("{\"hallo\"}"));
		assertEquals(Arrays.asList(3L), eval ("{3}"));
	    assertEquals (Arrays.asList("hallo", 3L), eval ("{\"hallo\",3}"));
	}

	public final void testFeatureCall() {
		final Object result = eval ("test", ExecutionContext.IMPLICIT_VARIABLE, new AType ());
		assertEquals(new AType().getTest(), result);
	}

	public final void testFeatureCall1() {
		final Object result = eval ("this.test", ExecutionContext.IMPLICIT_VARIABLE, new AType ());
		assertEquals(new AType().getTest(), result);
	}

	public final void testOperationCall1() {
		final Object result = eval ("myOperation()", ExecutionContext.IMPLICIT_VARIABLE, new AType ());
		assertEquals(new AType().myOperation(), result);
	}

	public final void testOperationCall2() {
		final Object result = eval ("myOperation(\"Test\")", ExecutionContext.IMPLICIT_VARIABLE, new AType ());
		assertEquals(new AType().myOperation("Test"), result);
	}

	public final void testOperationCall3() {
		final Object result = eval ("this.myOperation()", ExecutionContext.IMPLICIT_VARIABLE, new AType ());
		assertEquals(new AType().myOperation(), result);
	}

	public final void testOperationCall4() {
		final Object result = eval ("this.myOperation(\"Test\")", ExecutionContext.IMPLICIT_VARIABLE, new AType ());
		assertEquals(new AType().myOperation("Test"), result);
	}

	public final void testArithmetic() {
		assertEquals(new Long(11), eval ("4 * 2 + 3"));
		assertEquals(new Long(11), eval ("3 + 4 * 2"));
		assertEquals(new Long(9), eval ("4 * 2 + 3 / 3"));
		assertEquals(new Long(4), eval ("4 * 2 - (9 / 2)"));

		assertEquals(new Double(11), eval ("3 + 4.0 * 2"));
		assertEquals(new Double(11), eval ("4.0 * 2 + 3"));
		assertEquals(new Double(9), eval ("4 * 2 + 3 / 3.0"));

		assertEquals(new Long(2), eval ("5 / 2"));
		assertEquals(new Double(2.5), eval ("5 / 2.0"));
	}

	public final void testStringConcatenation() {
		assertEquals("test34", eval ("\"test\" + 3 + 4"));
	}

	public final void testNullReference() {
		assertEquals(null, eval ("nullRef + \"test\" + 3 + 4", "nullRef", null));
		assertNull(eval ("this.unknownMember", "this", null));
	}

	public final void testTypeLiteral1() {
		assertEquals (ec.getStringType(), evalOld ("String"));
		assertEquals (StringType.INSTANCE, evalNew ("String"));

		assertTrue (evalOld ("String.getProperty('length')") instanceof Property);
		assertTrue (evalNew ("String.getProperty('length')") instanceof org.eclipse.xtend.backend.common.Property);

		assertEquals (AType.TEST, eval (getATypeName() + "::TEST"));
	}

	private String getATypeName() {
		return AType.class.getName().replaceAll("\\.", SyntaxConstants.NS_DELIM);
	}

	public final void testPath1() {
	    assertEquals (Arrays.asList("A", "B", "C"), eval ("{'a','b','c'}.toUpperCase()"));

	    assertEquals(new Long(3), eval ("{'a','b','c'}.size"));

	    assertEquals (Arrays.asList (1L, 2L, 1L), eval ("{'a','b2','c'}.toUpperCase().length"));
	}

	public final void testPath4() {
		final List<?> result = (List<?>) eval ("{'a,b2,c','a,b,c','a,b,c'}.split(',').length");
		assertEquals(9, result.size());
		assertEquals(new Long(1), result.get(0));
		assertEquals(new Long(2), result.get(1));
		assertEquals(new Long(1), result.get(2));
	}

	public final void testNestedCollExpr() {
		final List<Object> list = new ArrayList<Object>();
		list.add("123");
		list.add("1234");
		list.add("12345");
		list.add(new Long(3));
		list.add(new Long(4));

		final String expr = "col.typeSelect(String).forAll (e|col.typeSelect(Integer).exists(a | a == e.length))";
		assertEquals(Boolean.FALSE, eval (expr, "col", list));
		
		list.add(new Long(5));
		assertEquals(Boolean.TRUE, eval (expr, "col", list));
	}

	public final void testTypeSelectWithNull() {
		assertEquals(new Long(1), eval ("{null, 'test'}.typeSelect(String).size"));
	}

	public final void testGlobalVar() {
		ec = new ExecutionContextImpl (Collections.singletonMap ("horst", new Variable("horst", "TEST")));
		assertEquals("TEST", eval ("GLOBALVAR horst"));
	}

	public final void testLet() {
		assertEquals("a,b,c", eval ("let x = {'a,b2,c','a,b,c','1,2,3'} : x.get(1)"));
		assertEquals(Arrays.asList("1", "2", "3"), eval ("let x = {} : x.add('1') -> x.add('2') -> x.add('3') -> x"));
	}

	public final void testCollectShortcut1() {
		assertEquals(Arrays.asList("A", "B", "C"), eval ("{'a','b','c'}.toUpperCase()"));
		assertEquals(Arrays.asList(1L, 1L, 1L), eval ("{'a','b','c'}.length"));

		assertEquals(Collections.emptyList(), eval ("{}.toUpperCase()"));
		assertEquals (Collections.emptyList(), eval ("{}.length"));
	}

	public final void testCollectShortcut5() {
		assertEquals ("String", eval ("String.name", ExecutionContext.IMPLICIT_VARIABLE, new ArrayList<Object>()));
	}

	public final void testConstruction() {
		assertEquals(new AType (), eval ("new org::eclipse::xtend::expression::ast::AType"));

		try {
			eval ("new Unkown");
			fail();
		} catch (final EvaluationException ee) {
			// expected
		}
	}

	public void testSortBy() throws Exception {
		assertEquals(Arrays.asList("AA", "BBB", "X"), eval ("{'X','AA','BBB'}.sortBy(e|e)"));
		assertEquals(Arrays.asList("X", "AA", "BBB"), eval ("{'X','AA','BBB'}.sortBy(e|e.length)"));
	}

	public void testIfExpression() throws Exception {
		assertEquals(true, eval ("if true then true else 'stuff'"));
		assertEquals("stuff", eval ("if false then false else 'stuff'"));
		assertEquals("stuff", eval ("if false then false else if true then 'stuff' else null "));
		assertEquals(null, eval ("if false then false else if false then 'stuff' "));
	}
	

	public void testCollectShortCutWithFeatureCalls() throws Exception {
		assertEquals (Arrays.asList ("test"), eval ("x.list.list.strings.toLowerCase()", "x", Collections.singletonList (new TestType ())));
		assertEquals (Arrays.asList ("test"), eval ("x.list().list().strings().toLowerCase()", "x", Collections.singletonList (new TestType ())));
		assertEquals (Arrays.asList ("test"), eval ("x.list.list().list.strings().toLowerCase()", "x", Collections.singletonList (new TestType ())));
	}
	
	public void testCollectOnNull() throws Exception {
		assertNull(eval("null.collect(e|e.size)"));
	}
	
	public void testEvaluationOrderOfOperands() throws Exception {
	    ec = (ExecutionContextImpl) ec.cloneWithVariable (new Variable ("x", new Cls()));
		checkEquals ("12", evalOld ("x.asString() + x.asString()"));

		ec = (ExecutionContextImpl) ec.cloneWithVariable (new Variable ("x", new Cls()));
		checkEquals ("12", evalNew ("x.asString() + x.asString()"));
	}
	
	public static class Cls {
	       int c = 1;

	       public String asString() {
               return ""+c++;
           }
	}
}