final IFileStore fileStore = EFS.getStore(new URI(getRemoteFileURL().getPath()));

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

package org.eclipse.ecf.internal.provider.filetransfer.efs;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.net.URI;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.filesystem.IFileStore;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransfer;
import org.eclipse.ecf.filetransfer.SendFileTransferException;
import org.eclipse.ecf.filetransfer.events.IOutgoingFileTransferResponseEvent;
import org.eclipse.ecf.provider.filetransfer.outgoing.AbstractOutgoingFileTransfer;
import org.eclipse.ecf.provider.filetransfer.util.JREProxyHelper;

/**
 *
 */
public class SendFileTransfer extends AbstractOutgoingFileTransfer {

	JREProxyHelper proxyHelper = null;

	public SendFileTransfer() {
		super();
		this.proxyHelper = new JREProxyHelper();
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.outgoing.AbstractOutgoingFileTransfer#hardClose()
	 */
	protected void hardClose() {
		super.hardClose();
		if (proxyHelper != null) {
			proxyHelper.dispose();
			proxyHelper = null;
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.outgoing.AbstractOutgoingFileTransfer#openStreams()
	 */
	protected void openStreams() throws SendFileTransferException {
		try {
			// Get/open input file
			setInputStream(new BufferedInputStream(new FileInputStream(getFileTransferInfo().getFile())));
			// Open target
			final IFileStore fileStore = EFS.getStore(new URI(getRemoteFileURL().getFile()));
			setOutputStream(fileStore.openOutputStream(0, null));
			// Notify listener
			listener.handleTransferEvent(new IOutgoingFileTransferResponseEvent() {

				private static final long serialVersionUID = 8414116325104138848L;

				public String toString() {
					final StringBuffer sb = new StringBuffer("IOutgoingFileTransferResponseEvent["); //$NON-NLS-1$
					sb.append("isdone=").append(done).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
					sb.append("bytesSent=").append( //$NON-NLS-1$
							bytesSent).append("]"); //$NON-NLS-1$
					return sb.toString();
				}

				public boolean requestAccepted() {
					return true;
				}

				public IOutgoingFileTransfer getSource() {
					return SendFileTransfer.this;
				}

			});

		} catch (final Exception e) {
			throw new SendFileTransferException(e);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.provider.filetransfer.outgoing.AbstractOutgoingFileTransfer#setupProxy(org.eclipse.ecf.core.util.Proxy)
	 */
	protected void setupProxy(Proxy proxy) {
		proxyHelper.setupProxy(proxy);
	}

}