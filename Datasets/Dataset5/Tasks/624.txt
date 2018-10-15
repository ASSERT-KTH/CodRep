private static final String HTTP_RETRIEVE = "http://ftp.osuosl.org/pub/eclipse/rt/ecf/update/features/org.eclipse.ecf.examples_1.2.0.v20071019-1300.jar";

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

import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IFileTransferPausable;
import org.eclipse.ecf.filetransfer.IIncomingFileTransfer;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDataEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceivePausedEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveResumedEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.service.IRetrieveFileTransfer;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

public class URLRetrievePauseResumeTest extends ContainerAbstractTestCase {

	private static final String HTTP_RETRIEVE = "http://ftp.osuosl.org/pub/eclipse/rt/ecf/org.eclipse.ecf.examples-1.0.3.v20070927-1821.zip";

	private static final String FILENAME = "foo.zip";

	private static final int PAUSE_TIME = 4000;

	private IRetrieveFileTransfer transferInstance;

	private File incomingFile = null;

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		transferInstance = Activator.getDefault().getRetrieveFileTransferFactory().newInstance();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		session = null;
		pausable = null;
		if (incomingFile != null)
			incomingFile.delete();
		incomingFile = null;
	}

	IIncomingFileTransfer session = null;

	IFileTransferPausable pausable = null;

	FileOutputStream outs = null;

	Object notify = new Object();

	private void closeOutputStream() {
		if (outs != null) {
			try {
				outs.close();
			} catch (final IOException e) {
				fail("output stream close exception");
			} finally {
				outs = null;
			}
		}
	}

	protected void testReceiveHttp(String url) throws Exception {
		assertNotNull(transferInstance);
		final IFileTransferListener listener = new IFileTransferListener() {
			public void handleTransferEvent(IFileTransferEvent event) {
				if (event instanceof IIncomingFileTransferReceiveResumedEvent) {
					try {
						IIncomingFileTransferReceiveResumedEvent rse = (IIncomingFileTransferReceiveResumedEvent) event;
						session = rse.receive(outs);
					} catch (Exception e) {
						fail(e.getLocalizedMessage());
					}
				} else if (event instanceof IIncomingFileTransferReceiveStartEvent) {
					IIncomingFileTransferReceiveStartEvent rse = (IIncomingFileTransferReceiveStartEvent) event;
					try {
						incomingFile = new File(FILENAME);
						outs = new FileOutputStream(incomingFile);
						session = rse.receive(outs);
						pausable = (IFileTransferPausable) session.getAdapter(IFileTransferPausable.class);
						if (pausable == null)
							fail("pausable is null");
					} catch (IOException e) {
						fail(e.getLocalizedMessage());
					}
				} else if (event instanceof IIncomingFileTransferReceiveDataEvent) {
					System.out.println("data=" + event);
				} else if (event instanceof IIncomingFileTransferReceivePausedEvent) {
					System.out.println("paused=" + event);
				} else if (event instanceof IIncomingFileTransferReceiveDoneEvent) {
					closeOutputStream();
					System.out.println("done=" + event);
					synchronized (notify) {
						notify.notify();
					}
				}
			}
		};

		transferInstance.sendRetrieveRequest(FileIDFactory.getDefault().createFileID(transferInstance.getRetrieveNamespace(), url), listener, null);

		// Now if we can do pausing, then pause, wait a while and resume
		if (pausable != null) {
			Thread.sleep(500);
			System.out.println("pausable.pause()=" + pausable.pause());
			System.out.println("Pausing " + PAUSE_TIME / 1000 + " seconds");
			Thread.sleep(PAUSE_TIME);
			final boolean success = pausable.resume();
			System.out.println("pausable.resume()=" + success);
			if (!success) {
				System.out.println("session=" + session);
				final Exception e = session.getException();
				System.out.println("  exception=" + e);
				if (e != null)
					e.printStackTrace();
				System.out.println("  isDone=" + session.isDone());
				return;
			}
			System.out.println();
		}

		synchronized (notify) {
			notify.wait();
		}

		final Exception e = session.getException();
		if (e != null)
			throw e;
	}

	public void testReceiveFile() throws Exception {
		testReceiveHttp(HTTP_RETRIEVE);
	}
}