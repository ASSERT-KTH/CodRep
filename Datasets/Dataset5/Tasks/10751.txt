assertNotNull(fixture.removeNamespace(namespace));

/*******************************************************************************
 * Copyright (c) 2010 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.tests.core.identity;

import java.util.List;

import org.eclipse.ecf.core.identity.GUID;
import org.eclipse.ecf.core.identity.IIDFactory;
import org.eclipse.ecf.core.identity.LongID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.StringID;

public abstract class IIDNamespaceTest extends NamespaceTest {

	IIDFactory fixture = null;

	/*
	 * (non-Javadoc)
	 *
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		fixture = null;
		assertNull(fixture);
	}

	public void testIDFactoryGetNamespaces() {
		List namespaces = fixture.getNamespaces();
		assertNotNull(namespaces);
		assertTrue(namespaces.size() > 0);
	}

	public void testIDFactoryGetStringIDNamespaceByName() {
		Namespace namespace = fixture.getNamespaceByName(StringID.class
				.getName());
		assertNotNull(namespace);
	}

	public void testIDFactoryGetGUIDIDNamespaceByName() {
		Namespace namespace = fixture.getNamespaceByName(GUID.class.getName());
		assertNotNull(namespace);
	}

	public void testIDFactoryGetLongIDNamespaceByName() {
		Namespace namespace = fixture
				.getNamespaceByName(LongID.class.getName());
		assertNotNull(namespace);
	}

	public void testIDFactoryAddNamespace() {
		Namespace namespace = createNamespace();
		int currentSize = fixture.getNamespaces().size();
		Namespace ns = fixture.addNamespace(namespace);
		assertNull(ns);
		assertTrue(fixture.getNamespaces().size() == (currentSize + 1));
		fixture.removeNamespace(namespace);
	}

	public void testIDFactoryRemoveNamespace() {
		Namespace namespace = fixture.getNamespaceByName(StringID.class
				.getName());
		int currentSize = fixture.getNamespaces().size();
		Namespace removed = fixture.removeNamespace(namespace);
		assertNotNull(removed);
		assertTrue(fixture.getNamespaces().size() == (currentSize - 1));
		// Put it back
		fixture.addNamespace(removed);
	}
}