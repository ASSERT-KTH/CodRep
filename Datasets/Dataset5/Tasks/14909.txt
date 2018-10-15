Thread.sleep(10000);

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

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.List;

import junit.framework.TestCase;

import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDataEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.service.IRetrieveFileTransfer;

public class MultiRetrieveFileTransferServiceTest extends TestCase {

	private static final String TESTSRCPATH = "test.src";
	private static final String TESTTARGETPATH = "test.target";
	
	private static List srcFiles = new ArrayList();
	
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
		Enumeration files = Activator.getDefault().getBundle().getEntryPaths(TESTSRCPATH);
		for( ; files.hasMoreElements(); ) {
			URL url = Activator.getDefault().getBundle().getEntry((String) files.nextElement());
			String file = url.getFile();
			if (file != null && !file.equals("") && !file.endsWith("/")) {
				srcFiles.add(url.toExternalForm());
			}
		}
		// Make target directory if it's not there
		File targetDir = new File(TESTTARGETPATH);
		targetDir.mkdirs();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
	}

	protected void printFileInfo(String prefix, IFileTransferEvent event, File targetFile) {
		System.out.println(prefix+";" + event
				+ ";length="+targetFile.length()
				+ ";file=" + targetFile.getAbsolutePath());
	}
	
	protected void testReceive(String url) throws Exception {
		final File srcFile = new File(url);
		assertNotNull(transferInstance);
		IFileTransferListener listener = new IFileTransferListener() {
			File targetFile = null;
			BufferedOutputStream bufferedStream = null;
			public void handleTransferEvent(IFileTransferEvent event) {
				if (event instanceof IIncomingFileTransferReceiveStartEvent) {
					IIncomingFileTransferReceiveStartEvent rse = (IIncomingFileTransferReceiveStartEvent) event;
					targetFile = new File(TESTTARGETPATH,rse.getFileID().getFilename());
					printFileInfo("START",event,targetFile);
					try {
						bufferedStream = new BufferedOutputStream(new FileOutputStream(targetFile));
						rse.receive(bufferedStream);
					} catch (IOException e) {
						e.printStackTrace();
						fail(e.getLocalizedMessage());
					}
				} else if (event instanceof IIncomingFileTransferReceiveDataEvent) {
					printFileInfo("DATA",event,targetFile);
				} else if (event instanceof IIncomingFileTransferReceiveDoneEvent) {
					try {
						bufferedStream.flush();
						printFileInfo("DONE",event,targetFile);
						assertTrue(srcFile.length()==targetFile.length());
					} catch (IOException e) {
						e.printStackTrace();
						fail(e.getLocalizedMessage());
					}
				} else {
					printFileInfo("OTHER",event,targetFile);
				}
			}
		};

		transferInstance.sendRetrieveRequest(FileIDFactory.getDefault()
				.createFileID(transferInstance.getRetrieveNamespace(), url),
				listener, null);
	}

	public void testReceives() throws Exception {
		for (Iterator i = srcFiles.iterator(); i.hasNext(); ) {
			testReceive((String) i.next());
		}
		Thread.sleep(50000);
	}

}