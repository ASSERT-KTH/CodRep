protected final static String[] SERVICES = new String[] {"ecf", "junit", "tests"};

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
	protected final static String USERNAME = System.getProperty("user.name", "testuser");
	protected final static String PASSWORD = "testpassword";
	protected final static String PATH = "/a/Path/to/Something";
	protected final static String QUERY = "someQuery";
	protected final static String FRAGMENT = "aFragment";

	protected final static String[] SERVICES = new String[] {"service", "ecf", "tests"};
	protected final static String SERVICE_TYPE = "_" + SERVICES[0] + "._" + SERVICES[1] + "._" + SERVICES[2] + "._" + PROTOCOL + "." + SCOPE + "._" + NAMINGAUTHORITY;
	
	public URI createDefaultURI() {
//TODO-mkuppe https://bugs.eclipse.org/216944
//		return URI.create(PROTOCOL + "://" + USERNAME + ":" + PASSWORD + "@" + getHost() + ":" + PORT + "/" + PATH + "?" + QUERY + "#" + FRAGMENT);
		return URI.create(PROTOCOL + "://" + USERNAME + "@" + getHost() + ":" + PORT + PATH);
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