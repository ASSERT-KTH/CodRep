public void testCreateServiceTypeIDWithProviderSpecificString() {

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.tests.provider.jmdns.identity;

import org.eclipse.ecf.tests.discovery.identity.ServiceIDTest;

/**
 *
 */
public class JMDNSServiceIDTest extends ServiceIDTest {

	public JMDNSServiceIDTest() {
		super("ecf.namespace.jmdns");
	}

	public void testJMDNSServiceTypeIDWithIPv6() {
		final String serviceType = "1.0.0.0.0.c.e.f.f.f.6.5.0.5.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa.";
		fail("Not implemented yet, don't know how to handle this service type " + serviceType + " if it even is one");
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.discovery.identity.ServiceIDTest#testCreateServiceTypeIDFromInternalString()
	 */
	public void testCreateServiceTypeIDFromInternalString() {
		final String internalRep = "_service._tcp.local";
		createIDFromString(internalRep);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.discovery.identity.ServiceIDTest#testCreateServiceTypeIDFromInternalString()
	 */
	public void testCreateServiceTypeIDFromInternalString2() {
		final String internalRep = "_service._tcp.ecf.eclipse.org";
		createIDFromString(internalRep);
	}
}