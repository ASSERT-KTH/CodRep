return false;

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
package org.eclipse.ecf.core.sharedobject;

import java.io.IOException;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.IIdentifiable;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.ISharedObjectManager;
import org.eclipse.ecf.core.ReplicaSharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.events.ISharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.events.RemoteSharedObjectEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;
import org.eclipse.ecf.core.util.IQueueEnqueue;
import org.eclipse.ecf.core.util.QueueException;
import org.eclipse.ecf.internal.core.Trace;

/**
 * Base class for shared object classes.
 *
 */
public class AbstractSharedObject implements ISharedObject,
		IIdentifiable {
	
	private static final Trace trace = Trace.create("abstractsharedobject");
	
	private ISharedObjectConfig config = null;
	private List eventProcessors = new Vector();
	
	public AbstractSharedObject() {
		super();
	}
	public final void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
		trace("init("+initData+")");
		addEventProcessor(new SharedObjectMsgEventProcessor(this));
		initialize();
	}
	/**
	 * Initialize this shared object.  Subclasses may override as appropriate
	 * to define custom initialization behavior.  If initialization should
	 * fail, then a SharedObjectInitException should be thrown by implementing code.
	 * Also, subclasses overriding this method should call super.initialize() before
	 * running their own code.
	 *
	 * @throws SharedObjectInitException if initialization should throw
	 */
	protected void initialize() throws SharedObjectInitException {}
    /**
     * Called by replication strategy code (e.g. two phase commit) when creation is completed (i.e. when transactional 
     * replication completed successfully).  Subclasses that need to be notified when creation is completed should 
     * override this method.
     *
     */
    protected void creationCompleted() {
    	trace("creationCompleted()");
    }
	public void dispose(ID containerID) {
		trace("dispose("+containerID+")");
		eventProcessors.clear();
		config = null;
	}
	public Object getAdapter(Class adapter) {
		return null;
	}
	public void handleEvent(Event event) {
		trace("handleEvent("+event+")");
		synchronized (eventProcessors) {
			fireEventProcessors(event);
		}
	}
	protected boolean addEventProcessor(IEventProcessor proc) {
		return eventProcessors.add(proc);
	}
	protected boolean removeEventProcessor(IEventProcessor proc) {
		return eventProcessors.remove(proc);
	}
	protected void clearEventProcessors() {
		eventProcessors.clear();
	}
	protected void handleUnhandledEvent(Event event) {
		trace("handleUnhandledEvent("+event+")");
	}
	protected void fireEventProcessors(Event event) {
		if (event == null) return;
		Event evt = event;
		if (eventProcessors.size()==0) {
			handleUnhandledEvent(event);
			return;
		}
		for(Iterator i=eventProcessors.iterator(); i.hasNext(); ) {
			IEventProcessor ep = (IEventProcessor) i.next();
			trace("calling eventProcessor="+ep+" for event="+evt);
			if (ep.processEvent(evt)) break;
		}
	}
	public void handleEvents(Event[] events) {
		trace("handleEvents("+Arrays.asList(events)+")");
		if (events == null) return;
		for(int i=0; i < events.length; i++) {
			handleEvent(events[i]);
		}
	}
	public ID getID() {
		return getConfig().getSharedObjectID();
	}
	protected ISharedObjectConfig getConfig() {
		return config;
	}
	protected ISharedObjectContext getContext() {
		return getConfig().getContext();
	}
	protected ID getHomeContainerID() {
		return getConfig().getHomeContainerID();
	}
	protected ID getLocalContainerID() {
		return getContext().getLocalContainerID();
	}
	protected ID getGroupID() {
		return getContext().getConnectedID();
	}
	protected boolean isConnected() {
		return (getContext().getConnectedID() != null);
	}
	protected boolean isPrimary() {
		ID local = getLocalContainerID();
		ID home = getHomeContainerID();
		if (local == null || home == null) {
			return false;
		} else return (local.equals(home));
	}
	protected Map getProperties() {
		return getConfig().getProperties();
	}
    protected void destroySelf() {
    	trace("destroySelf()");
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
    protected void destroySelfLocal() {
    	trace("destroySelfLocal()");
        try {
            ISharedObjectManager manager = getContext().getSharedObjectManager();
            if (manager != null) {
                manager.removeSharedObject(getID());
            }
        } catch (Exception e) {
            traceStack("Exception in destroySelfLocal()",e);
        }
    }
    protected void destroyRemote(ID remoteID) throws IOException {
        trace("destroyRemote("+remoteID+")");
    	getContext().sendDispose(remoteID);
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
	/**
	 * Send SharedObjectMessage to container with given ID.  The toID 
	 * parameter may be null, and if null the message will be delivered to 
	 * <b>all</b> containers in group.  The second parameter may not be null.
	 * 
	 * @param toID the target container ID for the SharedObjectMsg.  If null, the 
	 * given message is sent to all other containers currently in group
	 * @param msg the message instance to send
	 * @throws IOException thrown if the local container is not connected or unable
	 * to send for other reason
	 */
    protected void sendSharedObjectMsgTo(ID toID, SharedObjectMsg msg)
			throws IOException {
    	if (msg == null) throw new NullPointerException("msg cannot be null");
		getContext().sendMessage(toID,
				new SharedObjectMsgEvent(getID(), toID, msg));
	}
    /**
     * Send SharedObjectMsg to this shared object's primary instance.
     * @param msg the message instance to send
     * @throws IOException throws if the local container is not connect or unable 
     * to send for other reason
     */
    protected void sendSharedObjectMsgToPrimary(SharedObjectMsg msg) throws IOException {
    	sendSharedObjectMsgTo(getHomeContainerID(), msg);
    }
    /**
     * Send SharedObjectMsg to local shared object.  This places the given message at
     * the end of this shared object's message queue for processing.
     * @param msg the message instance to send.
     */
    protected void sendSharedObjectMsgToSelf(SharedObjectMsg msg) {
    	if (msg == null) throw new NullPointerException("msg cannot be null");
		ISharedObjectContext context = getContext();
		if (context == null)
			return;
		IQueueEnqueue queue = context.getQueue();
		try {
			queue.enqueue(new SharedObjectMsgEvent(getID(), getContext()
					.getLocalContainerID(), msg));
		} catch (QueueException e) {
			traceStack("QueueException enqueing message to self", e);
			return;
		}
	}
    /**
     * Get SharedObjectMsg from ISharedObjectMessageEvent.  ISharedObjectMessageEvents
     * can come from both local and remote sources.  In the remote case, the SharedObjectMsg
     * has to be retrieved from the RemoteSharedObjectEvent rather than the
     * ISharedObjectMessageEvent.getData() directly.  This method will provide a non-null
     * SharedObjectMsg if it's provided either via remotely or locally.  Returns null
     * if the given event does not provide a valid SharedObjectMsg.
     * @param event
     * @return SharedObjectMsg the SharedObjectMsg delivered by the given event
     */
	protected SharedObjectMsg getSharedObjectMsgFromEvent(
			ISharedObjectMessageEvent event) {
		Object eventData = event.getData();
		Object msgData = null;
		// If eventData is not null and instanceof RemoteSharedObjectEvent
		// then its a remote event and we extract the SharedObjectMsgEvent it
		// contains and get it's data
		if (eventData != null && eventData instanceof RemoteSharedObjectEvent) {
			// It's a remote event
			Object rsoeData = ((RemoteSharedObjectEvent) event).getData();
			if (rsoeData != null && rsoeData instanceof SharedObjectMsgEvent)
				msgData = ((SharedObjectMsgEvent) rsoeData).getData();
		} else
			msgData = eventData;
		if (msgData != null && msgData instanceof SharedObjectMsg)
			return (SharedObjectMsg) msgData;
		return null;
	}
    /**
     * Handle a ISharedObjectMessageEvent.  This method will be automatically called by 
     * the SharedObjectMsgEventProcessor when a ISharedObjectMessageEvent is received.
     * The SharedObjectMsgEventProcessor is associated with this object via the initialize()
     * method
     * @param event the event to handle
     * @return true if the provided event should receive no further processing.  If false the provided Event should be 
     * passed to subsequent event processors.
     */
    protected boolean handleSharedObjectMsgEvent(ISharedObjectMessageEvent event) {
    	trace("handleSharedObjectMsgEvent("+event+")");
    	if (event instanceof ISharedObjectCreateResponseEvent) return handleSharedObjectCreateResponseEvent((ISharedObjectCreateResponseEvent)event);
    	else {
	    	SharedObjectMsg msg = getSharedObjectMsgFromEvent(event);
	    	if (msg != null) return handleSharedObjectMsg(msg);
	    	else return false;
    	}
    }
    /**
     * Handle a ISharedObjectCreateResponseEvent.  This handler is called by handleSharedObjectMsgEvent
     * when the ISharedObjectMessageEvent is of type ISharedObjectCreateResponseEvent. This default 
     * implementation simply returns true.  Subclasses may override
     * as appropriate.
     * @param createResponseEvent the ISharedObjectCreateResponseEvent received
     * @return true if the provided event should receive no further processing.  If false the provided Event should be
     * passed to further event processors.  
     */
    protected boolean handleSharedObjectCreateResponseEvent(ISharedObjectCreateResponseEvent createResponseEvent) {
    	trace("handleSharedObjectCreateResponseEvent("+createResponseEvent+")");
    	return true;
    }
    /**
     * SharedObjectMsg handler method.  This method will be called by {@link #handleSharedObjectMsgEvent(ISharedObjectMessageEvent)} when
     * a SharedObjectMsg is received either from a local source or a remote source. This default implementation 
     * simply returns false so that other processing of of the given msg can occur.  Subclasses should override this
     * behavior to define custom logic for handling SharedObjectMsgs.
     * @param msg the SharedObjectMsg received
     * @return true if the msg has been completely handled and subsequent processing should stop.  False if processing 
     * should continue
     */
    protected boolean handleSharedObjectMsg(SharedObjectMsg msg) {
    	trace("handleSharedObjectMsg("+msg+")");
    	return false;
    }
	/**
	 * Get a ReplicaSharedObjectDescription for a replica to be created on a given receiver.
	 * 
	 * @param receiver the receiver the ReplicaSharedObjectDescription is for
	 * @return ReplicaSharedObjectDescription to be associated with given receiver.  A non-null
	 * ReplicaSharedObjectDescription <b>must</b> be returned.
	 */
	protected ReplicaSharedObjectDescription getReplicaDescription(ID receiver) {
		return new ReplicaSharedObjectDescription(getClass(),getID(),getConfig().getHomeContainerID(),
	    		getConfig().getProperties());
	}
	/**
	 * This method is called by replicateToRemoteContainers to
	 * determine the ReplicaSharedObjectDescriptions associated with the given receivers.  Receivers
	 * may be null (meaning that all in group are to be receivers), and if so then this method
	 * should return a ReplicaSharedObjectDescription [] of length 1 with a single ReplicaSharedObjectDescription
	 * that will be used for all receivers.  If receivers is non-null, then the ReplicaSharedObjectDescription [] 
	 * result must be of <b>same length</b> as the receivers array.  This method calls the
	 * getReplicaDescription method to create a replica description for each receiver.  If this method returns
	 * null, <b>null replication is done</b>.
	 * 
	 * @param receivers an ID[] of the intended receivers for the resulting ReplicaSharedObjectDescriptions.  If null,
	 * then the <b>entire current group</b> is assumed to be the target, and this method should return a
	 * ReplicaSharedObjectDescriptions array of length 1, with a single ReplicaSharedObjectDescriptions for all target receivers.
	 * 
	 * @return ReplicaSharedObjectDescription[] to determine replica descriptions for each receiver.  A null return
	 * value indicates that no replicas are to be created.  If the returned array is not null, then it <b>must</b>
	 * be of same length as the receivers parameter.
	 * 
	 */
	protected ReplicaSharedObjectDescription[] getReplicaDescriptions(ID[] receivers) {
		ReplicaSharedObjectDescription[] descriptions = null;
		if (receivers == null || receivers.length == 1) {
			descriptions = new ReplicaSharedObjectDescription[1];
			descriptions[0] = getReplicaDescription((receivers==null)?null:receivers[0]);
		} else {
			descriptions = new ReplicaSharedObjectDescription[receivers.length];
			for(int i=0; i < receivers.length; i++) {
				descriptions[i] = getReplicaDescription(receivers[i]);
			}
		}
		return descriptions;
	}
	/**
	 * Replicate this shared object to a given set of remote containers. This
	 * method will invoke the method getReplicaDescriptions in order to
	 * determine the set of ReplicaSharedObjectDescriptions to send to remote
	 * containers.
	 * 
	 * @param remoteContainers
	 *            the set of remote containers to replicate to. If null, <b>all</b>
	 *            containers in the current group are sent a message to create a
	 *            replica of this shared object.
	 */
	protected void replicateToRemoteContainers(ID[] remoteContainers) {
		if (remoteContainers == null)
			trace("replicateTo(null)");
		else
			trace("replicateTo(" + Arrays.asList(remoteContainers) + ")");
		try {
			// Get current group membership
			ISharedObjectContext context = getContext();
			if (context == null)
				return;
			ID[] group = context.getGroupMemberIDs();
			if (group == null || group.length < 1) {
				// we're done
				return;
			}
			ReplicaSharedObjectDescription[] createInfos = getReplicaDescriptions(remoteContainers);
			if (createInfos != null) {
				if (createInfos.length == 1) {
					context.sendCreate((remoteContainers == null) ? null
							: remoteContainers[0], createInfos[0]);
				} else {
					for (int i = 0; i < remoteContainers.length; i++) {
						context.sendCreate(remoteContainers[i], createInfos[i]);
					}
				}
			}
		} catch (IOException e) {
			if (remoteContainers == null)
				traceStack("Exception in replicateTo(null)", e);
			else
				traceStack("Exception in replicateTo("
						+ Arrays.asList(remoteContainers) + ")", e);
			return;
		}
	}

}