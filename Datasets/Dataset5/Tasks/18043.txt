final IFileStore fileStore = EFS.getStore(new URI(getRemoteFileURL().getPath()));

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

package org.eclipse.ecf.internal.provider.filetransfer.efs;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URI;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileInfo;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.filetransfer.IIncomingFileTransfer;
import org.eclipse.ecf.filetransfer.IncomingFileTransferException;
import org.eclipse.ecf.filetransfer.events.IIncomingFileTransferReceiveStartEvent;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer;
import org.eclipse.ecf.provider.filetransfer.util.JREProxyHelper;

/**
 * 
 */
public class RetrieveFileTransfer extends AbstractRetrieveFileTransfer {

	JREProxyHelper proxyHelper = null;

	public RetrieveFileTransfer() {
		super();
		proxyHelper = new JREProxyHelper();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#hardClose()
	 */
	protected void hardClose() {
		super.hardClose();
		if (proxyHelper != null) {
			proxyHelper.dispose();
			proxyHelper = null;
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#openStreams()
	 */
	protected void openStreams() throws IncomingFileTransferException {
		try {
			final IFileStore fileStore = EFS.getStore(new URI(getRemoteFileURL().getFile()));
			final IFileInfo info = fileStore.fetchInfo();
			setFileLength(info.getLength());
			setInputStream(fileStore.openInputStream(0, null));

			listener.handleTransferEvent(new IIncomingFileTransferReceiveStartEvent() {
				private static final long serialVersionUID = 5693211912862160540L;

				public IFileID getFileID() {
					return remoteFileID;
				}

				public IIncomingFileTransfer receive(File localFileToSave) throws IOException {
					setOutputStream(new BufferedOutputStream(new FileOutputStream(localFileToSave)));
					job = new FileTransferJob(getRemoteFileURL().toString());
					job.schedule();
					return RetrieveFileTransfer.this;
				}

				public String toString() {
					final StringBuffer sb = new StringBuffer("IIncomingFileTransferReceiveStartEvent["); //$NON-NLS-1$
					sb.append("isdone=").append(done).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
					sb.append("bytesReceived=").append( //$NON-NLS-1$
							bytesReceived).append("]"); //$NON-NLS-1$
					return sb.toString();
				}

				public void cancel() {
					hardClose();
				}

				public IIncomingFileTransfer receive(OutputStream streamToStore) throws IOException {
					setOutputStream(streamToStore);
					setCloseOutputStream(false);
					job = new FileTransferJob(getRemoteFileURL().toString());
					job.schedule();
					return RetrieveFileTransfer.this;
				}

			});

		} catch (final Exception e) {
			throw new IncomingFileTransferException(e);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#doPause()
	 */
	protected boolean doPause() {
		return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#doResume()
	 */
	protected boolean doResume() {
		return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.retrieve.AbstractRetrieveFileTransfer#setupProxy(org.eclipse.ecf.core.util.Proxy)
	 */
	protected void setupProxy(Proxy proxy) {
		proxyHelper.setupProxy(proxy);
	}
}