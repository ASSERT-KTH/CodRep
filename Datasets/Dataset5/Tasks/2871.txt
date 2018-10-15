Thread.sleep(3000);

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

package org.eclipse.ecf.tests.filetransfer;

import java.net.URL;

/**
 *
 */
public class URLBrowseTest extends AbstractBrowseTestCase {

	public URL[] testURLs = null;

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.filetransfer.AbstractBrowseTestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		testURLs = new URL[2];
		testURLs[0] = new URL("https://www.verisign.com/index.html");
		testURLs[1] = new URL("http://www.eclipse.org/ecf/ip_log.html");
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.filetransfer.AbstractBrowseTestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		testURLs = null;
	}

	public void testBrowseURLs() throws Exception {
		for (int i = 0; i < testURLs.length; i++) {
			testBrowse(testURLs[i]);
			Thread.sleep(1000);
		}
	}
}