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

import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Collection;
import java.util.Date;
import java.util.Iterator;

import junit.framework.TestCase;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.util.TimeoutException;
import org.eclipse.ecf.filetransfer.IRemoteFile;
import org.eclipse.ecf.filetransfer.IRemoteFileAttributes;
import org.eclipse.ecf.filetransfer.IRemoteFileInfo;
import org.eclipse.ecf.filetransfer.IRemoteFileSystemBrowserContainerAdapter;
import org.eclipse.ecf.filetransfer.IRemoteFileSystemListener;
import org.eclipse.ecf.filetransfer.IRemoteFileSystemRequest;
import org.eclipse.ecf.filetransfer.events.IRemoteFileSystemBrowseEvent;
import org.eclipse.ecf.filetransfer.events.IRemoteFileSystemEvent;
import org.eclipse.ecf.filetransfer.identity.FileIDFactory;
import org.eclipse.ecf.filetransfer.identity.IFileID;

/**
 *
 */
public abstract class AbstractBrowseTestCase extends TestCase {

	protected IRemoteFileSystemBrowserContainerAdapter adapter = null;

	protected Object lock = new Object();

	protected boolean done = false;

	protected IRemoteFileSystemRequest request = null;

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		final IContainer container = ContainerFactory.getDefault().createContainer();
		adapter = (IRemoteFileSystemBrowserContainerAdapter) container.getAdapter(IRemoteFileSystemBrowserContainerAdapter.class);
	}

	/* (non-Javadoc)
	 * @see junit.framework.TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
		adapter = null;
		if (request != null) {
			request.cancel();
			request = null;
		}
	}

	protected IRemoteFileSystemListener createRemoteFileSystemListener() {
		return new IRemoteFileSystemListener() {
			public void handleRemoteFileEvent(IRemoteFileSystemEvent event) {
				if (event instanceof IRemoteFileSystemBrowseEvent) {
					handleFileSystemBrowseEvent((IRemoteFileSystemBrowseEvent) event);
				} else
					handleUnknownEvent(event);
			}

		};
	}

	protected IFileID createFileID(URL directoryOrFile) throws Exception {
		return FileIDFactory.getDefault().createFileID(adapter.getBrowseNamespace(), directoryOrFile);
	}

	protected void testBrowse(URL directoryOrFile) throws Exception {
		Assert.isNotNull(adapter);
		request = adapter.sendBrowseRequest(createFileID(directoryOrFile), createRemoteFileSystemListener());
	}

	/**
		 * @param event
		 */
	protected void handleUnknownEvent(IRemoteFileSystemEvent event) {
		System.out.println("handleUnknownEvent(" + event + ")");
	}

	/**
	 * @param event
	 */
	protected void handleFileSystemBrowseEvent(IRemoteFileSystemBrowseEvent event) {
		System.out.println("handleFileSystemBrowseEvent(" + event + ")");
		if (event.getException() != null) {
			System.out.println(event.getException());
		}
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

	/**
	 * @param remoteFiles
	 */
	protected void verifyRemoteFiles(final IRemoteFile[] remoteFiles) {
		for (int i = 0; i < remoteFiles.length; i++) {
			final IRemoteFile first = remoteFiles[i];
			final IRemoteFileInfo firstInfo = first.getInfo();
			assertNotNull(firstInfo);
			final IFileID firstID = first.getID();
			assertNotNull(firstID);
			System.out.println("firstID=" + firstID);
			// Now check out info
			assertNotNull(firstInfo.getName());
			assertTrue(firstInfo.getLastModified() > 0);
			System.out.println("lastModified=" + new SimpleDateFormat().format(new Date(firstInfo.getLastModified())));
			System.out.println("length=" + firstInfo.getLength());
			System.out.println("isDirectory=" + firstInfo.isDirectory());
			final IRemoteFileAttributes attributes = firstInfo.getAttributes();
			assertNotNull(attributes);
			final Iterator attrNames = attributes.getAttributeKeys();
			for (; attrNames.hasNext();) {
				final String key = (String) attrNames.next();
				System.out.print("attrname=" + key);
				System.out.println(" attrvalue=" + attributes.getAttribute(key));
			}
		}
	}

}