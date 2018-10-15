assertEquals ("before1 TestParam Testerossa TestParam Testerossa override after1 name: org::eclipse::xtend::middleend::xtend::test::expressions::testSomeFunctionAdviceCtx  paramNames: param,p  paramTypes: String,org::eclipse::xtend::middleend::xtend::test::Person  paramValues: TestParam,Person: Tester Testerossa", result.toString());

/*
Copyright (c) 2008 André Arnold.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    André Arnold - initial API and implementation
 */
package org.eclipse.xtend.middleend.xtend.test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import static junit.framework.Assert.assertEquals;

import org.eclipse.internal.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.xtend.middleend.xtend.XtendBackendFacade;
import org.eclipse.xtend.typesystem.MetaModel;
import org.junit.Before;
import org.junit.Test;

/**
 * 
 * @author André Arnold
 *
 */
public class AopTest extends JavaXtendTest {

	private Collection<MetaModel> mms = new ArrayList<MetaModel> ();
	
	@Before
	@Override
	public void setUp() throws Exception {
		super.setUp();
		mms.add(new JavaMetaModel());
	}
	
	@Test
	public void testAdvicedFunction() {
		Map<String, Object> vars = new HashMap<String, Object> ();
		vars.put("param", "TestParam");
		Object result = XtendBackendFacade.evaluateExpression ("testSomeAdvicedFunction(param)", "org::eclipse::xtend::middleend::xtend::test::expressions", "iso-8859-1", mms, vars, new HashMap<String, Object>(), Arrays.asList("org::eclipse::xtend::middleend::xtend::test::advices"));

		assertEquals ("before1 TestParam TestParam body after1", result.toString());
	}

	@Test
	public void testSomeAdvicedFunction() {
		Map<String, Object> vars = new HashMap<String, Object> ();
		vars.put("param", "TestParam");
		vars.put("p", _person);
		Object result = XtendBackendFacade.evaluateExpression ("testSomeAdvicedFunction(param, p)", "org::eclipse::xtend::middleend::xtend::test::expressions", "iso-8859-1", mms, vars, new HashMap<String, Object>(), Arrays.asList("org::eclipse::xtend::middleend::xtend::test::advices"));

		assertEquals ("before1 TestParam Testerossa TestParam after1", result.toString());
	}

	@Test
	public void testSomeSubPackageFunction() {
		Map<String, Object> vars = new HashMap<String, Object> ();
		vars.put("param1", "TestParam");
		vars.put("param2", 7L);
		Object result = XtendBackendFacade.evaluateExpression ("testSomeFunction(param1, param2)", "org::eclipse::xtend::middleend::xtend::test::sub::subpackage", "iso-8859-1", mms, vars, new HashMap<String, Object>(), Arrays.asList("org::eclipse::xtend::middleend::xtend::test::advices"));

		assertEquals ("before2 TestParam7 after2", result.toString());
	}

	@Test
	public void testAdviceSubPackageFunction() {
		Map<String, Object> vars = new HashMap<String, Object> ();
		vars.put("param1", "TestParam");
		vars.put("param2", 7L);
		Object result = XtendBackendFacade.evaluateExpression ("testAdviceSubPackageFunction(param1, param2)", "org::eclipse::xtend::middleend::xtend::test::expressions", "iso-8859-1", mms, vars, new HashMap<String, Object>(), Arrays.asList("org::eclipse::xtend::middleend::xtend::test::advices"));

		assertEquals ("before2 TestParam7 after2", result.toString());
	}

	@Test
	public void testOtherAdviceSubPackageFunction() {
		Map<String, Object> vars = new HashMap<String, Object> ();
		vars.put("param1", "TestParam");
		vars.put("param2", 7L);
		Object result = XtendBackendFacade.evaluateExpression ("testOtherAdviceSubPackageFunction(param1, param2)", "org::eclipse::xtend::middleend::xtend::test::expressions", "iso-8859-1", mms, vars, new HashMap<String, Object>(), Arrays.asList("org::eclipse::xtend::middleend::xtend::test::advices"));

		assertEquals ("before1 TestParam before2 TestParam7 after2 after1", result.toString());
	}

	@Test
	public void testSomeFunctionAdviceCtx() {
		Map<String, Object> vars = new HashMap<String, Object> ();
		vars.put("param", "TestParam");
		vars.put("p", _person);
		Object result = XtendBackendFacade.evaluateExpression ("testSomeFunctionAdviceCtx(param, p)", "org::eclipse::xtend::middleend::xtend::test::expressions", "iso-8859-1", mms, vars, new HashMap<String, Object>(), Arrays.asList("org::eclipse::xtend::middleend::xtend::test::advices"));

		assertEquals ("before1 TestParam Testerossa TestParam after1 name: org::eclipse::xtend::middleend::xtend::test::expressions::testSomeFunctionAdviceCtx  paramNames: param,p  paramTypes: String,org::eclipse::xtend::middleend::xtend::test::Person  paramValues: TestParam,Person: Tester Testerossa", result.toString());
	}
		
}