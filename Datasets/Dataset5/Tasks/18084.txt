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
package org.eclipse.xtend.middleend.xpand.test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Collection;

import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.WorkflowInterruptedException;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.issues.IssuesImpl;
import org.eclipse.emf.mwe.core.monitor.NullProgressMonitor;
import org.eclipse.emf.mwe.internal.core.WorkflowContextDefaultImpl;
import org.eclipse.xpand2.output.Outlet;
import org.eclipse.xtend.middleend.xpand.XpandComponent;
import org.junit.Test;

/**
 * 
 * @author André Arnold
 *
 */
@SuppressWarnings("restriction")
public class XpandAopTest extends AbstractXpandTest {

	@Test
	public void testSomeAdvicedFunction () throws Exception {
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
		ctx.set("MODEL_SLOT", "world");
		Issues issues = new IssuesImpl();
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);

		XpandComponent xp = new XpandComponent();
		xp.addMetaModel(_mms.get(0));
		xp.addAdvice("org::eclipse::xtend::middleend::xpand::test::advices");
		xp.setExpand("org::eclipse::xtend::middleend::xpand::test::XpandStatements::testAop FOR MODEL_SLOT");
		xp.addOutlet(out);
		try {
			xp.invoke(ctx, new NullProgressMonitor(), issues);
			File outFile = new File("out", "aopoutput1.txt");
			assertTrue(outFile.exists());
			BufferedReader r = new BufferedReader(new FileReader(outFile));
			String line = null;
			StringBuffer buf = new StringBuffer();
			while ((line = r.readLine()) != null) {
				buf.append(line+"\n");
			}
			assertEquals("pre1: *SomeAdviced* (pre3: *SomeAdviced* (*) (world) post3\n) post1\n", buf.toString());
			r.close();
			outFile.delete();			
		} catch (WorkflowInterruptedException e) {
			fail(e.getMessage());
		}

	}

	@Test
	public void testAopNameNotMatched () throws Exception {
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
		ctx.set("MODEL_SLOT", "world");
		Issues issues = new IssuesImpl();
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);

		XpandComponent xp = new XpandComponent();
		xp.addMetaModel(_mms.get(0));
		xp.addAdvice("org::eclipse::xtend::middleend::xpand::test::advices");
		xp.setExpand("org::eclipse::xtend::middleend::xpand::test::XpandStatements::testAopNameNotMatched FOR MODEL_SLOT");
		xp.addOutlet(out);
		try {
			xp.invoke(ctx, new NullProgressMonitor(), issues);
			File outFile = new File("out", "aopoutput2.txt");
			assertTrue(outFile.exists());
			BufferedReader r = new BufferedReader(new FileReader(outFile));
			String line = null;
			StringBuffer buf = new StringBuffer();
			while ((line = r.readLine()) != null) {
				buf.append(line+"\n");
			}
			assertEquals("world\n", buf.toString());
			r.close();
			outFile.delete();			
		} catch (WorkflowInterruptedException e) {
			fail(e.getMessage());
		}

	}

	@Test
	public void testAopParamsMatched () throws Exception {
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
		ctx.set("MODEL_SLOT", "world");
		ctx.set("param", "param");
		Issues issues = new IssuesImpl();
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);

		XpandComponent xp = new XpandComponent();
		xp.addMetaModel(_mms.get(0));
		xp.addAdvice("org::eclipse::xtend::middleend::xpand::test::advices");
		xp.setExpand("org::eclipse::xtend::middleend::xpand::test::XpandStatements::testAopParamsMatched(param) FOR MODEL_SLOT");
		xp.addOutlet(out);
		try {
			xp.invoke(ctx, new NullProgressMonitor(), issues);
			File outFile = new File("out", "aopoutput3.txt");
			assertTrue(outFile.exists());
			BufferedReader r = new BufferedReader(new FileReader(outFile));
			String line = null;
			StringBuffer buf = new StringBuffer();
			while ((line = r.readLine()) != null) {
				buf.append(line+"\n");
			}
			assertEquals("pre2: *SomeAdviced* (String param1, *) param (pre3: *SomeAdviced* (*) (world param) post3\n) post2\n", buf.toString());
			r.close();
			outFile.delete();			
		} catch (WorkflowInterruptedException e) {
			fail(e.getMessage());
		}
	}


	@Test
	public void testAopWildcardParamsMatched () throws Exception {
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
		ctx.set("MODEL_SLOT", "world");
		ctx.set("param", "param");
		ctx.set("person", _person);
		Issues issues = new IssuesImpl();
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);

		XpandComponent xp = new XpandComponent();
		xp.addMetaModel(_mms.get(0));
		xp.addAdvice("org::eclipse::xtend::middleend::xpand::test::advices");
		xp.setExpand("org::eclipse::xtend::middleend::xpand::test::XpandStatements::testAopWildcardParamsMatched(param, person) FOR MODEL_SLOT");
		xp.addOutlet(out);
		try {
			xp.invoke(ctx, new NullProgressMonitor(), issues);
			File outFile = new File("out", "aopoutput4.txt");
			assertTrue(outFile.exists());
			BufferedReader r = new BufferedReader(new FileReader(outFile));
			String line = null;
			StringBuffer buf = new StringBuffer();
			while ((line = r.readLine()) != null) {
				buf.append(line+"\n");
			}
			assertEquals("pre2: *SomeAdviced* (String param1, *) param (pre3: *SomeAdviced* (*) (world param Testerossa) post3\n) post2\n", buf.toString());
			r.close();
			outFile.delete();			
		} catch (WorkflowInterruptedException e) {
			fail(e.getMessage());
		}
	}
}