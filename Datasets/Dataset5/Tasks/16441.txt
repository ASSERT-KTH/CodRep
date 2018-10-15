XtendFacade facade = XtendFacade.create(ec);

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

package org.eclipse.xtend;

import java.io.StringReader;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import junit.framework.TestCase;

import org.eclipse.internal.xtend.type.impl.java.JavaMetaModel;
import org.eclipse.internal.xtend.type.impl.java.beans.JavaBeansStrategy;
import org.eclipse.internal.xtend.xtend.ast.Extension;
import org.eclipse.internal.xtend.xtend.ast.ExtensionFile;
import org.eclipse.internal.xtend.xtend.parser.ParseFacade;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.typesystem.javabeansimpl.test.TypeA;
import org.eclipse.xtend.typesystem.javabeansimpl.test.TypeB;

public class ExtensionEvaluationTest extends TestCase {

	private ExecutionContextImpl ec;

	@Override
	protected void setUp() throws Exception {
		ec = new ExecutionContextImpl();
		ec.registerMetaModel(new JavaMetaModel("asdf", new JavaBeansStrategy()));
	}

	private ExtensionFile parse(final String expression) {
		return ParseFacade.file(new StringReader(expression), "nofile");
	}
	
	public void testVoidInSignature() throws Exception {
		final ExtensionFile file = parse(
				"foo(String str) : 'String';" +
				"foo(Integer int) : 'Int';" +
				"foo(Void void) : 'void';");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		XtendFacade facade = new XtendFacade(ec);
		assertEquals("String",facade.call("foo", "String"));
		assertEquals("Int",facade.call("foo", new Long(42)));
		assertEquals("void",facade.call("foo", (Object) null));
	}

	public final void testWithEverything() {
		final ExtensionFile file = parse("String toUpperCase(String str) : JAVA org.eclipse.xtend.Helper.toUpperCase(java.lang.String) ; \n"
				+ "\n"
				+ "String privateHelper(String str) : JAVA org.eclipse.xtend.Helper.privateHelper(java.lang.String) ; \n"
				+ "\n"
				+ "String nonStaticHelper(String str) : JAVA org.eclipse.xtend.Helper.nonStaticHelper(java.lang.String) ; \n"
				+ "\n" + "/* \n" + " * Meine Funktion \n" + " */ \n" + "myExtension(Object val) : {val} ; \n");

		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		final Object[] params = new Object[] { "test" };
		Extension ext = ec.getExtension("toUpperCase", params);
		assertEquals("TEST", ext.evaluate(params, ec));

		ext = ec.getExtension("myExtension", params);
		assertEquals(Collections.singletonList("test"), ext.evaluate(params, ec));
	}

	public final void testJavaExtension2() {
		final ExtensionFile file = parse("Collection union(Collection c1,Collection c2) : JAVA "
				+ "org.eclipse.xtend.Helper.union(java.util.Collection,java.util.Collection) ; \n");

		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		final Object[] params = new Object[] { Collections.singleton("1"), Collections.singleton("2") };
		final Extension ext = ec.getExtension("union", params);
		final Collection<?> result = (Collection<?>) ext.evaluate(params, ec);
		assertTrue(result.size() == 2);
		assertTrue(result.contains("1"));
		assertTrue(result.contains("2"));
	}

	public final void testPolymorphism() {
		final ExtensionFile file = parse("ext(Object val) : 'Object' ; \n" + "ext(List[Object] val) : 'List' ; \n"
				+ "ext(Collection[Object] val) : 'Collection' ; \n" + "ext(Integer val) : 'Integer' ; \n");

		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		Extension ext = ec.getExtension("ext", new Object[] { "test" });
		assertEquals("Object", ext.evaluate(new Object[] { "test" }, ec));

		ext = ec.getExtension("ext", new Object[] { Collections.EMPTY_SET });
		assertEquals("Collection", ext.evaluate(new Object[] { Collections.EMPTY_SET }, ec));

		ext = ec.getExtension("ext", new Object[] { Collections.EMPTY_LIST });
		assertEquals("List", ext.evaluate(new Object[] { Collections.EMPTY_LIST }, ec));

		ext = ec.getExtension("ext", new Object[] { new Integer(2) });
		assertEquals("Integer", ext.evaluate(new Object[] { new Integer(2) }, ec));

	}

