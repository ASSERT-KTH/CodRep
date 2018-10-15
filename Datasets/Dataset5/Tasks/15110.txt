public class PartialFileRetrieveTest extends ContainerAbstractTestCase {

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

import org.eclipse.ecf.filetransfer.IFileRangeSpecification;
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
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.filetransfer.service.IRetrieveFileTransfer;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

public class PartialFileRetrieveServiceTest extends ContainerAbstractTestCase {

	private static final String HTTP_RETRIEVE = "http://ftp.osuosl.org/pub/eclipse/technology/ecf/org.eclipse.ecf.examples-1.0.3.v20070927-1821.zip";

	private static final String FILENAME = "foo.zip";

	private IRetrieveFileTransfer transferInstance;

	File incomingFile = null;

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

	protected boolean isDone = false;

	protected void testReceiveHttp(final long start, final long end, String url) throws Exception {
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
						outs = new FileOutputStream(FILENAME);
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
						isDone = true;
						notify.notify();
					}
				}
			}
		};

		final IFileID fileID = FileIDFactory.getDefault().createFileID(transferInstance.getRetrieveNamespace(), url);
		IFileRangeSpecification rangeSpecification = null;
		if (start != -1) {
			rangeSpecification = new IFileRangeSpecification() {
				public long getEndPosition() {
					return end;
				}

				public long getStartPosition() {
					return start;
				}
			};
		}
		transferInstance.sendRetrieveRequest(fileID, rangeSpecification, listener, null);

		if (!isDone) {
			synchronized (notify) {
				notify.wait();
			}
		}

		final Exception e = session.getException();
		if (e != null)
			throw e;

		incomingFile = new File(FILENAME);
		final long fileLength = incomingFile.length();
		final long bytesReceived = session.getBytesReceived();
		System.out.println("start=" + start);
		System.out.println("end=" + end);
		System.out.println("bytes received=" + bytesReceived);
		System.out.println("fileLength=" + fileLength);

		if (start != -1) {
			assertTrue(fileLength == bytesReceived);
			if (end != -1) {
				assertTrue(fileLength == (end - start + 1));
			}
		}
	}

	/*
		public void testReceiveWholeFile() throws Exception {
			testReceiveHttp(-1, -1, HTTP_RETRIEVE);
		}

		public void testReceivePartialFile1() throws Exception {
			testReceiveHttp(0, -1, HTTP_RETRIEVE);
		}
	*/
	public void testReceivePartialFile2() throws Exception {
		testReceiveHttp(10, -1, HTTP_RETRIEVE);
	}

	public void testReceivePartialFile3() throws Exception {
		try {
			// should fail with invalid range spec
			testReceiveHttp(10, 5, HTTP_RETRIEVE);
			fail();
		} catch (final Exception e) {
		}
	}

	public void testReceivePartialFile4() throws Exception {
		testReceiveHttp(10, 20, HTTP_RETRIEVE);
	}

}