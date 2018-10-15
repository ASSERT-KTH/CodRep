if (config.getContext().isGroupManager())

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

import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.events.ISharedObjectContainerJoinedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;

/**
 * @author pnehrer
 */
public class ServerBootstrap implements IBootstrap {

	private Agent agent;

	private ISharedObjectConfig config;

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.internal.datashare.IBootstrap#setAgent(org.eclipse.ecf.internal.datashare.Agent)
	 */
	public void setAgent(Agent agent) {
		this.agent = agent;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.internal.datashare.IBootstrap#init(org.eclipse.ecf.core.ISharedObjectConfig)
	 */
	public void init(ISharedObjectConfig config)
			throws SharedObjectInitException {
		this.config = config;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.internal.datashare.IBootstrap#handleEvent(org.eclipse.ecf.core.util.Event)
	 */
	public void handleEvent(Event event) {
		if (event instanceof ISharedObjectContainerJoinedEvent) {
			ISharedObjectContainerJoinedEvent e = (ISharedObjectContainerJoinedEvent) event;
			if (!e.getJoinedContainerID().equals(e.getLocalContainerID()))
				handleJoined(e.getJoinedContainerID());
		}
	}

	private void handleJoined(ID containerID) {
		if (config.getContext().isGroupServer()) // TODO how about isGroupManager()?
			agent.doBootstrap(containerID);
	}
	/*
	private void handleError(Throwable t) {
		t.printStackTrace();
	}
	*/
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.internal.datashare.IBootstrap#dispose(org.eclipse.ecf.core.identity.ID)
	 */
	public void dispose(ID containerID) {
		config = null;
	}

	public SharedObjectDescription createDescription() {
		return new SharedObjectDescription(config.getSharedObjectID(),
				getClass());
	}
}