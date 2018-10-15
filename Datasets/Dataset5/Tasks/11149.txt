traceExiting("handleSharedObjectMsgEvent", result ? Boolean.TRUE : Boolean.FALSE); //$NON-NLS-1$

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
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IIdentifiable;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.sharedobject.events.RemoteSharedObjectEvent;
import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;
import org.eclipse.ecf.core.sharedobject.util.QueueException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IEventProcessor;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.core.sharedobject.Activator;
import org.eclipse.ecf.internal.core.sharedobject.Messages;
import org.eclipse.ecf.internal.core.sharedobject.SharedObjectDebugOptions;

/**
 * Base class for shared object classes. This base class provides a number of
 * utility method for subclasses to use for tracing (e.g.
 * {@link #traceCatching(String, Throwable)}, {@link #traceEntering(String)},
 * {@link #traceExiting(String)}) logging (e.g.
 * {@link #log(int, String, Throwable)}), as well as methods to access the
 * {@link ISharedObjectContext} for the shared object instance (e.g.
 * {@link #getID()}, {@link #getHomeContainerID()}, {@link #getContext()},
 * {@link #getConfig()}, {@link #getProperties()}, {@link #isConnected()},
 * {@link #isPrimary()}, etc). Also provided are a number of methods for
 * sending messages to remote replica shared objects (e.g.
 * {@link #sendSharedObjectMsgTo(ID, SharedObjectMsg)},
 * {@link #sendSharedObjectMsgToPrimary(SharedObjectMsg)},
 * {@link #sendSharedObjectMsgToSelf(SharedObjectMsg)}) and methods for
 * replicating oneself to remote containers (e.g.
 * {@link #replicateToRemoteContainers(ID[])}). Finally, object lifecycle
 * methods are also provided (e.g. {@link #initialize()},
 * {@link #creationCompleted()}, {@link #dispose(ID)}).
 * 
 * Subclasses may use and override these methods as appropriate.
 * 
 */
public class BaseSharedObject implements ISharedObject, IIdentifiable {

	protected static final int DESTROYREMOTE_CODE = 8001;

	protected static final int DESTROYSELFLOCAL_CODE = 8002;

	private ISharedObjectConfig config = null;

	private List eventProcessors = new Vector();

	public BaseSharedObject() {
		super();
	}

