container.addListener(listener);

/**
 * Copyright (c) 2006 Ecliptical Software Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Ecliptical Software Inc. - initial API and implementation
 */
package org.eclipse.ecf.pubsub.model;

import java.util.HashMap;

import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.core.sharedobject.ISharedObjectManager;
import org.eclipse.ecf.core.sharedobject.ReplicaSharedObjectDescription;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.core.sharedobject.SharedObjectCreateException;
import org.eclipse.ecf.core.sharedobject.SharedObjectDescription;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.pubsub.model.impl.AgentBase;
import org.eclipse.ecf.pubsub.model.impl.LocalAgent;

public class SharedModelFactory {
	
	protected static final Object INITIAL_DATA_KEY = AgentBase.INITIAL_DATA_KEY;
	
	protected static final Object MODEL_UPDATER_KEY = AgentBase.MODEL_UPDATER_KEY;

	protected static final long DEFAULT_CREATION_TIMEOUT = 5000;
	
	private static final SharedModelFactory INSTANCE = new SharedModelFactory();
	
	private SharedModelFactory() {
		// no public instantiation
	}
	
	public static SharedModelFactory getInstance() {
		return INSTANCE;
	}

	public IMasterModel createSharedDataSource(ISharedObjectContainer container, final ID id, Object data, String updaterID) throws SharedObjectCreateException {
		final ISharedObjectManager mgr = container.getSharedObjectManager();
		final Object[] result = new Object[1];
		final Object monitor = new Object();
		
		IContainerListener listener = new IContainerListener() {
			public void handleEvent(IContainerEvent event) {
				if (event instanceof ISharedObjectActivatedEvent) {
					ISharedObjectActivatedEvent e = (ISharedObjectActivatedEvent) event;
					if (e.getActivatedID().equals(id)) {
						result[0] = mgr.getSharedObject(id);
						synchronized (monitor) {
							monitor.notify();
						}
					}
				}
			}
		};
		
		try {
			container.addListener(listener, null);
/*			SharedObjectDescription desc = createLocalAgentDescription(id, container.getID(), data, updaterID);
			synchronized (monitor) {
				mgr.createSharedObject(desc);
				if (result[0] == null)
					monitor.wait(getCreationTimeout());
			}
*/		
			synchronized (monitor) {
				addSharedObject(mgr,id,data,updaterID);
				if (result[0] == null) monitor.wait(getCreationTimeout());
			}
		} catch (InterruptedException e) {
			throw new SharedObjectCreateException(e);
		} finally {
			container.removeListener(listener);
		}
		
		
		return (IMasterModel) result[0];
	}
	
	protected long getCreationTimeout() {
		return DEFAULT_CREATION_TIMEOUT;
	}

	protected void addSharedObject(ISharedObjectManager mgr, ID id, Object data, String updaterID) throws SharedObjectCreateException {
		HashMap props = new HashMap(2);
		props.put(INITIAL_DATA_KEY, data);
		props.put(MODEL_UPDATER_KEY, updaterID);
		try {
			mgr.addSharedObject(id, new LocalAgent(), props);
		} catch (SharedObjectAddException e) {
			throw new SharedObjectCreateException(e);
		}		
	}
	protected SharedObjectDescription createLocalAgentDescription(ID sharedObjectID, ID homeContainerID, Object data, String updaterID) {
		HashMap props = new HashMap(2);
		props.put(INITIAL_DATA_KEY, data);
		props.put(MODEL_UPDATER_KEY, updaterID);
		return new ReplicaSharedObjectDescription(LocalAgent.class, sharedObjectID, homeContainerID, props);
	}
}