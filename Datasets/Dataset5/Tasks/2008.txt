EObject oxml = XMLReaderImpl.read(xml, mm, false);

/*******************************************************************************
 * Copyright (c) 2005 - 2009 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/

package org.eclipse.xtend.typesystem.xsd.tests.featuremap;

import java.util.Collection;
import java.util.Collections;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.xtend.expression.ExecutionContextImpl;
import org.eclipse.xtend.expression.ExpressionFacade;
import org.eclipse.xtend.expression.Variable;
import org.eclipse.xtend.typesystem.xsd.XMLReaderImpl;
import org.eclipse.xtend.typesystem.xsd.XSDMetaModel;
import org.eclipse.xtend.typesystem.xsd.tests.AbstractTestCase;
import org.eclipse.xtend.typesystem.xsd.type.EFeatureMapEntryTypeImpl;
import org.eclipse.xtend.typesystem.xsd.type.EFeatureMapTypeImpl;
import org.eclipse.xtend.typesystem.xsd.type.EFeatureType;
import org.eclipse.xtend.typesystem.xsd.type.XMLEClassType;
import org.eclipse.xtend.typesystem.xsd.type.XMLFeatureMapTypeImpl;

/**
 * @author Moritz Eysholdt - Initial contribution
 */
public class FeatureMapTest extends AbstractTestCase {

	private ExpressionFacade ec;

	private Object def(String varname, String exp) {
		Object o = ec.evaluate(exp);
		ec = ec.cloneWithVariable(new Variable(varname, o));
		return o;
	}

	@Override
	protected void setUp() throws Exception {
		super.setUp();
		String xsd = getSrcDir() + "/FeatureMap.xsd";
		String xml = getSrcDir() + "/FeatureMap.xml";
		XSDMetaModel mm = new XSDMetaModel();
		mm.setId("mm");
		mm.addSchemaFile(xsd);
		ExecutionContextImpl ctx = new ExecutionContextImpl();
		ctx.registerMetaModel(mm);
		ec = new ExpressionFacade(ctx);
		EObject oxml = XMLReaderImpl.read(xml, "mm", false);
		ec = ec.cloneWithVariable(new Variable("xml", oxml));
	}

	public void testAdd1() {
		Object ele1 = def("ele1", "featureMap::ClassAny.newInstance()");
		def("obj", "featureMap::ClassMixed.newInstance()");
		def("fele1", "featureMap::ClassMixed::elementAny");
		ec.evaluate("obj.mixed.add(fele1,ele1)");
		assertEquals(ele1, ec.evaluate("obj.elementAny"));
	}

	public void testAdd2() {
		Object ele1 = def("ele1", "'mystring'");
		def("obj", "featureMap::ClassMixed.newInstance()");
		def("fele1", "featureMap::ClassMixed::element1");
		ec.evaluate("obj.mixed.add(fele1,ele1)");
		assertEquals(ele1, ec.evaluate("obj.element1.get(0)"));
	}

	public void testAddAllAndList() {
		Object ele1 = def("ele1", "{'mystring1','mystring2'}");
		def("obj", "featureMap::ClassMixed.newInstance()");
		def("fele1", "featureMap::ClassMixed::element1");
		ec.evaluate("obj.mixed.addAll(fele1,ele1)");
		assertEquals(ele1, ec.evaluate("obj.element1"));
		assertEquals(ele1, ec.evaluate("obj.mixed.list(fele1)"));
	}

	public void testAddAllToMixed() {
		def("obj", "featureMap::ClassMixed.newInstance()");
		ec.evaluate("obj.setAttr1('mystring1')");
		ec.evaluate("obj.element1.add('mystring2')");
		def("m", "featureMap::ClassMixed.newInstance()");
		ec.evaluate("m.mixed.addFrom(obj)");
		assertEquals(Collections.singletonList("mystring2"), ec
				.evaluate("m.mixed.value"));
	}

	public void testAddAttributeToAnyAttribute() {
		def("obj", "featureMap::ClassMixed.newInstance()");
		ec.evaluate("obj.setAttr1('mystring1')");
		ec.evaluate("obj.element1.add('mystring2')");
		def("any", "featureMap::ClassAnyAttribute.newInstance()");
		ec.evaluate("any.anyAttribute.addFrom(obj)");
		assertEquals(Collections.singletonList("mystring1"), ec
				.evaluate("any.anyAttribute.value"));
	}

	public void testAddElementToAny() {
		def("obj", "featureMap::ClassMixed.newInstance()");
		ec.evaluate("obj.setAttr1('mystring1')");
		ec.evaluate("obj.element1.add('mystring2')");
		def("a", "featureMap::ClassAny.newInstance()");
		ec.evaluate("a.any.addFrom(obj)");
		assertEquals(Collections.singletonList("mystring2"), ec
				.evaluate("a.any.value"));
	}

	public void testClassFeature() {
		Object o = ec.evaluate("featureMap::ClassMixed::element1.metaType");
		assertInstanceOf(o, EFeatureType.class);
	}

	public void testClassType() {
		Object o = ec.evaluate("featureMap::ClassMixed");
		assertInstanceOf(o, XMLEClassType.class);
		System.out.println(o.getClass());
	}

	@SuppressWarnings("unchecked")
	public void testElementFeature() {
		Collection c = (Collection) ec
				.evaluate("xml.mixed.collect(e|e.feature.metaType)");
		for (Object o : c)
			assertInstanceOf(o, EFeatureType.class);
	}

	@SuppressWarnings("unchecked")
	public void testElementType() {
		Collection c = (Collection) ec
				.evaluate("xml.mixed.collect(e|e.metaType)");
		for (Object o : c)
			assertInstanceOf(o, EFeatureMapEntryTypeImpl.class);
	}

	public void testMapEntryName() {
		Object o = ec.evaluate("EFeatureMapEntry");
		assertInstanceOf(o, EFeatureMapEntryTypeImpl.class);
	}

	public void testMapName() {
		Object o = ec.evaluate("XMLFeatureMap");
		assertInstanceOf(o, XMLFeatureMapTypeImpl.class);
	}

	public void testMapType() {
		Object o = ec.evaluate("xml.mixed.metaType");
		assertInstanceOf(o, EFeatureMapTypeImpl.class);
	}

	public void testSet() {
		Object ele2 = def("ele2", "'mystring'");
		def("obj", "featureMap::ClassMixed.newInstance()");
		def("fele2", "featureMap::ClassMixed::element2");
		assertFalse(ec.evaluate("obj.mixed.isSet(fele2)"));
		ec.evaluate("obj.mixed.set(fele2,ele2)");
		assertTrue(ec.evaluate("obj.mixed.isSet(fele2)"));
		assertEquals(ele2, ec.evaluate("obj.element2"));
		ec.evaluate("obj.mixed.unset(fele2)");
		assertFalse(ec.evaluate("obj.mixed.isSet(fele2)"));
	}
}