waitForDone(10000);

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

package org.eclipse.ecf.tests.filetransfer;

import java.io.File;

/**
 *
 */
public class FileSendTest extends AbstractSendTestCase {

	File inputFile = null;
	File outputFile = null;

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.filetransfer.AbstractSendTestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		inputFile = new File("test.txt");
		outputFile = File.createTempFile("ECFTest", "test.txt");
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.filetransfer.AbstractSendTestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		inputFile = null;
		outputFile = null;
	}

	public void testSend() throws Exception {
		testSendForFile(outputFile.toURL(), inputFile);
		waitForDone(5000);
		assertEquals(outputFile.length(), inputFile.length());
	}
}