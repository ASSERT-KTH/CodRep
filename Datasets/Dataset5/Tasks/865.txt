protected BaseContainer(long idl) throws ContainerCreateException {

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
package org.eclipse.ecf.core;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.provider.BaseContainerInstantiator;
import org.eclipse.ecf.core.security.IConnectContext;

/**
 * Base implementation of IContainer. Subclasses may be created to fill out the
 * behavior of this base implementation. Also, adapter factories may be created
 * via adapterFactory extension point to allow adapters to be added to this
 * BaseContainer implementation without the need to create a separate IContainer
 * implementation class.
 */
public class BaseContainer extends AbstractContainer {

	public static class Instantiator extends BaseContainerInstantiator {
		private static long nextBaseContainerID = 0L;
		
		public IContainer createInstance(ContainerTypeDescription description,
				Object[] parameters) throws ContainerCreateException {
			return new BaseContainer(nextBaseContainerID++);
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.provider.IContainerInstantiator#getSupportedAdapterTypes(org.eclipse.ecf.core.ContainerTypeDescription)
		 */
		public String[] getSupportedAdapterTypes(
				ContainerTypeDescription description) {
			return getInterfacesAndAdaptersForClass(BaseContainer.class);
		}
	}

	private ID id = null;
	
	private BaseContainer(long idl) throws ContainerCreateException {
		try {
			this.id = IDFactory.getDefault().createLongID(idl);
		} catch (IDCreateException e) {
			throw new ContainerCreateException(e);
		}
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID targetID, IConnectContext connectContext)
			throws ContainerConnectException {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectedID()
	 */
	public ID getConnectedID() {
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.IIdentifiable#getID()
	 */
	public ID getID() {
		return id;
	}

	public String toString() {
		StringBuffer sb = new StringBuffer("BaseContainer[");
		sb.append("id=").append(getID()).append("]");
		return sb.toString();
	}
}