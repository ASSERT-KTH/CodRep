callback.dataSubscribed(agent, container.getID());

/*******************************************************************************
 * Copyright (c) 2005 Peter Nehrer and Composent, Inc.
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Peter Nehrer - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.internal.datashare;

import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.datashare.IDataShareService;
import org.eclipse.ecf.datashare.IPublicationCallback;
import org.eclipse.ecf.datashare.ISharedData;
import org.eclipse.ecf.datashare.ISubscriptionCallback;
import org.eclipse.ecf.datashare.IUpdateProvider;
import org.eclipse.ecf.datashare.multicast.AbstractMulticaster;
import org.eclipse.ecf.datashare.multicast.ConsistentMulticaster;

/**
 * @author pnehrer
 */
public class DataShareService implements IDataShareService {

	private ServiceManager mgr;

	private ISharedObjectContainer container;

	public DataShareService(ServiceManager mgr, ISharedObjectContainer container) {
		this.mgr = mgr;
		this.container = container;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.datashare.IDataShareService#publish(java.lang.Object,
	 *      org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.datashare.IUpdateProvider,
	 *      org.eclipse.ecf.datashare.IPublicationCallback)
	 */
	public synchronized void publish(Object dataGraph, ID id,
			IUpdateProvider provider, IPublicationCallback callback)
			throws ECFException {
		Agent agent = (Agent) container.getSharedObjectManager()
				.getSharedObject(id);
		if (agent != null)
			throw new ECFException("Already published!");

		IBootstrap bootstrap = getBootstrap();
		AbstractMulticaster sender = getSender();
		agent = new Agent(dataGraph, bootstrap, sender, provider, callback);
		container.getSharedObjectManager().addSharedObject(id, agent, null);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.datashare.IDataShareService#subscribe(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.datashare.ISubscriptionCallback)
	 */
	public synchronized ISharedData subscribe(ID id,
			ISubscriptionCallback callback) throws ECFException {
		Agent agent = (Agent) container.getSharedObjectManager()
				.getSharedObject(id);
		if (agent == null)
			return null; // TODO should we throw?

		if (callback != null)
			callback.dataSubscribed(agent, container.getConfig().getID());

		return agent;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.datashare.IDataShareService#dispose()
	 */
	public synchronized void dispose() {
		mgr.dispose(container);
		mgr = null;
		container = null;
	}

	private IBootstrap getBootstrap() {
		return new ServerBootstrap(); // TODO strategize
	}
	
	private AbstractMulticaster getSender() {
		return new ConsistentMulticaster(); // TODO strategize
	}
}