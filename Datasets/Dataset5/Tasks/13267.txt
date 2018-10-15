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

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.provider.IContainerInstantiator;

public class DummyFileTransferContainerInstantiator implements
		IContainerInstantiator {

	public IContainer createInstance(ContainerTypeDescription description,
			Object[] args) throws ContainerCreateException {
		throw new ContainerCreateException("can't create an instance of dummy");
	}

	public String[] getSupportedAdapterTypes(ContainerTypeDescription description) {
		return null;
	}

	public Class[][] getSupportedParameterTypes(
			ContainerTypeDescription description) {
		return null;
	}

}