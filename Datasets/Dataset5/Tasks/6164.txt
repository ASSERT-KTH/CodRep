System.out.println("");

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

package org.eclipse.ecf.example.collab.share;

import java.io.IOException;
import java.io.Serializable;
import java.util.Hashtable;
import java.util.Random;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.events.IContainerConnectedEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectConfig;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContext;
import org.eclipse.ecf.core.sharedobject.ReplicaSharedObjectDescription;
import org.eclipse.ecf.core.sharedobject.SharedObjectInitException;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectDeactivatedEvent;
import org.eclipse.ecf.core.sharedobject.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.sharedobject.events.RemoteSharedObjectEvent;
import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;
import org.eclipse.ecf.core.sharedobject.util.QueueException;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.internal.example.collab.ClientPlugin;

public class GenericSharedObject implements ISharedObject {
	protected static final String ARGS_PROPERTY_NAME = "args";

	protected static final class MsgMap {
		String meth;
		Object obj;

		MsgMap(Object o, String m) {
			obj = o;
			meth = m;
		}

		public Object getObject() {
			return obj;
		}
	}

	private static long replicateID = 0;
	protected ISharedObjectConfig config;
	protected SharedObjectMsg currentMsg;
	protected ID currentMsgFromContainerID;
	protected ID currentMsgFromObjID;
	protected Hashtable msgMap;
	protected Object msgMapLock = new Object();

	ID localContainerID;

	protected static long getNextReplicateID() {
		return replicateID++;
	}

	public void activated(ID[] ids) {
		if (isHost())
			replicate(null);
	}

	public void deactivated() {
	}

	public void destroyRemote(ID remoteID) throws IOException {
		getContext().sendDispose(remoteID);
	}

	public void destroySelf() {
		if (isHost()) {
			try {
				// Send destroy message to all known remotes
				destroyRemote(null);
			} catch (IOException e) {
				log("Exception sending destroy message to remotes", e);
			}
		}
		destroySelfLocal();
	}

