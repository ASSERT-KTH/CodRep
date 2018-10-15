throw new TimeoutException(timeout);

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
import java.net.URL;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;

import junit.framework.TestCase;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.util.TimeoutException;
import org.eclipse.ecf.filetransfer.IFileTransferListener;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransfer;
import org.eclipse.ecf.filetransfer.ISendFileTransferContainerAdapter;
import org.eclipse.ecf.filetransfer.events.IFileTransferEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferResponseEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferSendDataEvent;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferSendDoneEvent;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.identity.IFileID;

/**
 *
 */
public abstract class AbstractSendTestCase extends TestCase {

	ISendFileTransferContainerAdapter sendAdapter = null;

	protected List startEvents = null;
	protected List dataEvents = null;
	protected List doneEvents = null;

	protected IOutgoingFileTransfer outgoingFileTransfer;

	protected boolean done = false;

	Object lock = new Object();

	protected void trace(String msg) {
		System.out.println(msg);
	}

	protected ISendFileTransferContainerAdapter getSendAdapter() throws Exception {
		return (ISendFileTransferContainerAdapter) ContainerFactory.getDefault().createContainer().getAdapter(ISendFileTransferContainerAdapter.class);
	}

	protected IFileID createFileID(URL url) throws Exception {
		return FileIDFactory.getDefault().createFileID(sendAdapter.getOutgoingNamespace(), url);
	}

	protected void handleUnexpectedEvent(IFileTransferEvent event) {
		trace("handleUnexpectedEvent(" + event + ")");
	}

	protected void handleStartEvent(IOutgoingFileTransferResponseEvent event) {
		trace("handleStartEvent(" + event + ")");
		startEvents.add(event);
	}

	protected void handleDataEvent(IOutgoingFileTransferSendDataEvent event) {
		trace("handleDataEvent(" + event + ")");
		dataEvents.add(event);
	}

	protected void handleDoneEvent(IOutgoingFileTransferSendDoneEvent event) {
		trace("handleDoneEvent(" + event + ")");
		doneEvents.add(event);
		synchronized (lock) {
			done = true;
		}
	}

	protected IFileTransferListener createFileTransferListener() {
		return new IFileTransferListener() {
			public void handleTransferEvent(IFileTransferEvent event) {
				if (event instanceof IOutgoingFileTransferResponseEvent) {
					handleStartEvent((IOutgoingFileTransferResponseEvent) event);
				} else if (event instanceof IOutgoingFileTransferSendDataEvent) {
					handleDataEvent((IOutgoingFileTransferSendDataEvent) event);
				} else if (event instanceof IOutgoingFileTransferSendDoneEvent) {
					handleDoneEvent((IOutgoingFileTransferSendDoneEvent) event);
				} else {
					handleUnexpectedEvent(event);
				}
			}

		};
	}

	protected void testSendForFile(URL target, File inputFile) throws Exception {
		sendAdapter.sendOutgoingRequest(createFileID(target), inputFile, createFileTransferListener(), null);
	}

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		sendAdapter = getSendAdapter();
		startEvents = new ArrayList();
		dataEvents = new ArrayList();
		doneEvents = new ArrayList();
		synchronized (lock) {
			done = false;
		}
	}

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		sendAdapter = null;
		startEvents = null;
		dataEvents = null;
		doneEvents = null;
		super.tearDown();
	}

	protected void waitForDone(int timeout) throws Exception {
		final long start = System.currentTimeMillis();
		synchronized (lock) {
			while (!done && ((System.currentTimeMillis() - start) < timeout)) {
				lock.wait(timeout / 20);
			}
			if (!done)
				throw new TimeoutException(new Status(IStatus.ERROR,Activator.PLUGIN_ID,IStatus.ERROR,"timeout",null),(long) timeout);
		}
	}

	protected void assertHasEvent(Collection collection, Class eventType) {
		assertHasEventCount(collection, eventType, 1);
	}

	protected void assertHasEventCount(Collection collection, Class eventType, int eventCount) {
		int count = 0;
		for (final Iterator i = collection.iterator(); i.hasNext();) {
			final Object o = i.next();
			if (eventType.isInstance(o))
				count++;
		}
		assertTrue(count == eventCount);
	}

	protected void assertHasMoreThanEventCount(Collection collection, Class eventType, int eventCount) {
		int count = 0;
		for (final Iterator i = collection.iterator(); i.hasNext();) {
			final Object o = i.next();
			if (eventType.isInstance(o))
				count++;
		}
		assertTrue(count > eventCount);
	}

}