import org.eclipse.ecf.examples.provider.trivial.identity.TrivialNamespace;

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

package org.eclipse.ecf.internal.examples.provider.trivial.container;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.AbstractContainer;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.internal.examples.provider.trivial.identity.TrivialNamespace;

/**
 * Trivial container implementation. Note that container adapter implementations can be
 * provided by the container class to expose appropriate adapters.
 */
public class TrivialContainer extends AbstractContainer
/*
 * implements IChannelContainerAdapter, ICallSessionContainerAdapter,
 * IDiscoveryContainerAdapter, IRetrieveFileTransferContainerAdapter
 */
{

	/*
	 * The targetID.  This value is set on 'connect' and unset in 'disconnect'.
	 * This represents the other process that this container is connected to.
	 * Value is returned via getConnectedID()
	 */
	private ID targetID = null;
	/*
	 * This is the ID for this container.  Returned via getID().
	 */
	private ID containerID = null;

	public TrivialContainer() throws IDCreateException {
		super();
		this.containerID = IDFactory.getDefault().createGUID();
	}

	public TrivialContainer(ID id) {
		super();
		Assert.isNotNull(id);
		this.containerID = id;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID targetID, IConnectContext connectContext) throws ContainerConnectException {
		if (!targetID.getNamespace().getName().equals(getConnectNamespace().getName()))
			throw new ContainerConnectException("targetID not of appropriate Namespace");

		fireContainerEvent(new ContainerConnectingEvent(getID(), targetID));

		// XXX connect to remote service here

		this.targetID = targetID;
		fireContainerEvent(new ContainerConnectedEvent(getID(), targetID));

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
		fireContainerEvent(new ContainerDisconnectingEvent(getID(), targetID));

		final ID oldID = targetID;

		// XXX disconnect here

		fireContainerEvent(new ContainerDisconnectedEvent(getID(), oldID));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(TrivialNamespace.NAME);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectedID()
	 */
	public ID getConnectedID() {
		return targetID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.IIdentifiable#getID()
	 */
	public ID getID() {
		return containerID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.AbstractContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class serviceType) {
		/*
		 * See AbstractContainer.getAdapter() implementation.
		 */
		return super.getAdapter(serviceType);
	}
}