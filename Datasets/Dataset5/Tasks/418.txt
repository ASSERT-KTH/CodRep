package org.eclipse.ecf.tests.provider.xmpp;

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.ecllpse.ecf.tests.provider.xmpp;

import junit.framework.TestCase;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.presence.IFQID;

/**
 *
 */
public class FQIDTest extends TestCase {

	public static final String XMPP_NAMESPACE = "ecf.xmpp";

	Namespace namespace;
	ID id1;
	ID id2;
	ID id3;

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		namespace = IDFactory.getDefault().getNamespaceByName(XMPP_NAMESPACE);
		assertNotNull(namespace);
		id1 = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333/myresource");
		id2 = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333");
		id3 = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org");
	}

	public void testFQID() throws Exception {
		final ID local = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333/myresource");
		assertNotNull(local);
		final IFQID localfqid = (IFQID) local.getAdapter(IFQID.class);
		assertNotNull(localfqid);
		assertNotNull(localfqid.getFQName());
		assertNotNull(localfqid.getResourceName());
	}

	public void testFQID1() throws Exception {
		final ID local = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333/myresource");
		assertNotNull(local);
		final IFQID localfqid = (IFQID) local.getAdapter(IFQID.class);
		assertNotNull(localfqid);
		assertNotNull(localfqid.getFQName());
		assertNotNull(localfqid.getResourceName());

		final IFQID idfqid = (IFQID) id1.getAdapter(IFQID.class);
		assertTrue(local.equals(id1));
		assertTrue(localfqid.getFQName().equals(idfqid.getFQName()));
		assertTrue(localfqid.getResourceName().equals(idfqid.getResourceName()));
	}

	public void testFQID2() throws Exception {
		final ID local = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333/myresource");
		assertNotNull(local);
		final IFQID localfqid = (IFQID) local.getAdapter(IFQID.class);
		assertNotNull(localfqid);
		assertNotNull(localfqid.getFQName());
		assertNotNull(localfqid.getResourceName());

		final IFQID idfqid = (IFQID) id2.getAdapter(IFQID.class);
		assertTrue(!localfqid.getFQName().equals(idfqid.getFQName()));
		assertTrue(!localfqid.getResourceName().equals(idfqid.getResourceName()));
	}

	public void testFQID3() throws Exception {
		final ID local = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333/myresource");
		assertNotNull(local);
		final IFQID localfqid = (IFQID) local.getAdapter(IFQID.class);
		assertNotNull(localfqid);
		assertNotNull(localfqid.getFQName());
		assertNotNull(localfqid.getResourceName());

		final IFQID idfqid = (IFQID) id3.getAdapter(IFQID.class);
		assertTrue(!local.equals(id3));
		assertTrue(!localfqid.getFQName().equals(idfqid.getFQName()));
		assertTrue(!localfqid.getResourceName().equals(idfqid.getResourceName()));
	}

}