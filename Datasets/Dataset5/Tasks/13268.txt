package org.eclipse.ecf.internal.provider.filetransfer;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.filetransfer;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.AbstractSharedObjectContainerAdapterFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter;

public class HttpClientFileTransferAdapterFactory extends
		AbstractSharedObjectContainerAdapterFactory {

	protected ISharedObject createAdapter(ISharedObjectContainer container,
			Class adapterType, ID adapterID) {
		if (adapterType.equals(IRetrieveFileTransferContainerAdapter.class)) {
			return new HttpClientRetrieveFileTransfer();
		} else return null;
	}

	public Class[] getAdapterList() {
		return new Class[] { IRetrieveFileTransferContainerAdapter.class };
	}

}