return URI.create(PROTOCOLS[0] + "://"/* + USERNAME + "@" */+ getHost() + ":" + PORT + PATH);

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

public abstract class DiscoveryTestHelper {
	public final static int WEIGHT = 43;
	public final static int PRIORITY = 42;
	public final static String SERVICENAME = "aServiceNAME";
	public final static String NAMINGAUTHORITY = "someNamingAuthority";
	public final static String SCOPE = "someScope";
	public final static String PROTOCOL = "someProtocol";
	public final static int PORT = 3282;
	public final static String USERNAME = System.getProperty("user.name", "testuser");
	public final static String PASSWORD = "testpassword";
	public final static String PATH = "/a/Path/to/Something";
	public final static String QUERY = "someQuery";
	public final static String FRAGMENT = "aFragment";

	public final static String[] SERVICES = new String[] {"ecf", "junit", "tests"};
	public final static String[] PROTOCOLS = new String[] {PROTOCOL};
	public final static String SERVICE_TYPE = "_" + SERVICES[0] + "._" + SERVICES[1] + "._" + SERVICES[2] + "._" + PROTOCOL + "." + SCOPE + "._" + NAMINGAUTHORITY;
	
	public static URI createDefaultURI() {
//TODO-mkuppe https://bugs.eclipse.org/216944
//		return URI.create(PROTOCOL + "://" + USERNAME + ":" + PASSWORD + "@" + getHost() + ":" + PORT + "/" + PATH + "?" + QUERY + "#" + FRAGMENT);
		return URI.create(PROTOCOLS[0] + "://" + USERNAME + "@" + getHost() + ":" + PORT + PATH);
	}
	
	public static String getHost() {
		try {
			return InetAddress.getLocalHost().getHostAddress();
		} catch (UnknownHostException e) {
			e.printStackTrace();
			return "localhost";
		}
	}
}
 No newline at end of file