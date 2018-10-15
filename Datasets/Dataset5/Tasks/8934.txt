Object[] args)

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

package org.eclipse.ecf.provider.irc.container;

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.provider.IContainerInstantiator;

public class IRCContainerInstantiator implements IContainerInstantiator {

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.provider.IContainerInstantiator#createInstance(org.eclipse.ecf.core.ContainerTypeDescription, java.lang.Class[], java.lang.Object[])
	 */
	public IContainer createInstance(ContainerTypeDescription description,
			Class[] argTypes, Object[] args)
			throws ContainerCreateException {
		try {
			return new IRCRootContainer(IDFactory.getDefault().createGUID());
			//return new IRCContainer(IDFactory.getDefault().createGUID());
		} catch (IDCreateException e) {
			throw new ContainerCreateException("Exception creating ID",e);
		}
	}
}