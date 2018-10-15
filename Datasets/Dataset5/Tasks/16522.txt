public class NamespaceTest extends ECFAbstractTestCase {

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.tests.filetransfer;

import java.io.ByteArrayOutputStream;
import java.io.NotSerializableException;
import java.io.ObjectOutputStream;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.tests.ECFAbstractTestCase;

public class FileTransferNamespaceTest extends ECFAbstractTestCase {

	private Namespace fixture;
	
	/* (non-Javadoc)
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		fixture = IDFactory.getDefault().getNamespaceByName("ecf.provider.filetransfer");
		assertNotNull(fixture);
	}
	
	/* (non-Javadoc)
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		fixture = null;
	}

	public void testNamespaceGetScheme() {
		String scheme = fixture.getScheme();
		assertNotNull(scheme);
	}
	
	public void testNamespaceGetName() {
		String name = fixture.getName();
		assertNotNull(name);
		assertTrue(name.equals("ecf.provider.filetransfer"));
	}
	
	public final void testSerializable() throws Exception {
		ByteArrayOutputStream buf = new ByteArrayOutputStream();
		ObjectOutputStream out = new ObjectOutputStream(buf);
		try {
			out.writeObject(fixture);
		} catch (NotSerializableException ex) {
			fail(ex.getLocalizedMessage());
		} finally {
			out.close();
		}
	}
	
	public final void testCreateID() throws Exception {
		ID newID = IDFactory.getDefault().createID(fixture, "http://www.news.com");
		assertNotNull(newID);
	}
	
	public final void testGetSupportedSchemes() throws Exception {
		String [] supportedSchemes = fixture.getSupportedSchemes();
		assertNotNull(supportedSchemes);
	}

	/*
	public final void testGetURLConnection() throws Exception {
		
		FileIDFactory.getDefault();
		URL anURL = new URL("foobar:http://slewis@lala.lala.com:3333/foo/bar/lala.txt?artifact=one&group=two");
		
		System.out.println("protocol="+anURL.getProtocol());
		System.out.println("auth="+anURL.getAuthority());
		System.out.println("defport="+anURL.getDefaultPort());
		System.out.println("port="+anURL.getPort());
		System.out.println("host="+anURL.getHost());
		System.out.println("file="+anURL.getFile());
		System.out.println("path="+anURL.getPath());
		System.out.println("ref="+anURL.getRef());
		System.out.println("query="+anURL.getQuery());
		System.out.println("userinfo="+anURL.getUserInfo());
		System.out.println("externalform="+anURL.toExternalForm());
		System.out.println("tostring="+anURL.toString());
		
		URLConnection connection = anURL.openConnection();
		assertNotNull(connection);
		
	}
	*/
}
 No newline at end of file