	public void destroySelfLocal() {
		getContext().getSharedObjectManager().removeSharedObject(
				getConfig().getSharedObjectID());
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
	 */
	public void dispose(ID containerID) {
		config = null;
	}

	protected void execMsg(ID fromID, SharedObjectMsg msg) {
		try {
			MsgMap m = null;
			synchronized (msgMapLock) {
				m = (MsgMap) ((msgMap == null) ? null : (msgMap.get(msg
						.getMethodName())));
			}
			Object o = this;
			String methName = null;
			if (m != null) {
				if (m.obj != null) {
					o = m.obj;
				}
				if (m.meth != null) {
					methName = m.meth;
				}
			}
			if (methName != null) {
				msg = SharedObjectMsg.createMsg(msg.getClassName(), methName,
						msg.getArgs());
			}
			if (currentMsgFromObjID == null)
				currentMsgFromObjID = getID();
			currentMsgFromContainerID = fromID;
			currentMsg = msg;
			// Actually invoke msg on given object. Typically will be 'this'.
			execMsgInvoke(msg, currentMsgFromObjID, o);
			currentMsg = null;
			currentMsgFromContainerID = null;
		} catch (Throwable e) {
			msgException(this, msg, e);
		}
	}

	protected void execMsgInvoke(SharedObjectMsg msg, ID fromID, Object o)
			throws Exception {
		try {
			msg.invoke(o);
		} catch (NoSuchMethodException e) {
			msg.invokeFrom(fromID, o);
		}
	}

	protected void forwardMsgHome(SharedObjectMsg msg) throws IOException {
		forwardMsgTo(config.getHomeContainerID(), msg);
	}

	protected void forwardMsgTo(ID toID, SharedObjectMsg msg)
			throws IOException {
		getContext().sendMessage(toID,
				new RemoteSharedObjectMsgEvent(getID(), toID, msg));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		if (clazz.equals(ISharedObjectContainerTransaction.class)
				&& (this instanceof ISharedObjectContainerTransaction)) {
			return this;
		}
		return null;
	}

	public ISharedObjectContext getContext() {
		return getConfig().getContext();
	}

	public ISharedObjectConfig getConfig() {
		return config;
	}

	protected ID getHomeContainerID() {
		return getConfig().getHomeContainerID();
	}

	public ID getID() {
		return getConfig().getSharedObjectID();
	}

	protected ReplicaSharedObjectDescription getReplicaDescription(ID receiver) {
		return new ReplicaSharedObjectDescription(getClass(), getID(),
				getHomeContainerID(), getConfig().getProperties(),
				getNextReplicateID());
	}

	protected void handleCreateResponse(ID fromID, Throwable t, Long identifier) {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
	 */
	public void handleEvent(Event event) {
		if (event instanceof ISharedObjectActivatedEvent) {
			ISharedObjectActivatedEvent ae = (ISharedObjectActivatedEvent) event;
			ID myID = getID();
			if (myID == null)
				return;
			if (myID.equals(ae.getActivatedID())) {
				activated(getContext().getSharedObjectManager()
						.getSharedObjectIDs());
			} else {
				otherActivated(ae.getActivatedID());
			}
		} else if (event instanceof ISharedObjectDeactivatedEvent) {
			ISharedObjectDeactivatedEvent ae = (ISharedObjectDeactivatedEvent) event;
			ID myID = getID();
			if (myID == null)
				return;
			if (myID.equals(ae.getDeactivatedID())) {
				deactivated();
			} else {
				otherDeactivated(ae.getDeactivatedID());
			}
		} else if (event instanceof IContainerConnectedEvent) {
			memberAdded(((IContainerConnectedEvent) event).getTargetID());
		} else if (event instanceof IContainerDisconnectedEvent) {
			memberRemoved(((IContainerDisconnectedEvent) event).getTargetID());
		} else if (event instanceof ISharedObjectMessageEvent) {
			handleSharedObjectMessageEvent(((ISharedObjectMessageEvent) event));
		}
	}

	protected void handleSharedObjectMessageEvent(
			ISharedObjectMessageEvent event) {
		if (event instanceof RemoteSharedObjectEvent) {
			if (event instanceof ISharedObjectCreateResponseEvent) {
				handleCreateResponseMessageEvent((ISharedObjectCreateResponseEvent) event);
			} else if (event instanceof RemoteSharedObjectMsgEvent) {
				handleSelfSendMessageEvent((RemoteSharedObjectMsgEvent) event);
			} else {
				RemoteSharedObjectMsgEvent me = (RemoteSharedObjectMsgEvent) event
						.getData();
				SharedObjectMsg msg = me.getMsg();
				execMsg(me.getRemoteContainerID(), msg);
			}
		}
	}

	protected void handleSelfSendMessageEvent(RemoteSharedObjectMsgEvent event) {
		execMsg(event.getRemoteContainerID(), event.getMsg());
	}

	protected void handleCreateResponseMessageEvent(
			ISharedObjectCreateResponseEvent event) {
		handleCreateResponse(event.getRemoteContainerID(),
				event.getException(), new Long(event.getSequence()));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
	 */
	public void handleEvents(Event[] events) {
		for (int i = 0; i < events.length; i++) {
			handleEvent(events[i]);
		}
	}

	public void handleRemoteData(ID spaceID, Serializable msg) {
		SharedObjectMsg aMsg = (SharedObjectMsg) msg;
		if (isReplicaMsgAllowed(spaceID, aMsg) != null) {
			execMsg(spaceID, aMsg);
		} else {
			ignoreReplicaMsg(spaceID, aMsg);
		}
	}

	protected void ignoreReplicaMsg(ID fromID, SharedObjectMsg msg) {
		// Do nothing
	}

	protected void ignoreSharedObjectMsg(ID fromID, SharedObjectMsg aMsg) {
		// Do nothing
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
	 */
	public void init(ISharedObjectConfig initData)
			throws SharedObjectInitException {
		this.config = initData;
		this.localContainerID = getContext().getLocalContainerID();
	}

	public boolean isHost() {
		ID homeContainerID = getHomeContainerID();
		if (homeContainerID == null)
			return false;
		else
			return (homeContainerID.equals(localContainerID));
	}

	protected Object isMsgAllowed(ID fromID, SharedObjectMsg aMsg) {
		return this;
	}

	protected Object isReplicaMsgAllowed(ID fromID, SharedObjectMsg aMsg) {
		return this;
	}

	public boolean isServer() {
		return getContext().isGroupManager();
	}

	public void memberAdded(ID member) {
		if (isHost())
			replicate(member);
	}

	public void memberRemoved(ID member) {
	}

	public void msgException(Object target, SharedObjectMsg aMsg, Throwable e) {
		if (e != null)
			e.printStackTrace(System.err);
	}

	public void otherActivated(ID member) {
	}

	public void otherDeactivated(ID member) {
	}

	public void registerProxy(Object object, String msg) {
		registerProxy(object, msg, null);
	}

	protected void registerProxy(Object target, String msg, String method) {
		Assert.isNotNull(msg);
		Assert.isNotNull(target);
		synchronized (msgMapLock) {
			// Create table lazily
			if (msgMap == null)
				msgMap = new Hashtable();
			else if (msgMap.containsKey(msg))
				throw new IllegalArgumentException(
						"registerProxy:  proxy already registered for "
								+ method + " by " + target);
			// Then put entry into table with msg as key
			msgMap.put(msg, new MsgMap(target, method));
		}
	}

	protected void replicate(ID remote) {
		try {
			// Get current group membership
			ID[] group = getContext().getGroupMemberIDs();
			if (group == null || group.length < 1) {
				// we're done
				return;
			}
			ReplicaSharedObjectDescription createInfo = getReplicaDescription(remote);
			if (createInfo != null)
				getContext().sendCreate(remote, createInfo);
			else
				return;
		} catch (IOException e) {
			log("Exception in replicate", e);
		}
	}

	protected void sendSelf(SharedObjectMsg msg) {
		IQueueEnqueue queue = getContext().getQueue();
		try {
			queue.enqueue(new RemoteSharedObjectMsgEvent(getID(), getContext()
					.getLocalContainerID(), msg));
		} catch (QueueException e) {
			log("QueueException enqueing message to self", e);
		}
	}

	public void sharedObjectMsg(ID fromID, SharedObjectMsg msg) {
		if (isMsgAllowed(fromID, msg) != null) {
			currentMsgFromObjID = fromID;
			execMsg(localContainerID, msg);
			currentMsgFromObjID = null;
		} else {
			ignoreSharedObjectMsg(fromID, msg);
		}
	}

	protected void trace(String msg) {
	}

	protected void log(String msg, Throwable t) {
		ClientPlugin.log(msg, t);
	}

	public ID createObject(ID target, ReplicaSharedObjectDescription desc)
			throws Exception {
		if (target == null) {
			if (desc.getID() == null) {
				desc.setID(IDFactory.getDefault().createStringID(
						getUniqueString()));
			}
			try {
				return getContext().getSharedObjectManager()
						.createSharedObject(desc);
			} catch (Exception e) {
				log("Exception creating replicated object", e);
				throw e;
			}
		} else
			throw new Exception(
					"Cannot send object creation request direct to target");
	}

	public String getUniqueString() {
		return String.valueOf((new Random()).nextLong());
	}
}