outputFile = File.createTempFile("ECFTest", "").toURL();

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

package org.eclipse.ecf.tests.provider.filetransfer.efs;

import java.io.File;
import java.net.URL;

import org.eclipse.ecf.tests.filetransfer.AbstractSendTestCase;

public class SendTest extends AbstractSendTestCase {

	File inputFile = null;
	URL outputFile = null;

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.filetransfer.AbstractSendTestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		inputFile = new File("test.txt");
		outputFile = new URL("efs:file://c:/ECFtest.txt");
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
		testSendForFile(outputFile, inputFile);
		waitForDone(5000);
	}
}