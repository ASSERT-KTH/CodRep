&& !allowedPackages.contains(obj))

/*******************************************************************************
 * Copyright (c) 2005 - 2009 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/

package org.eclipse.xtend.typesystem.xsd.tests.reloadschemas;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.emf.ecore.xml.type.XMLTypePackage;
import org.eclipse.emf.mwe.core.monitor.NullProgressMonitor;
import org.eclipse.xsd.XSDConcreteComponent;
import org.eclipse.xsd.XSDSchema;
import org.eclipse.xsd.XSDSchemaDirective;
import org.eclipse.xtend.typesystem.emf.EcoreUtil2;
import org.eclipse.xtend.typesystem.xsd.builder.OawXSDResource;
import org.eclipse.xtend.typesystem.xsd.builder.OawXSDResourceSet;
import org.eclipse.xtend.typesystem.xsd.builder.XSDManager;
import org.eclipse.xtend.typesystem.xsd.tests.AbstractTestCase;
import org.eclipse.xtend.typesystem.xsd.util.Msg;

/**
 * @author Moritz Eysholdt - Initial contribution
 */
public class ReloadSchemasTest extends AbstractTestCase {

	private final URI Ns1_A = uri("/Ns1-A.xsd");
	private final URI Ns1_B = uri("/Ns1-B.xsd");
	private final URI Ns1_C_AB = uri("/Ns1-C-AB.xsd");
	private final URI Ns2_K_C = uri("/Ns2-K-C.xsd");
	private final URI Ns2_L_K = uri("/Ns2-L-K.xsd");
	private final URI Ns3_M_C = uri("/Ns3-M-C.xsd");

	private void assertNoReferencesToPackage(XSDManager rs, EPackage p) {
		HashSet<EPackage> allowedPackages = new HashSet<EPackage>(rs
				.getPackages());
		assertFalse(allowedPackages.contains(p));
		allowedPackages.add(XMLTypePackage.eINSTANCE);
		for (EPackage s : rs.getPackages()) {
			assertNoReferencesToPackage(allowedPackages, s);
			TreeIterator<EObject> ti = s.eAllContents();
			while (ti.hasNext())
				assertNoReferencesToPackage(allowedPackages, ti.next());
		}
	}

	private void assertNoReferencesToPackage(Set<EPackage> allowedPackages,
			EObject obj) {
		for (EReference ref : obj.eClass().getEAllReferences()) {
			Object o = obj.eGet(ref);
			if (obj instanceof EPackage
					&& !allowedPackages.contains((EPackage) obj))
				fail2(Msg.create("Supplied object is a forbidden package:")
						.pkg((EPackage) obj));
			/*
			 * if (o instanceof EObject) { EObject eo = (EObject) o; if
			 * (eo.eResource() == null || eo.eResource().getURI() == null)
			 * fail2(Msg.create("").uri(obj).txt(": Resource is null:")
			 * .path(obj).txt("->").txt(ref.getName())); }
			 */
			if (o instanceof EClassifier) {
				EClassifier cc = (EClassifier) o;
				if (!allowedPackages.contains(cc.getEPackage()))
					fail2(Msg.create("Reference to ").pkg(cc.getEPackage())
							.txt(" found:").path(obj).txt("->").txt(
									ref.getName()));
			}
		}
	}

	private void assertNoReferencesToSchema(EObject obj, EReference ref,
			Object o, XSDSchema schema) {
		if (o instanceof EObject) {
			EObject eo = (EObject) o;
			if (eo.eResource() == null || eo.eResource().getURI() == null)
				fail2(Msg.create("").uri(obj).txt(": Resource is null:").path(
						obj).txt("->").txt(ref.getName()));
		}
		if (o instanceof XSDConcreteComponent) {
			XSDConcreteComponent cc = (XSDConcreteComponent) o;
			if (cc.getSchema() == schema)
				fail2(Msg.create("").uri(obj).txt(": Reference to ").schema(
						schema).txt(" found:").path(obj).txt("->").txt(
						ref.getName()));
		}
	}

	private void assertNoReferencesToSchema(OawXSDResourceSet rs,
			XSDSchema schema) {
		for (XSDSchema s : rs.getSchemas()) {
			assertNoReferencesToSchemaFromFeature(s, schema);
			TreeIterator<EObject> ti = s.eAllContents();
			for (XSDSchemaDirective ref : s.getReferencingDirectives())
				assertNoReferencesToSchemaFromFeature(ref, schema);
			while (ti.hasNext())
				assertNoReferencesToSchemaFromFeature(ti.next(), schema);
		}
	}

