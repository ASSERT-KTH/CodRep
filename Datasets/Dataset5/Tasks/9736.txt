return URI.create(PROTOCOL + "://" + getAuthority() + "/");

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

package org.eclipse.ecf.tests.discovery;

import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;

import junit.framework.TestCase;

public abstract class AbstractDiscoveryTest extends TestCase {
	protected final static String NAMINGAUTHORITY = "IANA";
	protected final static String SCOPE = "local";
	protected final static String PROTOCOL = "tcp";
	protected final static int PORT = 3282;

	protected final static String[] SERVICES = new String[] {"service", "ecf", "tests"};
	protected final static String SERVICE_TYPE = "_" + SERVICES[0] + "._" + SERVICES[1] + "._" + SERVICES[2] + "._" + PROTOCOL + "." + SCOPE + "._" + NAMINGAUTHORITY;
	
	public URI createDefaultURI() {
		return URI.create("foo://" + getAuthority() + "/");
	}
	
	private String getAuthority() {
		return System.getProperty("user.name") + "@" + getHost() + ":" + PORT;
	}
	
	protected static String getHost() {
		try {
			return InetAddress.getLocalHost().getHostAddress();
		} catch (UnknownHostException e) {
			e.printStackTrace();
			return "localhost";
		}
	}
}
 No newline at end of file