public class RetrieveFileTransferContainerAdapterFactory extends

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.filetransfer;

import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.httpclient.MultiThreadedHttpConnectionManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.AbstractSharedObjectContainerAdapterFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter;

public class HttpClientFileTransferAdapterFactory extends
		AbstractSharedObjectContainerAdapterFactory {

	private HttpClient httpClient = new HttpClient(
			new MultiThreadedHttpConnectionManager());

	protected ISharedObject createAdapter(ISharedObjectContainer container,
			Class adapterType, ID adapterID) {
		if (adapterType.equals(IRetrieveFileTransferContainerAdapter.class)) {
			return new HttpClientRetrieveFileTransfer(httpClient);
		} else
			return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.AbstractSharedObjectContainerAdapterFactory#getAdapterList()
	 */
	public Class[] getAdapterList() {
		return new Class[] { IRetrieveFileTransferContainerAdapter.class };
	}

}