	private void assertNoReferencesToSchemaFromFeature(EObject obj,
			XSDSchema schema) {
		if (obj == schema)
			fail2(Msg.create("Supplied object is forbidden schema"));
		for (EReference ref : obj.eClass().getEAllReferences()) {
			Object o = obj.eGet(ref);
			if (o instanceof Collection)
				for (Object p : (Collection<?>) o)
					assertNoReferencesToSchema(obj, ref, p, schema);
			else
				assertNoReferencesToSchema(obj, ref, o, schema);
		}
	}

	private void assertSchemaLoaded(OawXSDResourceSet rs, URI uri,
			boolean expectEcore) {
		OawXSDResource r = rs.getXsdResource(uri, false);
		assertNotNull(r);
		assertTrue(r.isLoaded());
		assertEquals(expectEcore, r.isEcorePackageGenerated());
	}

	private void fail2(Msg msg) {
		System.out.println("Fail: " + msg);
	}

	private void reloadPackage(URI uri) {
		OawXSDResourceSet rs = new OawXSDResourceSet();
		rs.markDirty(Ns2_L_K);
		rs.reloadDirty(new NullProgressMonitor());
		OawXSDResource r = rs.getXsdResource(uri, false);
		EPackage p = r.getEPackage();
		XSDSchema s = r.getSchema();
		rs.markDirty(uri);
		rs.reloadDirty(new NullProgressMonitor());
		assertSchemaLoaded(rs, uri, true);
		assertNoReferencesToPackage(rs, p);
		assertNoReferencesToSchema(rs, s);
	}

	public void testLoadAll() {
		OawXSDResourceSet rs = new OawXSDResourceSet();
		rs.markDirty(Ns2_L_K);
		rs.markDirty(Ns1_C_AB);
		rs.reloadDirty(new NullProgressMonitor());
		assertSchemaLoaded(rs, Ns1_A, false);
		assertSchemaLoaded(rs, Ns1_B, false);
		assertSchemaLoaded(rs, Ns1_C_AB, true);
		assertSchemaLoaded(rs, Ns2_K_C, false);
		assertSchemaLoaded(rs, Ns2_L_K, true);
	}

	public void testReloadPackageA() {
		reloadPackage(Ns1_A);
	}

	public void testReloadPackageB() {
		reloadPackage(Ns1_B);
	}

	public void testReloadPackageCAB() {
		reloadPackage(Ns1_C_AB);
	}

	public void testReloadPackageKC() {
		reloadPackage(Ns2_K_C);
	}

	public void testReloadPackageLK() {
		reloadPackage(Ns2_L_K);
	}

	public void testRemove() {
		OawXSDResourceSet rs = new OawXSDResourceSet();
		rs.loadAndGenerate(Ns2_L_K);
		OawXSDResource r = rs.getXsdResource(Ns2_L_K, false);
		XSDSchema s = r.getSchema();
		EPackage p = r.getEPackage();
		rs.remove(Ns2_L_K);
		assertNoReferencesToSchema(rs, s);
		assertNoReferencesToPackage(rs, p);
		assertNull(rs.getXsdResource(Ns2_L_K, false));
	}

	public void testUnloadRootPackage() {
		OawXSDResourceSet rs = new OawXSDResourceSet();
		rs.markDirty(Ns2_L_K);
		rs.reloadDirty(new NullProgressMonitor());
		OawXSDResource r = rs.getXsdResource(Ns2_L_K, false);
		EPackage p = r.getEPackage();
		r.unload();
		assertNoReferencesToPackage(rs, p);
	}

	public void testUnloadRootSchema() {
		OawXSDResourceSet rs = new OawXSDResourceSet();
		rs.markDirty(Ns2_L_K);
		rs.reloadDirty(new NullProgressMonitor());
		OawXSDResource r = rs.getXsdResource(Ns2_L_K, false);
		XSDSchema s = r.getSchema();
		r.unload();
		assertNoReferencesToSchema(rs, s);
	}

	private URI uri(String file) {
		return EcoreUtil2.getURI(getSrcDir() + file);
	}

	public void testLoadIncludes() {
		// usually included schemas are not loaded if there is no element that
		// references them. bit the OawXSDResourceSet is supposed to load them
		// anyway.
		OawXSDResourceSet rs = new OawXSDResourceSet();
		rs.markDirty(Ns3_M_C);
		rs.reloadDirty(new NullProgressMonitor());
	}

}