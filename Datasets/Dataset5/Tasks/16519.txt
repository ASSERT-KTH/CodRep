public class CancelServiceTest extends ContainerAbstractTestCase {

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
import java.io.IOException;

import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IIncomingFileTransfer;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDataEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.service.IRetrieveFileTransfer;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

public class RetrieveFileTransferCancelServiceTest extends ContainerAbstractTestCase {

	private static final String HTTP_RETRIEVE = "http://www.eclipse.org/ecf/ip_log.html";
	private static final String HTTPS_RETRIEVE = "https://bugs.eclipse.org/bugs";
	
	//private static final String EFS_RETRIEVE = "efs:file://c:/foo.txt";
	
	File tmpFile = null;
	
	private IRetrieveFileTransfer transferInstance;
	
	protected IRetrieveFileTransfer getTransferInstance() {
		return Activator.getDefault().getRetrieveFileTransferFactory().newInstance();
	}
	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		transferInstance = getTransferInstance();
		tmpFile = File.createTempFile("ECFTest", "");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		tmpFile = null;
	}

	IIncomingFileTransfer incoming = null;
	
	protected void testReceiveHttp(String url) throws Exception {
		assertNotNull(transferInstance);
		IFileTransferListener listener = new IFileTransferListener() {
			public void handleTransferEvent(IFileTransferEvent event) {
				if (event instanceof IIncomingFileTransferReceiveStartEvent) {
					IIncomingFileTransferReceiveStartEvent rse = (IIncomingFileTransferReceiveStartEvent) event;
					assertNotNull(rse.getFileID());
					assertNotNull(rse.getFileID().getFilename());
					try {
						incoming = rse.receive(tmpFile);
					} catch (IOException e) {
						fail(e.getLocalizedMessage());
					}
				} else if (event instanceof IIncomingFileTransferReceiveDataEvent) {
					if (incoming != null && incoming.getPercentComplete() > 0.50) {
						incoming.cancel();
					}
					System.out.println("receive data="+event);
				} else if (event instanceof IIncomingFileTransferReceiveDoneEvent) {
					System.out.println("receive done="+event+", exception="+incoming.getException());
					assertTrue(incoming.getException() != null);
				}
			}
		};

		transferInstance.sendRetrieveRequest(FileIDFactory.getDefault()
				.createFileID(transferInstance.getRetrieveNamespace(),
						url), listener, null);
		// Wait for 5 seconds
		sleep(5000, "Starting 5 second wait", "Ending 5 second wait");
	}

	public void testReceiveFile() throws Exception {
		testReceiveHttp(HTTP_RETRIEVE);
	}

	public void testHttpsReceiveFile() throws Exception {
		testReceiveHttp(HTTPS_RETRIEVE);
	}
	/*
	public void testEFSReceiveFile() throws Exception {
		testReceiveHttp(EFS_RETRIEVE);
	}
	*/
}