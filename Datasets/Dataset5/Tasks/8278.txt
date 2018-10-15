//private static final String EFS_RETRIEVE = "efs:file://c:/foo.txt";

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
import java.util.ArrayList;
import java.util.List;

import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDataEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.service.IRetrieveFileTransfer;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

public class RetrieveFileTransferServiceTest extends ContainerAbstractTestCase {

	private static final String HTTP_RETRIEVE = "http://www.eclipse.org/ecf/ip_log.html";
	private static final String HTTPS_RETRIEVE = "https://bugs.eclipse.org/bugs";
	
	private static final String EFS_RETRIEVE = "efs:file://c:/foo.txt";
	
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

	List receiveStartEvents = new ArrayList();

	List receiveDataEvents = new ArrayList();

	List receiveDoneEvents = new ArrayList();

	protected void testReceiveHttp(String url) throws Exception {
		assertNotNull(transferInstance);
		IFileTransferListener listener = new IFileTransferListener() {
			public void handleTransferEvent(IFileTransferEvent event) {
				if (event instanceof IIncomingFileTransferReceiveStartEvent) {
					IIncomingFileTransferReceiveStartEvent rse = (IIncomingFileTransferReceiveStartEvent) event;
					receiveStartEvents.add(rse);
					assertNotNull(rse.getFileID());
					assertNotNull(rse.getFileID().getFilename());
					try {
						rse.receive(tmpFile);
					} catch (IOException e) {
						fail(e.getLocalizedMessage());
					}
				} else if (event instanceof IIncomingFileTransferReceiveDataEvent) {
					receiveDataEvents.add(event);
				} else if (event instanceof IIncomingFileTransferReceiveDoneEvent) {
					receiveDoneEvents.add(event);
				}
			}
		};

		transferInstance.sendRetrieveRequest(FileIDFactory.getDefault()
				.createFileID(transferInstance.getRetrieveNamespace(),
						url), listener, null);
		// Wait for 5 seconds
		sleep(5000, "Starting 5 second wait", "Ending 5 second wait");

		assertHasEvent(receiveStartEvents,
				IIncomingFileTransferReceiveStartEvent.class);
		assertHasMoreThanEventCount(receiveDataEvents,
				IIncomingFileTransferReceiveDataEvent.class, 0);
		assertHasEvent(receiveDoneEvents,
				IIncomingFileTransferReceiveDoneEvent.class);
		
		assertTrue(tmpFile.exists());
		assertTrue(tmpFile.length() > 0);
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