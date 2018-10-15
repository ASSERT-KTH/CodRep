return fsb.sendBrowseRequest();

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

import java.net.URL;

import org.eclipse.core.filesystem.EFS;
import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.util.StringUtils;
import org.eclipse.ecf.filetransfer.IRemoteFileSystemListener;
import org.eclipse.ecf.filetransfer.IRemoteFileSystemRequest;
import org.eclipse.ecf.filetransfer.RemoteFileSystemException;
import org.eclipse.ecf.filetransfer.identity.IFileID;
import org.eclipse.ecf.filetransfer.service.IRemoteFileSystemBrowser;
import org.eclipse.ecf.filetransfer.service.IRemoteFileSystemBrowserFactory;
import org.eclipse.ecf.provider.filetransfer.identity.FileTransferNamespace;

/**
 *
 */
public class EFSRemoteFileSystemBrowseFactory implements IRemoteFileSystemBrowserFactory {

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.filetransfer.service.IRemoteFileSystemBrowserFactory#newInstance()
	 */
	public IRemoteFileSystemBrowser newInstance() {
		return new IRemoteFileSystemBrowser() {

			public Namespace getBrowseNamespace() {
				return IDFactory.getDefault().getNamespaceByName(FileTransferNamespace.PROTOCOL);
			}

			public IRemoteFileSystemRequest sendBrowseRequest(IFileID directoryOrFileID, IRemoteFileSystemListener listener) throws RemoteFileSystemException {
				Assert.isNotNull(directoryOrFileID);
				Assert.isNotNull(listener);
				URL efsDirectory = null;
				FileStoreBrowser fsb = null;
				try {
					efsDirectory = directoryOrFileID.getURL();
					final String path = StringUtils.replaceAll(efsDirectory.getPath(), " ", "%20"); //$NON-NLS-1$ //$NON-NLS-2$
					fsb = new FileStoreBrowser(EFS.getStore(new URL(path).toURI()), efsDirectory, directoryOrFileID, listener);
				} catch (final Exception e) {
					throw new RemoteFileSystemException(e);
				}
				return fsb.sendDirectoryRequest();
			}

			public Object getAdapter(Class adapter) {
				return null;
			}
		};
	}

}