} else return context.getConnectedID();

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

package org.eclipse.ecf.provider.generic.sobject;

import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.IIdentifiable;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.ISharedObjectManager;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;
import org.eclipse.ecf.provider.Trace;

/**
 * @author slewis
 *
 */
public class BaseSharedObject implements ISharedObject, IIdentifiable, ISharedObjectInternal {

	private static long identifier = 0L;
	
	public static final String TRANSACTION_PROPERTY_NAME = ISharedObjectContainerTransaction.class.getName();
	public static final int TRANSACTION_TIMEOUT_DEFAULT = -1;
	
	Trace trace = Trace.create("basesharedobject");
	
	ISharedObjectConfig config = null;
	List eventProcessors = new Vector();
	
	int transactionTimeout = TRANSACTION_TIMEOUT_DEFAULT;
	ISharedObjectContainerTransaction transaction = null;
	ID [] excludedContainerIDs;
	
	public BaseSharedObject(int transactionTimeout, ID [] excludedContainers) {
		super();
		this.transactionTimeout = transactionTimeout;
		this.excludedContainerIDs = excludedContainers;
	}
	public BaseSharedObject(int transactionTimeout) {
		this(transactionTimeout,null);
	}
	public BaseSharedObject() {
		this(TRANSACTION_TIMEOUT_DEFAULT,null);
	}
	protected static long getNextIdentifier() {
		return identifier++;
	}
	private void trace(String msg) {
		if (Trace.ON && trace != null) {
			trace.msg(getID()+":"+msg);
		}
	}
	private void traceStack(String msg, Throwable t) {
		if (Trace.ON && trace != null) {
			trace.dumpStack(t,getID()+":"+msg);
		}
	}
	public void addEventProcessor(IEventProcessor proc) {
		eventProcessors.add(proc);
	}
	public boolean removeEventProcessor(IEventProcessor proc) {
		return eventProcessors.remove(proc);
	}
	public void clearEventProcessors() {
		eventProcessors.clear();
	}
	protected void fireEventProcessors(Event event) {
		if (event == null) return;
		Event evt = event;
		trace("fireEventProcessors("+event+")");
		if (eventProcessors.size()==0) {
			handleUnhandledEvent(event);
			return;
		}
		for(Iterator i=eventProcessors.iterator(); i.hasNext(); ) {
			IEventProcessor ep = (IEventProcessor) i.next();
			if (ep != null) {
				if (evt != null) {
					if (ep.acceptEvent(evt)) {
						trace("eventProcessor="+ep+":event="+evt);
						evt = ep.processEvent(evt);
					}
				}
			}
		}
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
	 */
	public void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
		trace("init("+initData+")");
		initTransaction();
	}
	protected void initTransaction() {
		Map props = config.getProperties();
		// If transaction property is set, get Integer value and use for transaction timeout
		Object o = props.get(TRANSACTION_PROPERTY_NAME);
		if (o instanceof Integer) {
			Integer trans = (Integer) o;
			if (trans != null) {
				// transactional...
				transactionTimeout = trans.intValue();
			}
		}
		if (transactionTimeout != TRANSACTION_TIMEOUT_DEFAULT) {
			transaction = new SharedObjectReplication(this,transactionTimeout,excludedContainerIDs);
		}
	}
	protected ISharedObjectConfig getConfig() {
		return config;
	}
	public ISharedObjectContext getContext() {
		ISharedObjectConfig c = getConfig();
		if (c == null) {
			return null;
		} else return config.getContext();
	}
	public ID getHomeID() {
		ISharedObjectConfig conf = getConfig();
		if (conf == null) return null;
		else return conf.getHomeContainerID();
	}
	protected ID getLocalID() {
		ISharedObjectContext context = getContext();
		if (context == null) {
			return null;
		} else return context.getLocalContainerID();
	}
	protected ID getGroupID() {
		ISharedObjectContext context = getContext();
		if (context == null) {
			return null;
		} else return context.getGroupID();
	}
	public boolean isPrimary() {
		ID local = getLocalID();
		ID home = getHomeID();
		if (local == null || home == null) {
			return false;
		} else return (local.equals(home));
	}
	protected Map getProperties() {
		ISharedObjectConfig config = getConfig();
		if (config == null) {
			return null;
		} else return config.getProperties();
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
	 */
	public void handleEvent(Event event) {
		fireEventProcessors(event);
	}
	protected void handleUnhandledEvent(Event event) {
		trace("handleUnhandledEvent("+event+")");
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
	 */
	public void handleEvents(Event[] events) {
		if (events == null) return;
		for(int i=0; i < events.length; i++) {
			handleEvent(events[i]);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
	 */
	public void dispose(ID containerID) {
		config = null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		if (clazz.equals(ISharedObjectContainer.class)) {
			return this;
		}
		if (clazz.equals(ISharedObjectContainerTransaction.class)) {
			if (transactionTimeout != TRANSACTION_TIMEOUT_DEFAULT) {
				return transaction;
			} 
		}
		return null;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IIdentifiable#getID()
	 */
	public ID getID() {
		ISharedObjectConfig conf = getConfig();
		if (conf == null) {
			return null;
		} else return conf.getSharedObjectID();
	}
    public void destroySelf() {
        if (isPrimary()) {
            try {
                // Send destroy message to all known remotes
                destroyRemote(null);
            } catch (IOException e) {
                traceStack("Exception sending destroy message to remotes", e);
            }
        }
        destroySelfLocal();
    }

    public void destroySelfLocal() {
        try {
            ISharedObjectConfig soconfig = getConfig();
            if (soconfig != null) {
                ID myID = soconfig.getSharedObjectID();
                ISharedObjectContext context = getContext();
                if (context != null) {
                    ISharedObjectManager manager = context.getSharedObjectManager();
                    if (manager != null) {
                        manager.removeSharedObject(myID);
                    }
                }
            }
        } catch (Exception e) {
            traceStack("Exception in destroySelfLocal()",e);
        }
    }
    public void destroyRemote(ID remoteID) throws IOException {
        ISharedObjectContext context = getContext();
        if (context != null) {
            context.sendDispose(remoteID);
        }
    }

    public SharedObjectDescription getReplicaDescription(ID receiver) {
    	return new SharedObjectDescription(getID(), getClass().getName(),
        		getConfig().getProperties(), getNextIdentifier());
    }
    public SharedObjectDescription[] getReplicaDescriptions(ID [] receivers) {
    	SharedObjectDescription [] descriptions = null;
    	if (receivers == null || receivers.length == 1) {
    		descriptions = new SharedObjectDescription[1];
    		descriptions[0] = getReplicaDescription((receivers==null)?null:receivers[0]);
    	} else {
    		descriptions = new SharedObjectDescription[receivers.length];
    		for(int i=0; i < receivers.length; i++) {
    			descriptions[i] = getReplicaDescription(receivers[i]);
    		}
    	}
    	return descriptions;
    }

}