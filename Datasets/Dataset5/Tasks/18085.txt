import org.eclipse.emf.mwe.core.WorkflowContextDefaultImpl;

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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.WorkflowInterruptedException;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.issues.IssuesImpl;
import org.eclipse.emf.mwe.core.monitor.NullProgressMonitor;
import org.eclipse.emf.mwe.internal.core.WorkflowContextDefaultImpl;
import org.eclipse.xtend.middleend.xtend.CheckBackendFacade;
import org.eclipse.xtend.middleend.xtend.CheckComponent;
import org.eclipse.xtend.middleend.xtend.XtendBackendFacade;
import org.junit.Before;
import org.junit.Test;

/**
 * 
 * @author André Arnold
 *
 */
@SuppressWarnings("restriction")
public class CheckTest extends JavaXtendTest {

	@Before
	@Override
	public void setUp() throws Exception {
		super.setUp();
		_person.setName("xy");
		_employee.setCompany(null);
	}

	@Test
	public void testCheckAll() {
		Issues issues = new IssuesImpl();
		List<?> model = Arrays.asList(_person, _employee);

		CheckBackendFacade.checkAll(
				"org::eclipse::xtend::middleend::xtend::test::Checks",
				_mms, issues, model);

		assertEquals(1, issues.getErrors().length);
		assertEquals("Company not defined", issues.getErrors()[0].getMessage());
		assertEquals(1, issues.getWarnings().length);
		assertEquals("Name too short: " + _person.getName(), issues.getWarnings()[0].getMessage());
	}

	@Test
	public void testCheckFacade() {
		Issues issues = new IssuesImpl();
		List<?> model = Arrays.asList(_person, _employee);
		final Map<String, Object> localVars = new HashMap<String, Object>();
		localVars.put("MODEL_SLOT", model);

		Object o = XtendBackendFacade.evaluateExpression("MODEL_SLOT", _mms,
				localVars);
		Collection<?> result = null;
		if (o instanceof Collection) {
			result = (Collection<?>) o;
		} else if (o == null) {
			result = Collections.EMPTY_SET;
		} else {
			result = Collections.singleton(result);
		}
		CheckBackendFacade.checkAll(
				"org::eclipse::xtend::middleend::xtend::test::Checks",
				_mms, issues, result);

		assertEquals(1, issues.getErrors().length);
		assertEquals(1, issues.getWarnings().length);
	}

	@Test
	public void testCheckComponent() {
		List<?> model = Arrays.asList(_person, _employee);
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
		ctx.set("MODEL_SLOT", model);
		Issues issues = new IssuesImpl();

		CheckComponent chk = new CheckComponent();
		chk.addMetaModel(_mms.get(0));
		chk.setFileEncoding("ISO-8859-1");
		chk
				.addCheckFile("org::eclipse::xtend::middleend::xtend::test::Checks");
		chk.setExpression("MODEL_SLOT");
		try {
			chk.invoke(ctx, new NullProgressMonitor(), issues);
			fail("Errors expected");
		} catch (WorkflowInterruptedException e) {
			assertEquals(1, issues.getErrors().length);
			assertEquals(1, issues.getWarnings().length);
		}
	}

}