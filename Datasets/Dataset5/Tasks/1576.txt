package org.eclipse.ecf.provider.filetransfer.retrieve;

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

package org.eclipse.ecf.internal.provider.filetransfer.retrieve;

import org.eclipse.ecf.core.AbstractContainerAdapterFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.filetransfer.IRetrieveFileTransferContainerAdapter;

/**
 *
 */
public class MultiProtocolRetrieveAdapterFactory extends AbstractContainerAdapterFactory {

	IRetrieveFileTransferContainerAdapter multiProtocolAdapter = new MultiProtocolRetrieveAdapter();
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.AbstractSharedObjectContainerAdapterFactory#getAdapterList()
	 */
	public Class[] getAdapterList() {
		return new Class[] { IRetrieveFileTransferContainerAdapter.class };
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.AbstractContainerAdapterFactory#getContainerAdapter(org.eclipse.ecf.core.IContainer, java.lang.Class)
	 */
	protected Object getContainerAdapter(IContainer container, Class adapterType) {
		if (adapterType.equals(IRetrieveFileTransferContainerAdapter.class)) {
			return multiProtocolAdapter;
		} else
			return null;
	}

}