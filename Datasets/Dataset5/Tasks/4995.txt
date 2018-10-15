FileSystemBrowser fsb = new FileSystemBrowser(directoryID, listener);

/****************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.provider.filetransfer.browse;

import java.net.MalformedURLException;
import java.net.URL;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IAdapterManager;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.Proxy;
import org.eclipse.ecf.filetransfer.*;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.filetransfer.service.IRemoteFileSystemBrowser;
import org.eclipse.ecf.internal.provider.filetransfer.Activator;
import org.eclipse.ecf.internal.provider.filetransfer.Messages;
import org.eclipse.ecf.provider.filetransfer.identity.FileTransferNamespace;
import org.eclipse.osgi.util.NLS;

/**
 * Multi protocol handler for remote file system browser. 
 */
public class MultiProtocolFileSystemBrowserAdapter implements IRemoteFileSystemBrowser {

	IConnectContext connectContext = null;
	Proxy proxy = null;

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter#setConnectContextForAuthentication(org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void setConnectContextForAuthentication(IConnectContext connectContext) {
		this.connectContext = connectContext;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter#setProxy(org.eclipse.ecf.core.util.Proxy)
	 */
	public void setProxy(Proxy proxy) {
		this.proxy = proxy;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.IRemoteFileSystemBrowserContainerAdapter#getDirectoryNamespace()
	 */
	public Namespace getDirectoryNamespace() {
		return IDFactory.getDefault().getNamespaceByName(FileTransferNamespace.PROTOCOL);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.IRemoteFileSystemBrowserContainerAdapter#sendDirectoryRequest(org.eclipse.ecf.filetransfer.identity.IFileID, org.eclipse.ecf.filetransfer.IRemoteFileSystemListener)
	 */
	public IRemoteFileSystemRequest sendDirectoryRequest(IFileID directoryID, IRemoteFileSystemListener listener) throws RemoteFileSystemException {
		Assert.isNotNull(directoryID);
		Assert.isNotNull(listener);
		URL url;
		try {
			url = directoryID.getURL();
		} catch (final MalformedURLException e) {
			throw new RemoteFileSystemException(Messages.AbstractRetrieveFileTransfer_MalformedURLException);
		}

		IRemoteFileSystemBrowserContainerAdapter fileSystemBrowser = null;
		fileSystemBrowser = Activator.getDefault().getBrowseFileTransfer(url.getProtocol());

		if (fileSystemBrowser == null) {
			if (url.getProtocol().equalsIgnoreCase("file")) { //$NON-NLS-1$
				FileSystemBrowser fsb = new FileSystemBrowser(directoryID, url, listener);
				return fsb.sendDirectoryRequest();
			}
			throw new RemoteFileSystemException(NLS.bind(Messages.MultiProtocolOutgoingAdapter_EXCEPTION_NO_PROTOCOL_HANDER, directoryID));
		}

		return fileSystemBrowser.sendDirectoryRequest(directoryID, listener);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.core.runtime.IAdaptable#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		if (adapter == null)
			return null;
		final IAdapterManager adapterManager = Activator.getDefault().getAdapterManager();
		if (adapterManager == null)
			return null;
		return adapterManager.loadAdapter(this, adapter.getName());
	}

}