	public final void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
		traceEntering("init", initData); //$NON-NLS-1$
		addEventProcessor(new SharedObjectMsgEventProcessor(this));
		initialize();
		traceExiting("init"); //$NON-NLS-1$
	}

	/**
	 * Initialize this shared object. Subclasses may override as appropriate to
	 * define custom initialization behavior. If initialization should fail,
	 * then a SharedObjectInitException should be thrown by implementing code.
	 * Also, subclasses overriding this method should call super.initialize()
	 * before running their own code.
	 * 
	 * @throws SharedObjectInitException
	 *             if initialization should throw
	 */
	protected void initialize() throws SharedObjectInitException {
		traceEntering("initialize"); //$NON-NLS-1$
	}

	/**
	 * Called by replication strategy code (e.g. two phase commit) when creation
	 * is completed (i.e. when transactional replication completed
	 * successfully). Subclasses that need to be notified when creation is
	 * completed should override this method.
	 * 
	 */
	protected void creationCompleted() {
		traceEntering("creationCompleted", null); //$NON-NLS-1$
	}

	public void dispose(ID containerID) {
		traceEntering("dispose", containerID); //$NON-NLS-1$
		eventProcessors.clear();
	}

	public Object getAdapter(Class adapter) {
		return null;
	}

	public void handleEvent(Event event) {
		traceEntering("handleEvent", event); //$NON-NLS-1$
		synchronized (eventProcessors) {
			fireEventProcessors(event);
		}
		traceExiting("handleEvent"); //$NON-NLS-1$
	}

	public boolean addEventProcessor(IEventProcessor proc) {
		return eventProcessors.add(proc);
	}

	public boolean removeEventProcessor(IEventProcessor proc) {
		return eventProcessors.remove(proc);
	}

	public void clearEventProcessors() {
		eventProcessors.clear();
	}

	protected void handleUnhandledEvent(Event event) {
		traceEntering("handleUnhandledEvent", event); //$NON-NLS-1$
	}

	protected void fireEventProcessors(Event event) {
		if (event == null)
			return;
		Event evt = event;
		if (eventProcessors.size() == 0) {
			handleUnhandledEvent(event);
			return;
		}
		for (Iterator i = eventProcessors.iterator(); i.hasNext();) {
			IEventProcessor ep = (IEventProcessor) i.next();
			if (ep.processEvent(evt))
				break;
		}
	}

	public void handleEvents(Event[] events) {
		traceEntering("handleEvents", events); //$NON-NLS-1$
		if (events == null)
			return;
		for (int i = 0; i < events.length; i++) {
			handleEvent(events[i]);
		}
		traceExiting("handleEvents"); //$NON-NLS-1$
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
		} else
			return (local.equals(home));
	}

	protected Map getProperties() {
		return getConfig().getProperties();
	}

	protected void destroySelf() {
		traceEntering("destroySelf"); //$NON-NLS-1$
		if (isPrimary()) {
			try {
				// Send destroy message to all known remotes
				destroyRemote(null);
			} catch (IOException e) {
				traceCatching("destroySelf", e); //$NON-NLS-1$
				log(DESTROYREMOTE_CODE, "destroySelf", e); //$NON-NLS-1$
			}
		}
		// Now destroy self locally
		destroySelfLocal();
		traceExiting("destroySelf"); //$NON-NLS-1$
	}

	protected void destroySelfLocal() {
		traceEntering("destroySelfLocal"); //$NON-NLS-1$
		try {
			ISharedObjectManager manager = getContext()
					.getSharedObjectManager();
			if (manager != null) {
				manager.removeSharedObject(getID());
			}
		} catch (Exception e) {
			traceCatching("destroySelfLocal", e); //$NON-NLS-1$
			log(DESTROYSELFLOCAL_CODE, "destroySelfLocal", e); //$NON-NLS-1$
		}
		traceExiting("destroySelfLocal"); //$NON-NLS-1$
	}

	protected void destroyRemote(ID remoteID) throws IOException {
		getContext().sendDispose(remoteID);
	}

	/**
	 * Send SharedObjectMessage to container with given ID. The toID parameter
	 * may be null, and if null the message will be delivered to <b>all</b>
	 * containers in group. The second parameter may not be null.
	 * 
	 * @param toID
	 *            the target container ID for the SharedObjectMsg. If null, the
	 *            given message is sent to all other containers currently in
	 *            group
	 * @param msg
	 *            the message instance to send
	 * @throws IOException
	 *             thrown if the local container is not connected or unable to
	 *             send for other reason
	 */
	protected void sendSharedObjectMsgTo(ID toID, SharedObjectMsg msg)
			throws IOException {
		Assert.isNotNull(msg,Messages.BaseSharedObject_Message_Not_Null);
		String method = "sendSharedObjectMsgTo"; //$NON-NLS-1$
		traceEntering(method, new Object[] { toID, msg });
		getContext().sendMessage(toID,
				new SharedObjectMsgEvent(getID(), toID, msg));
		traceExiting(method);
	}

	/**
	 * Send SharedObjectMsg to this shared object's primary instance.
	 * 
	 * @param msg
	 *            the message instance to send
	 * @throws IOException
	 *             throws if the local container is not connect or unable to
	 *             send for other reason
	 */
	protected void sendSharedObjectMsgToPrimary(SharedObjectMsg msg)
			throws IOException {
		sendSharedObjectMsgTo(getHomeContainerID(), msg);
	}

	/**
	 * Send SharedObjectMsg to local shared object. This places the given
	 * message at the end of this shared object's message queue for processing.
	 * 
	 * @param msg
	 *            the message instance to send.
	 */
	protected void sendSharedObjectMsgToSelf(SharedObjectMsg msg) {
		if (msg == null)
			throw new NullPointerException(Messages.BaseSharedObject_Message_Not_Null);
		ISharedObjectContext context = getContext();
		if (context == null)
			return;
		IQueueEnqueue queue = context.getQueue();
		try {
			queue.enqueue(new SharedObjectMsgEvent(getID(), getContext()
					.getLocalContainerID(), msg));
		} catch (QueueException e) {
			traceCatching("sendSharedObjectMsgToSelf", e); //$NON-NLS-1$
			log(DESTROYREMOTE_CODE, "sendSharedObjectMsgToSelf", e); //$NON-NLS-1$
		}
	}

	/**
	 * Get SharedObjectMsg from ISharedObjectMessageEvent.
	 * ISharedObjectMessageEvents can come from both local and remote sources.
	 * In the remote case, the SharedObjectMsg has to be retrieved from the
	 * RemoteSharedObjectEvent rather than the
	 * ISharedObjectMessageEvent.getData() directly. This method will provide a
	 * non-null SharedObjectMsg if it's provided either via remotely or locally.
	 * Returns null if the given event does not provide a valid SharedObjectMsg.
	 * 
	 * @param event
	 * @return SharedObjectMsg the SharedObjectMsg delivered by the given event
	 */
	protected SharedObjectMsg getSharedObjectMsgFromEvent(
			ISharedObjectMessageEvent event) {
		traceEntering("getSharedObjectMsgFromEvent", event); //$NON-NLS-1$
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

		if (msgData != null && msgData instanceof SharedObjectMsg) {
			traceExiting("getSharedObjectMsgFromEvent", msgData); //$NON-NLS-1$
			return (SharedObjectMsg) msgData;
		} else {
			traceExiting("getSharedObjectMsgFromEvent", null); //$NON-NLS-1$
			return null;
		}
	}

	/**
	 * Handle a ISharedObjectMessageEvent. This method will be automatically
	 * called by the SharedObjectMsgEventProcessor when a
	 * ISharedObjectMessageEvent is received. The SharedObjectMsgEventProcessor
	 * is associated with this object via the initialize() method
	 * 
	 * @param event
	 *            the event to handle
	 * @return true if the provided event should receive no further processing.
	 *         If false the provided Event should be passed to subsequent event
	 *         processors.
	 */
	protected boolean handleSharedObjectMsgEvent(ISharedObjectMessageEvent event) {
		traceEntering("handleSharedObjectMsgEvent", event); //$NON-NLS-1$
		boolean result = false;
		if (event instanceof ISharedObjectCreateResponseEvent)
			result = handleSharedObjectCreateResponseEvent((ISharedObjectCreateResponseEvent) event);
		else {
			SharedObjectMsg msg = getSharedObjectMsgFromEvent(event);
			if (msg != null)
				result = handleSharedObjectMsg(msg);
		}
		traceExiting("handleSharedObjectMsgEvent", new Boolean(result)); //$NON-NLS-1$
		return result;
	}

	/**
	 * Handle a ISharedObjectCreateResponseEvent. This handler is called by
	 * handleSharedObjectMsgEvent when the ISharedObjectMessageEvent is of type
	 * ISharedObjectCreateResponseEvent. This default implementation simply
	 * returns false. Subclasses may override as appropriate. Note that if
	 * return value is true, it will prevent subsequent event processors from
	 * having a chance to process event
	 * 
	 * @param createResponseEvent
	 *            the ISharedObjectCreateResponseEvent received
	 * @return true if the provided event should receive no further processing.
	 *         If false the provided Event should be passed to subsequent event
	 *         processors.
	 */
	protected boolean handleSharedObjectCreateResponseEvent(
			ISharedObjectCreateResponseEvent createResponseEvent) {
		return false;
	}

	/**
	 * SharedObjectMsg handler method. This method will be called by
	 * {@link #handleSharedObjectMsgEvent(ISharedObjectMessageEvent)} when a
	 * SharedObjectMsg is received either from a local source or a remote
	 * source. This default implementation simply returns false so that other
	 * processing of of the given msg can occur. Subclasses should override this
	 * behavior to define custom logic for handling SharedObjectMsgs.
	 * 
	 * @param msg
	 *            the SharedObjectMsg received
	 * @return true if the msg has been completely handled and subsequent
	 *         processing should stop. False if processing should continue
	 */
	protected boolean handleSharedObjectMsg(SharedObjectMsg msg) {
		return false;
	}

	/**
	 * Get a ReplicaSharedObjectDescription for a replica to be created on a
	 * given receiver.
	 * 
	 * @param receiver
	 *            the receiver the ReplicaSharedObjectDescription is for
	 * @return ReplicaSharedObjectDescription to be associated with given
	 *         receiver. A non-null ReplicaSharedObjectDescription <b>must</b>
	 *         be returned.
	 */
	protected ReplicaSharedObjectDescription getReplicaDescription(ID receiver) {
		traceEntering("getReplicaDescription", receiver); //$NON-NLS-1$
		ReplicaSharedObjectDescription result = new ReplicaSharedObjectDescription(
				getClass(), getID(), getConfig().getHomeContainerID(),
				getConfig().getProperties());
		traceExiting("getReplicaDescription", result); //$NON-NLS-1$
		return result;
	}

	/**
	 * This method is called by replicateToRemoteContainers to determine the
	 * ReplicaSharedObjectDescriptions associated with the given receivers.
	 * Receivers may be null (meaning that all in group are to be receivers),
	 * and if so then this method should return a ReplicaSharedObjectDescription []
	 * of length 1 with a single ReplicaSharedObjectDescription that will be
	 * used for all receivers. If receivers is non-null, then the
	 * ReplicaSharedObjectDescription [] result must be of <b>same length</b>
	 * as the receivers array. This method calls the getReplicaDescription
	 * method to create a replica description for each receiver. If this method
	 * returns null, <b>null replication is done</b>.
	 * 
	 * @param receivers
	 *            an ID[] of the intended receivers for the resulting
	 *            ReplicaSharedObjectDescriptions. If null, then the <b>entire
	 *            current group</b> is assumed to be the target, and this
	 *            method should return a ReplicaSharedObjectDescriptions array
	 *            of length 1, with a single ReplicaSharedObjectDescriptions for
	 *            all target receivers.
	 * 
	 * @return ReplicaSharedObjectDescription[] to determine replica
	 *         descriptions for each receiver. A null return value indicates
	 *         that no replicas are to be created. If the returned array is not
	 *         null, then it <b>must</b> be of same length as the receivers
	 *         parameter.
	 * 
	 */
	protected ReplicaSharedObjectDescription[] getReplicaDescriptions(
			ID[] receivers) {
		traceEntering("getReplicaDescriptions", receivers); //$NON-NLS-1$
		ReplicaSharedObjectDescription[] descriptions = null;
		if (receivers == null || receivers.length == 1) {
			descriptions = new ReplicaSharedObjectDescription[1];
			descriptions[0] = getReplicaDescription((receivers == null) ? null
					: receivers[0]);
		} else {
			descriptions = new ReplicaSharedObjectDescription[receivers.length];
			for (int i = 0; i < receivers.length; i++) {
				descriptions[i] = getReplicaDescription(receivers[i]);
			}
		}
		traceExiting("getReplicaDescriptions", descriptions); //$NON-NLS-1$
		return descriptions;
	}

	/**
	 * Get IDs of remote containers currently in this group. This method
	 * consults the current container context to retrieve the current group
	 * membership
	 * 
	 * @return ID[] of current group membership. Will not return null;
	 * 
	 * @see ISharedObjectContext#getGroupMemberIDs()
	 */
	protected ID[] getGroupMemberIDs() {
		return getContext().getGroupMemberIDs();
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
		traceEntering("replicateToRemoteContainers", remoteContainers); //$NON-NLS-1$
		try {
			// Get current group membership
			ReplicaSharedObjectDescription[] createInfos = getReplicaDescriptions(remoteContainers);
			if (createInfos != null) {
				if (createInfos.length == 1) {
					getContext().sendCreate(
							(remoteContainers == null) ? null
									: remoteContainers[0], createInfos[0]);
				} else {
					for (int i = 0; i < remoteContainers.length; i++) {
						getContext().sendCreate(remoteContainers[i],
								createInfos[i]);
					}
				}
			}
		} catch (IOException e) {
			traceCatching("replicateToRemoteContainers." + DESTROYREMOTE_CODE, //$NON-NLS-1$
					e);
			log(DESTROYREMOTE_CODE, "replicateToRemoteContainers", e); //$NON-NLS-1$
		}
	}

	protected void log(int code, String method, Throwable e) {
		Activator.getDefault().log(
				new Status(IStatus.ERROR, Activator.PLUGIN_ID, code,
						getSharedObjectAsString(method), e));
	}

	protected void log(String method, Throwable e) {
		log(IStatus.ERROR,method,e);
	}
	
	private String getSharedObjectAsString(String suffix) {
		StringBuffer buf = new StringBuffer(String.valueOf(getID()));
		buf.append(((isPrimary()) ? ".p." : ".r.")); //$NON-NLS-1$ //$NON-NLS-2$
		buf.append(suffix);
		return buf.toString();
	}

	protected void traceEntering(String methodName) {
		Trace.entering(Activator.PLUGIN_ID,
				SharedObjectDebugOptions.METHODS_ENTERING, this.getClass(),
				getSharedObjectAsString(methodName));
	}

	protected void traceEntering(String methodName, Object[] params) {
		Trace.entering(Activator.PLUGIN_ID,
				SharedObjectDebugOptions.METHODS_ENTERING, this.getClass(),
				getSharedObjectAsString(methodName));
	}

	protected void traceEntering(String methodName, Object param) {
		Trace.entering(Activator.PLUGIN_ID,
				SharedObjectDebugOptions.METHODS_ENTERING, this.getClass(),
				getSharedObjectAsString(methodName));
	}

	protected void traceExiting(String methodName) {
		Trace.entering(Activator.PLUGIN_ID,
				SharedObjectDebugOptions.METHODS_EXITING, this.getClass(),
				getSharedObjectAsString(methodName));
	}

	protected void traceExiting(String methodName, Object result) {
		Trace.entering(Activator.PLUGIN_ID,
				SharedObjectDebugOptions.METHODS_EXITING, this.getClass(),
				getSharedObjectAsString(methodName));
	}

	protected void traceCatching(String method, Throwable t) {
		Trace.catching(Activator.PLUGIN_ID,
				SharedObjectDebugOptions.EXCEPTIONS_CATCHING, this.getClass(),
				getSharedObjectAsString(method), t);
	}

}