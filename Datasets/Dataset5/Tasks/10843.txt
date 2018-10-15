"http://download.eclipse.org/eclipse/updates/3.4/plugins/javax.servlet.jsp_2.0.0.v200806031607.jar.pack.gz",

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

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URL;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDataEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.equinox.internal.p2.artifact.repository.ECFTransport;

public class URLRetrieveTest extends AbstractRetrieveTestCase {

	private static final String HTTP_RETRIEVE = "http://www.eclipse.org/ecf/ip_log.html";
	protected static final String HTTPS_RETRIEVE = "https://www.verisign.com";
	private static final String HTTP_404_FAIL_RETRIEVE = "http://www.google.com/googleliciousafdasdfasdfasdf";

	private static final String FTP_RETRIEVE = "ftp://ftp.osuosl.org/pub/eclipse/rt/ecf/org.eclipse.ecf.examples-1.0.3.v20070927-1821.zip";
	
	// See bug 237936
	private static final String BUG_237936_URL = "http://www.eclipse.org/downloads/download.php?file=/webtools/updates/site.xml&format=xml&countryCode=us&timeZone=-5&responseType=xml";

	File tmpFile = null;

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		tmpFile = File.createTempFile("ECFTest", "");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		if (tmpFile != null)
			tmpFile.delete();
		tmpFile = null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.tests.filetransfer.AbstractRetrieveTestCase#handleStartEvent(org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent)
	 */
	protected void handleStartEvent(IIncomingFileTransferReceiveStartEvent event) {
		super.handleStartEvent(event);
		assertNotNull(event.getFileID());
		assertNotNull(event.getFileID().getFilename());
		try {
			incomingFileTransfer = event.receive(tmpFile);
		} catch (final IOException e) {
			fail(e.getLocalizedMessage());
		}
	}

	
	protected void testReceive(String url) throws Exception {
		assertNotNull(retrieveAdapter);
		final IFileTransferListener listener = createFileTransferListener();
		final IFileID fileID = createFileID(new URL(url));
		retrieveAdapter.sendRetrieveRequest(fileID, listener, null);

		waitForDone(10000);

		assertHasEvent(startEvents, IIncomingFileTransferReceiveStartEvent.class);
		assertHasMoreThanEventCount(dataEvents, IIncomingFileTransferReceiveDataEvent.class, 0);
		assertHasEvent(doneEvents, IIncomingFileTransferReceiveDoneEvent.class);

		assertTrue(tmpFile.exists());
		assertTrue(tmpFile.length() > 0);
	}

	public void testReceiveFile() throws Exception {
		//addProxy("composent.com",3129,"foo\\bar","password");
		testReceive(HTTP_RETRIEVE);
	}
	
	public void testFTPReceiveFile() throws Exception {
		testReceive(FTP_RETRIEVE);
	}
	
	public void testHttpsReceiveFile() throws Exception {
		testReceive(HTTPS_RETRIEVE);
	}

	public void testFailedReceive() throws Exception {
		try {
			testReceive(HTTP_404_FAIL_RETRIEVE);
			fail();
		} catch (final Exception e) {
			assertTrue(e instanceof IncomingFileTransferException);
		}
	}
	
	public void testReceiveGzip() throws Exception {
		testReceive(BUG_237936_URL);
	}

	public void testReceiveGzipWithGZFile() throws Exception {
		File f = File.createTempFile("foo", "pascal.pack.gz");
		FileOutputStream fos = new FileOutputStream(f);
		System.out.println(f);
		IStatus s = ECFTransport
				.getInstance()
				.download(
						"http://download.eclipse.org/eclipse/updates/3.5-I-builds/plugins/javax.servlet.jsp_2.0.0.v200806031607.jar.pack.gz",
						fos, new NullProgressMonitor());
		fos.close();
		if (f != null) {
			System.out.println(f.length());
			assertTrue("4.0", f.length() < 50000);
		}
	}
 }