	public final void testRecursion() {
		final ExtensionFile file = parse("List[Integer] recExtension(Integer von,Integer bis) : von>=bis ? {von} : recExtension(von,bis-1).add(bis) ; \n");

		ec = (ExecutionContextImpl) ec.cloneWithResource(file);

		final Extension ext = ec.getExtension("recExtension", new Object[] { new BigInteger("5"), new BigInteger("10") });
		final List<BigInteger> expected = new ArrayList<BigInteger>();
		for (int i = 5; i <= 10; i++) {
			expected.add(new BigInteger(""+i));
		}
		final Object evalResult = ext.evaluate(new Object[] { new BigInteger("5"), new BigInteger("10") }, ec);
		assertEquals(expected, evalResult);

	}

	public final void testMemberPosition() {
		final ExtensionFile file = parse("ext1(String txt) : 'test'+txt ;" + "ext2(String txt) : txt.ext1() ;");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);

		final Extension ext = ec.getExtension("ext2", new Object[] { "fall" });
		final Object evalResult = ext.evaluate(new Object[] { "fall" }, ec);
		assertEquals("testfall", evalResult);

	}

	public final void testCachedExtension() {
		final ExtensionFile file = parse("cached String ext(String txt) : JAVA org.eclipse.xtend.ExtensionEvaluationTest.testMethod(java.lang.String);");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);

		final Extension ext = ec.getExtension("ext", new Object[] { "test" });
		String expected = "test" + String.valueOf(magic);
		assertEquals(expected, ext.evaluate(new Object[] { "test" }, ec));
		assertEquals(expected, ext.evaluate(new Object[] { "test" }, ec));
		assertEquals(expected, ext.evaluate(new Object[] { "test" }, ec));
		assertEquals(expected, ext.evaluate(new Object[] { "test" }, ec));
	}

	private static int magic = 0;

	public final static String testMethod(final String s) {
		return s + magic++;
	}

	public final void testCreateExtension() {
		final ExtensionFile file = parse("create List l test(String s) : l.add(s) ;");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		final List<?> l = (List<?>) (file.getExtensions().get(0)).evaluate(new String[] { "test" }, ec);

		assertEquals(Collections.singletonList("test"), l);
	}

	public final void testCreateExtension1() {
		final ExtensionFile file = parse("create List test(String s) : add(s) ;");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		final List<?> l = (List<?>) (file.getExtensions().get(0)).evaluate(new String[] { "test" }, ec);

		assertEquals(Collections.singletonList("test"), l);
	}

	public final void testAmbigous() {
		final ExtensionFile file = parse("import " + TypeA.class.getPackage().getName().replaceAll("\\.", "::") + ";"
				+ "doStuff(TypeA this) : true; " + "doStuff(TypeC this) : false;");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		assertNotNull(ec.getExtension("doStuff", new Object[] { new TypeA() }));
		try {
			ec.getExtension("doStuff", new Object[] { new TypeB() });
			fail("Ambigous operation exception expected");
		}
		catch (final RuntimeException re) {
			// expected
			System.out.println(re.getMessage());
		}
	}

	public final void testBug134626() {
		final ExtensionFile file = parse("String someExt(TestA someA) : JAVA " + getClass().getName()
				+ "(java.lang.String) ; \n");

		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
	}

	public static String methodForBug134626() {
		return "Hello";
	}

	public void testAdvices() throws Exception {
		final ExtensionFile file = parse("doStuff() : '_THE_'; " + "doStuff(String s) : s;");
		ec = (ExecutionContextImpl) ec.cloneWithResource(file);
		ec.registerExtensionAdvices("org::eclipse::xtend::Advices");

		assertEquals("AROUND_THE_END", call(ec, "doStuff"));
		assertEquals("AROUNDAROUND_HONK_ENDEND", call(ec, "doStuff", "_HONK_"));

	}

	private Object call(ExecutionContextImpl ctx, String string, Object... params) {
		Extension ext = ctx.getExtension(string, params);
		return ext.evaluate(params, ctx);
	}

}