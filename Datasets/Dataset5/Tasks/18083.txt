import org.eclipse.emf.mwe.core.WorkflowContextDefaultImpl;

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
package org.eclipse.xtend.middleend.xpand.test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.emf.mwe.core.WorkflowContext;
import org.eclipse.emf.mwe.core.WorkflowInterruptedException;
import org.eclipse.emf.mwe.core.issues.Issues;
import org.eclipse.emf.mwe.core.issues.IssuesImpl;
import org.eclipse.emf.mwe.core.monitor.NullProgressMonitor;
import org.eclipse.emf.mwe.internal.core.WorkflowContextDefaultImpl;
import org.eclipse.internal.xpand2.codeassist.XpandTokens;
import org.eclipse.internal.xtend.type.impl.java.JavaBeansMetaModel;
import org.eclipse.xpand2.output.Outlet;
import org.eclipse.xtend.backend.BackendFacade;
import org.eclipse.xtend.backend.common.ExecutionContext;
import org.eclipse.xtend.backend.common.QualifiedName;
import org.eclipse.xtend.backend.types.CompositeTypesystem;
import org.eclipse.xtend.backend.util.FileHelper;
import org.eclipse.xtend.middleend.xpand.XpandBackendFacade;
import org.eclipse.xtend.middleend.xpand.XpandComponent;
import org.eclipse.xtend.middleend.xtend.XtendBackendFacade;
import org.eclipse.xtend.typesystem.MetaModel;
import org.junit.Test;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 *
 */
@SuppressWarnings("restriction")
public class GeneralXpandTest extends AbstractXpandTest {
	
    @Test
    @SuppressWarnings("unchecked")
    public void testXtendFacade() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        
        final CompositeTypesystem ts = new CompositeTypesystem ();
        
        final XtendBackendFacade bc = XtendBackendFacade.createForFile ("org::eclipse::xtend::middleend::xpand::test::first", "iso-8859-1", mms);
        final ExecutionContext ctx = BackendFacade.createExecutionContext (bc.getFunctionDefContext(), ts, true);

        assertEquals ("Hallo, Arno: 27 - imported 99!", BackendFacade.invoke (ctx, new QualifiedName ("test"), Arrays.asList ("Arno")).toString());
        assertEquals ("[a Hallo b]", BackendFacade.invoke (ctx, new QualifiedName ("testColl"), Arrays.asList (Arrays.asList (1L, "Hallo"))).toString());
        assertEquals (10L, BackendFacade.invoke (ctx, new QualifiedName ("reexp"), Arrays.asList (2L)));

        final Person p = new Person ();
        p.setFirstName ("Testa");
        p.setName ("Testarossa");

        assertEquals ("[Testa Testarossa] - Testa Testarossa - Testa Testarossa - Testa", BackendFacade.invoke (ctx, new QualifiedName ("testPerson"), Arrays.asList(p)).toString());
    }
    
    @Test
    public void testEvaluateExpression() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        
        assertEquals ("Hallo, Arno: 27 - imported 99!", XtendBackendFacade.invokeXtendFunction ("org::eclipse::xtend::middleend::xpand::test::first", null, mms, new QualifiedName ("test"), "Arno").toString());
        assertEquals (7L, XtendBackendFacade.evaluateExpression ("1 + 2 + \"asdf\".length", null, null));
        assertEquals (33L, XtendBackendFacade.evaluateExpression ("1 + 2 + test(\"Arno\").length", "org::eclipse::xtend::middleend::xpand::test::first", null, mms, null));
    }
    
    @Test
    public void testTemplate() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::aTemplate", "iso-8859-1", mms, null );
		Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("element", "world");
		Object o = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::aTemplate::greeting FOR element" + XpandTokens.RT, variables , null, null);
		
		assertEquals("\nHello, world: Hallo, world: 27 - imported 99!\n" +
				"\n  Name: world \n" +
				"\n" +
				"\n\n    ... output from otherTemplate.xpt...\n" +
				"\n\n  This is a message from another package!\n" +
				"\n\n  This is a message from another package!\n" +
				"\n\n  This is a message from another package!\n" +
				"\n\n", o.toString());
    }
    
	@Test
	public void testXpandComponent () throws Exception {
//		List model = Arrays.asList("someText");
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
		ctx.set("MODEL_SLOT", "world");
		Issues issues = new IssuesImpl();
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);

		XpandComponent xp = new XpandComponent();
		xp.addMetaModel(_mms.get(0));
		xp.setExpand("org::eclipse::xtend::middleend::xpand::test::WithFileOutput::WithFileOutput FOR MODEL_SLOT");
		xp.addOutlet(out);
		try {
			xp.invoke(ctx, new NullProgressMonitor(), issues);
			File outFile = new File("out", "dummy.txt");
			assertTrue(outFile.exists());
			BufferedReader r = new BufferedReader(new FileReader(outFile));
			String line = null;
			StringBuffer buf = new StringBuffer();
			while ((line = r.readLine()) != null) {
				buf.append(line+"\n");
			}
			assertEquals("\n	Hello world: 5!\n	\n", buf.toString());
			r.close();
			outFile.delete();			
		} catch (WorkflowInterruptedException e) {
			fail(e.getMessage());
		}

	}
    
	@Test
	public void testXpandComponentWithProtectedRegions () throws Exception {
//		List model = Arrays.asList("someText");
		WorkflowContext ctx = new WorkflowContextDefaultImpl();
        Person p = new Person();
        p.setName("Tester");
        p.setFirstName("Testerossa");

		ctx.set("MODEL_SLOT", p);
		Issues issues = new IssuesImpl();
        Outlet out = new Outlet("out4");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);

        File generatedFile = new File (out.getPath() + "/Person.java");
		if (generatedFile.exists ())
			generatedFile.delete ();

		XpandComponent xp = new XpandComponent();
		xp.addMetaModel(_mms.get(0));
		xp.setExpand("org::eclipse::xtend::middleend::xpand::test::XpandProtectedRegions::testProtect FOR MODEL_SLOT");
		xp.addOutlet(out);
		xp.setFileEncoding("ISO-8859-1");
		try {
			xp.invoke(ctx, new NullProgressMonitor(), issues);
			final String initalExpected = "\npackage org.eclipse.xtend.middleend.xpand.test;\n\npublic class Person {\n\npublic void someOperation {\n/*PROTECTED REGION ID(Person_Tester_1) ENABLED START*/\n/* TODO Protected Region 1: Implement this method */\n/*PROTECTED REGION END*/\n}\n\n\npublic void someOtherFunction {\n/*PROTECTED REGION ID(Person_Tester_2) ENABLED START*/\n/* TODO Protected Region 2: Implement this method */\n/*PROTECTED REGION END*/\n}\n\n}\n\n";
			String content = FileHelper.read (out.getPath() + "/Person.java");
			assertEquals (initalExpected, content);
		} catch (WorkflowInterruptedException e) {
			fail(e.getMessage());
		}

	}
    
    @Test
    public void testWithFileOutput() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::WithFileOutput", "iso-8859-1", mms, outlets );
		Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("element", "world");
		bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::WithFileOutput::WithFileOutput FOR element" + XpandTokens.RT, variables , null, null);
		
		File outFile = new File("out", "dummy.txt");
		assertTrue(outFile.exists());
		BufferedReader r = new BufferedReader(new FileReader(outFile));
		String line = null;
		StringBuffer buf = new StringBuffer();
		while ((line = r.readLine()) != null) {
			buf.append(line+"\n");
		}
		assertEquals("\n	Hello world: 5!\n	\n", buf.toString());
		r.close();
    }
    
}