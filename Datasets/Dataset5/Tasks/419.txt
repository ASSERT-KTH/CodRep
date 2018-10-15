package org.eclipse.ecf.tests.provider.xmpp;

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
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
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;

/**
 *
 */
public class IDCreateTest extends TestCase {

	public static final String XMPP_NAMESPACE = "ecf.xmpp";

	Namespace namespace;

	protected void setUp() throws Exception {
		namespace = IDFactory.getDefault().getNamespaceByName(XMPP_NAMESPACE);
		assertNotNull(namespace);
	}

	public void testXMPPCreateID() throws Exception {
		final ID xmppID = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org");
		assertNotNull(xmppID);
	}

	public void testXMPPCreateID1() throws Exception {
		try {
			IDFactory.getDefault().createID(namespace, "ecf.eclipse.org");
			fail();
		} catch (final IDCreateException e) {
			// this construction should fail
		}
	}

	public void testXMPPCreateID2() throws Exception {
		final ID xmppID = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333");
		assertNotNull(xmppID);
	}

	public void testXMPPCreateID3() throws Exception {
		final ID xmppID = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org:5333/myresource");
		assertNotNull(xmppID);
	}

	public void testXMPPCreateID4() throws Exception {
		final ID xmppID = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org/myresource");
		assertNotNull(xmppID);
	}

	public void testXMPPCreateID5() throws Exception {
		final ID xmppID = IDFactory.getDefault().createID(namespace, "foobar@ecf.eclipse.org/myresource/subresource");
		assertNotNull(xmppID);
	}

}