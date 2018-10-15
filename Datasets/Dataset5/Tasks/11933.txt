public class XMPPOutgoingTest extends ContainerAbstractTestCase {

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

package org.eclipse.ecf.tests.filetransfer.outgoing;

import java.io.File;
import java.io.FileOutputStream;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IIncomingFileTransferRequestListener;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransferContainerAdapter;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IFileTransferRequestEvent;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveDoneEvent;
import org.eclipse.ecf.filetransfer.identity.FileCreateException;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

/**
 * 
 */
public class OutgoingTest extends ContainerAbstractTestCase {

	private static final String TESTSRCPATH = "test.src";
	private static final String TESTSRCFILE = TESTSRCPATH + "/test.txt";

	private static final String TESTTARGETPATH = "test.target";

	static final String XMPP_CONTAINER = "ecf.xmpp.smack";

	protected IOutgoingFileTransferContainerAdapter adapter0, adapter1 = null;

	protected String getClientContainerName() {
		return XMPP_CONTAINER;
	}

	protected IOutgoingFileTransferContainerAdapter getOutgoingFileTransfer(int client) {
		final IContainer c = getClient(client);
		if (c != null)
			return (IOutgoingFileTransferContainerAdapter) c.getAdapter(IOutgoingFileTransferContainerAdapter.class);
		else
			return null;
	}

	protected IFileTransferListener getFileTransferListener(final String prefix) {
		return new IFileTransferListener() {
			public void handleTransferEvent(IFileTransferEvent event) {
				System.out.println(prefix + ".handleTransferEvent(" + event + ")");
				if (event instanceof IIncomingFileTransferReceiveDoneEvent) {

				}
			}
		};
	}

	File incomingDirectory = null;
	File incomingFile = null;

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		if (incomingFile != null)
			incomingFile.delete();
		incomingFile = null;
		if (incomingDirectory != null)
			incomingDirectory.delete();
		incomingDirectory = null;
	}

	protected IIncomingFileTransferRequestListener requestListener = new IIncomingFileTransferRequestListener() {

		public void handleFileTransferRequest(IFileTransferRequestEvent event) {
			System.out.println("receiver.handleFileTransferRequest(" + event + ")");
			incomingDirectory = new File(TESTTARGETPATH);
			incomingDirectory.mkdirs();
			incomingFile = new File(incomingDirectory, event.getFileTransferInfo().getFile().getName());
			try {
				FileOutputStream fos = new FileOutputStream(incomingFile);
				event.accept(fos, receiverTransferListener);
				//event.accept(f);
			} catch (Exception e) {
				e.printStackTrace(System.err);
				fail("exception calling accept for receive file transfer");
			}
		}

	};

	protected IFileTransferListener senderTransferListener = getFileTransferListener("sender");
	protected IFileTransferListener receiverTransferListener = getFileTransferListener("receiver");

	protected ID getServerConnectID(int client) {
		final IContainer container = getClient(client);
		final Namespace connectNamespace = container.getConnectNamespace();
		final String username = getUsername(client);
		try {
			return IDFactory.getDefault().createID(connectNamespace, username);
		} catch (final IDCreateException e) {
			e.printStackTrace(System.err);
			fail("Could not create server connect ID");
			return null;
		}
	}

	protected IFileID createFileID(IOutgoingFileTransferContainerAdapter adapter, ID clientID, String filename) throws FileCreateException {
		return FileIDFactory.getDefault().createFileID(adapter.getOutgoingNamespace(), new Object[] {clientID, filename});
	}

	public void testTwoClientsToSendAndReceive() throws Exception {
		// Setup two clients.  Client 0 is the receiver, client 1 is the sender
		setClientCount(2);
		clients = createClients();
		adapter0 = getOutgoingFileTransfer(0);
		adapter0.addListener(requestListener);
		adapter1 = getOutgoingFileTransfer(1);
		for (int i = 0; i < 2; i++) {
			connectClient(i);
		}

		final IFileID targetID = createFileID(adapter1, getServerConnectID(0), TESTSRCFILE);
		adapter1.sendOutgoingRequest(targetID, new File(TESTSRCFILE), senderTransferListener, null);

		sleep(20000);

		disconnectClients();

	}

}