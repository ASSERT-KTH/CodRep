import org.eclipse.internal.xpand2.XpandTokens;

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

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.internal.xpand2.codeassist.XpandTokens;
import org.eclipse.xpand2.output.Outlet;
import org.eclipse.xtend.backend.util.FileHelper;
import org.eclipse.xtend.middleend.xpand.XpandBackendFacade;
import org.eclipse.xtend.middleend.xpand.internal.xpandlib.pr.XpandProtectedRegionResolver;
import org.eclipse.xtend.type.impl.java.JavaBeansMetaModel;
import org.eclipse.xtend.typesystem.MetaModel;
import org.junit.Test;

/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 * @author André Arnold
 *
 */
@SuppressWarnings("restriction")
public class XpandStatementTest {

	
	@Test
	public void testIf() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		
		variables.put("element", "one");
		Object res1 = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testIf FOR element" + XpandTokens.RT, variables , null, null);
		assertEquals("\n\nfirst: one\n\n", res1.toString());
		
		variables.put("element", "two");
		Object res2 = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testIf FOR element" + XpandTokens.RT, variables , null, null);
		assertEquals("\n\ntwo\n\n", res2.toString());

		variables.put("element", "three");
		Object res3 = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testIf FOR element" + XpandTokens.RT, variables , null, null);
		assertEquals("\n\nlast: three\n\n", res3.toString());
	}
	
	@Test
	public void testForeach() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("elements", Arrays.asList("one", "two" , "three"));
		Object o = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testForeach FOR elements" + XpandTokens.RT, variables , null, null);
		
		assertEquals("\n\nelement: one\n\nelement: two\n\nelement: three\n\n", o.toString());
	}
	
	@Test
	public void testForeachWithSeparator() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("elements", Arrays.asList("one", "two" , "three"));
		Object o = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testForeachWithSeparator FOR elements" + XpandTokens.RT, variables , null, null);
		
		assertEquals("\n\nelement: one\n,\nelement: two\n,\nelement: three\n\n", o.toString());
	}
	
	@Test
	public void testForeachWithSeparatorAndDelLine() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("elements", Arrays.asList("one", "two" , "three"));
		bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testForeachWithSeparatorAndDelLine FOR elements" + XpandTokens.RT, variables , null, null);
		
		File outFile = new File("out", "output.txt");
		assertTrue(outFile.exists());
		BufferedReader r = new BufferedReader(new FileReader(outFile));
		String line = null;
		StringBuffer buf = new StringBuffer();
		while ((line = r.readLine()) != null) {
			buf.append(line+"\n");
		}
		assertEquals("element: one,element: two,element: three\n", buf.toString());
		r.close();
		outFile.delete();
	}
	
	@Test
	public void testForeachWithIterator() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("elements", Arrays.asList("one", "two" , "three" , "four"));
		Object o = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testForeachWithIterator FOR elements" + XpandTokens.RT, variables , null, null);
		
		assertEquals("\n\n\nfirst: one 4\n\n,\n\ntwo 1 2\n\n,\n\nthree 2 3\n\n,\n\nlast: four\n\n\n", o.toString());
	}
	
	@Test
	public void testLet() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
        Person p = new Person();
        p.setName("Tester");
        p.setFirstName("Testerossa");
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("element", p);
		Object o = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testLet FOR element" + XpandTokens.RT, variables , null, null);
		
		assertEquals("\n\nTester\n\n", o.toString());
	}
	
	@Test
	public void testRem() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out");
        Collection<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
		
        XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("element", "one");
		Object o = bf.executeStatement(XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandStatements::testRem FOR element" + XpandTokens.RT, variables , null, null);
		
		assertEquals("\n\none\n", o.toString());
	}
	
	@Test
	public void testProtect() throws Exception {
        final List<MetaModel> mms = new ArrayList<MetaModel> ();
        mms.add (new JavaBeansMetaModel ());
        Outlet out = new Outlet("out3");
        List<Outlet> outlets = new ArrayList<Outlet>();
        outlets.add(out);
        Person p = new Person();
        p.setName("Tester");
        p.setFirstName("Testerossa");
		
		
		File generatedFile = new File (out.getPath() + "/Person.java");
		if (generatedFile.exists ())
			generatedFile.delete ();

		XpandBackendFacade bf = XpandBackendFacade.createForFile("org::eclipse::xtend::middleend::xpand::test::XpandStatements", "iso-8859-1", mms, outlets );
		final Map<String, Object> variables = new HashMap<String, Object>();
		variables.put("element", p);
		XpandProtectedRegionResolver resolver1 = new XpandProtectedRegionResolver(null, true, outlets, "ISO-8859-1", false);
		
		bf.executeStatement (XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandProtectedRegions::testProtect FOR element" + XpandTokens.RT, variables , null, resolver1);
		
		final String initalExpected = "\npackage org.eclipse.xtend.middleend.xpand.test;\n\npublic class Person {\n\npublic void someOperation {\n/*PROTECTED REGION ID(Person_Tester_1) ENABLED START*/\n/* TODO Protected Region 1: Implement this method */\n/*PROTECTED REGION END*/\n}\n\n\npublic void someOtherFunction {\n/*PROTECTED REGION ID(Person_Tester_2) ENABLED START*/\n/* TODO Protected Region 2: Implement this method */\n/*PROTECTED REGION END*/\n}\n\n}\n\n";
		final String modifiedExpected = "\npackage org.eclipse.xtend.middleend.xpand.test;\n\npublic class Person {\n\npublic void someOperation {\n/*PROTECTED REGION ID(Person_Tester_1) ENABLED START*/\n/* TODO Protected Region 1: Implement this method */\nString value1 = \"value1\"\n/*PROTECTED REGION END*/\n}\n\n\npublic void someOtherFunction {\n/*PROTECTED REGION ID(Person_Tester_2) ENABLED START*/\n/* TODO Protected Region 2: Implement this method */\nString value2 = \"value2\"\n/*PROTECTED REGION END*/\n}\n\n}\n\n";
		String content = FileHelper.read (out.getPath() + "/Person.java");
		assertEquals (initalExpected, content);
		
		FileHelper.write (out.getPath() + "/Person.java", modifiedExpected);
		assertEquals (modifiedExpected, FileHelper.read (out.getPath() + "/Person.java"));

		XpandProtectedRegionResolver resolver2 = new XpandProtectedRegionResolver(null, true, outlets, "ISO-8859-1", false);
		bf.executeStatement (XpandTokens.LT + "EXPAND org::eclipse::xtend::middleend::xpand::test::XpandProtectedRegions::testProtect FOR element" + XpandTokens.RT, variables , null, resolver2);
		String modifiedContent = FileHelper.read (out.getPath() + "/Person.java");
		assertEquals(modifiedExpected, modifiedContent);
	}

}