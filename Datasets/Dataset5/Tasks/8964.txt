return getContext().isGroupManager();

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
import java.util.Arrays;
import java.util.Hashtable;
import java.util.Map;
import java.util.Random;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.ISharedObjectManager;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerJoinedEvent;
import org.eclipse.ecf.core.events.ISharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.events.ISharedObjectDeactivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.events.RemoteSharedObjectEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.IQueueEnqueue;
import org.eclipse.ecf.core.util.QueueException;
import org.eclipse.ecf.example.collab.Trace;

/**
 * @author slewis
 * 
 */
public class GenericSharedObject implements ISharedObject {
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

    protected static long replicateID = 0;
    ISharedObjectConfig config;
    protected SharedObjectMsg currentMsg;
    protected ID currentMsgFromContainerID;
    protected ID currentMsgFromObjID;
    protected Hashtable msgMap;
    protected Object msgMapLock = new Object();
    static final Trace trace = Trace.create("genericsharedobject");

    ID localContainerID;
    
    public void activated(ID[] ids) {
        trace("activated(" + Arrays.asList(ids) + ")");
        if (isHost()) {
            replicate(null);
        }
    }

    public void deactivated() {
        trace("deactivated()");
    }

    public void destroyRemote(ID remoteID) throws IOException {
        ISharedObjectContext context = getContext();
        if (context != null) {
            context.sendDispose(remoteID);
        }
    }

    public void destroySelf() {
        if (isHost()) {
            try {
                // Send destroy message to all known remotes
                destroyRemote(null);
            } catch (IOException e) {
                traceDump("Exception sending destroy message to remotes", e);
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
            traceDump("Exception in destroySelfLocal()",e);
        }
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
            trace("execMsg(" + fromID + "," + msg + ")");
            trace(" msg method=" + msg.getMethodName());
            trace(" proxy msg=" + methName);
            trace(" o=" + o);
            if (methName != null) {
                msg = SharedObjectMsg.makeMsg(msg.getClassName(), methName, msg
                        .getArgs());
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
        ISharedObjectContext context = getContext();
        if (context != null) {
            context.sendMessage(toID, new RemoteSharedObjectMsgEvent(getID(), toID,
                msg));
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#getAdapter(java.lang.Class)
     */
    public Object getAdapter(Class clazz) {
    	if (clazz.equals(ISharedObjectContainerTransaction.class) && (this instanceof ISharedObjectContainerTransaction)) {
    		return this;
    	}
        return null;
    }

    public ISharedObjectContext getContext() {
        ISharedObjectConfig soconfig = getConfig();
        if (soconfig != null) return soconfig.getContext();
        else return null;
    }

    public ISharedObjectConfig getConfig() {
        return config;
    }
    protected ID getHomeContainerID() {
        ISharedObjectConfig soconfig = getConfig();
        if (soconfig != null) {
            return soconfig.getHomeContainerID();
        } else return null;
    }

    public ID getID() {
        ISharedObjectConfig soconfig = getConfig();
        if (soconfig != null) {
            return soconfig.getSharedObjectID();
        } else return null;
    }

    protected long getIdentifier() {
        return replicateID++;
    }

    public ID getLocalContainerID() {
        return localContainerID;
    }

    protected SharedObjectDescription getReplicaDescription(ID receiver) {
        ISharedObjectConfig soconfig = getConfig();
        if (soconfig != null) {
            return new SharedObjectDescription(getID(), getClass().getName(),
            		soconfig.getProperties(), replicateID++);
        } else return null;
    }

    protected void handleCreateResponse(ID fromID, Throwable t, Long identifier) {
        trace("got create response " + fromID + " e=" + t + " id=" + identifier);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
     */
public void handleEvent(Event event) {
        trace("handleEvent("+event+")");
        if (event instanceof ISharedObjectActivatedEvent) {
            ISharedObjectActivatedEvent ae = (ISharedObjectActivatedEvent) event;
            ID myID = getID();
            if (myID == null) return;
            if (myID.equals(ae.getActivatedID())) {
                activated(ae.getGroupMemberIDs());
            } else {
                otherActivated(ae.getActivatedID());
            }
        } else if (event instanceof ISharedObjectDeactivatedEvent) {
            ISharedObjectDeactivatedEvent ae = (ISharedObjectDeactivatedEvent) event;
            ID myID = getID();
            if (myID == null) return;
            if (myID.equals(ae.getDeactivatedID())) {
                deactivated();
            } else {
                otherDeactivated(ae.getDeactivatedID());
            }
        } else if (event instanceof ISharedObjectContainerJoinedEvent) {
            memberAdded(((ISharedObjectContainerJoinedEvent)event).getJoinedContainerID());
        } else if (event instanceof ISharedObjectContainerDepartedEvent) {
            memberRemoved(((ISharedObjectContainerDepartedEvent)event).getDepartedContainerID());
        } else if (event instanceof ISharedObjectMessageEvent) {
            handleSharedObjectMessageEvent(((ISharedObjectMessageEvent)event));
        } else {
            System.err.println("Got unexpected event: "+event);
            trace("Got unexpected event: "+event);
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
        } else {
            System.err.println("Got unexpected ISharedObjectMessageEvent: "
                    + event);
            trace("Got unexpected ISharedObjectMessageEvent: " + event);
        }
    }
    protected void handleSelfSendMessageEvent(RemoteSharedObjectMsgEvent event) {
        trace("handleSelfSendMessageEvent("+event+")");
        execMsg(event.getRemoteContainerID(),event.getMsg());
    }
    protected void handleCreateResponseMessageEvent(ISharedObjectCreateResponseEvent event) {
        trace("handleCreateResponseMessageEvent("+event+")");
        handleCreateResponse(event.getRemoteContainerID(),event.getException(),new Long(event.getSequence()));
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
        trace("IGNORED msg from " + fromID + ": " + msg + " ");
    }

    protected void ignoreSharedObjectMsg(ID fromID, SharedObjectMsg aMsg) {
        // Do nothing
        trace("ignored message from " + fromID + ": " + aMsg);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
     */
    public void init(ISharedObjectConfig initData)
            throws SharedObjectInitException {
        this.config = initData;
        localContainerID = getContext().getLocalContainerID();
    }

    public boolean isHost() {
        ID homeContainerID = getHomeContainerID();
        if (homeContainerID == null) return false;
        else return (homeContainerID.equals(getLocalContainerID()));
    }

    protected Object isMsgAllowed(ID fromID, SharedObjectMsg aMsg) {
        return this;
    }

    protected Object isReplicaMsgAllowed(ID fromID, SharedObjectMsg aMsg) {
        return this;
    }

    public boolean isServer() {
        ISharedObjectContext context = getContext();
        if (context != null) {
            return getContext().isGroupServer();
        } else return false;
    }

    public void memberAdded(ID member) {
        trace("memberAdded(" + member + ")");
        if (isHost()) {
            replicate(member);
        }
    }

    public void memberRemoved(ID member) {
        trace("memberRemoved(" + member + ")");
    }

    public void msgException(Object target, SharedObjectMsg aMsg, Throwable e) {
        trace("msgException(" + getID() + "," + aMsg + "," + e + ")");
        if (e != null) {
            e.printStackTrace(System.err);
        }
    }

    public void otherActivated(ID member) {
        trace("otherActivated(" + member + ")");
    }

    public void otherDeactivated(ID member) {
        trace("otherDeactivated(" + member + ")");
    }

    public void registerProxy(Object object, String msg) {
        registerProxy(object, msg, null);
    }

    protected void registerProxy(Object object, String msg, String method) {
        if (msg == null || object == null)
            throw new NullPointerException(
                    "registerProxy:  params cannot be null");
        synchronized (msgMapLock) {
            // Create table lazily
            if (msgMap == null)
                msgMap = new Hashtable();
            else if (msgMap.containsKey(msg))
                throw new IllegalArgumentException(
                        "registerProxy:  proxy already registered for "
                                + method + " by " + object);
            // Then put entry into table with msg as key
            msgMap.put(msg, new MsgMap(object, method));
        }
    }

    protected void replicate(ID remote) {
        trace("replicate(" + remote + ")");
        try {
            // Get current group membership
            ISharedObjectContext context = getContext();
            if (context == null) return;
            ID[] group = context.getGroupMemberIDs();
            if (group == null || group.length < 1) {
                // we're done
                return;
            }
            SharedObjectDescription createInfo = getReplicaDescription(remote);
            if (createInfo != null) {
                context.sendCreate(remote, createInfo);
            } else {
                return;
            }
        } catch (IOException e) {
            traceDump("Exception in replicate", e);
            return;
        }
    }

    protected void sendSelf(SharedObjectMsg msg) {
        ISharedObjectContext context = getContext();
        if (context == null) return;
        IQueueEnqueue queue = context.getQueue();
        try {
            queue.enqueue(new RemoteSharedObjectMsgEvent(getID(), getContext()
                    .getLocalContainerID(), msg));
        } catch (QueueException e) {
            traceDump("QueueException enqueing message to self", e);
            return;
        }
    }

    public void sharedObjectMsg(ID fromID, SharedObjectMsg msg) {
        if (isMsgAllowed(fromID, msg) != null) {
            currentMsgFromObjID = fromID;
            execMsg(getLocalContainerID(), msg);
            currentMsgFromObjID = null;
        } else {
            ignoreSharedObjectMsg(fromID, msg);
        }
    }

    protected void trace(String msg) {
        if (Trace.ON && trace != null) {
            trace.msg(msg);
        }
    }

    protected void traceDump(String msg, Throwable t) {
        if (Trace.ON && trace != null) {
            trace.dumpStack(t, msg);
        }
    }

    public ID makeObject(ID target, String className, Map map) throws Exception {
        ISharedObjectContext crs = getContext();
        ID newID = IDFactory.makeStringID(getNewUniqueIDString());
        if (crs == null) {
            throw new InstantiationException(
                    "Cannot make object.  Have no local creation capability because context is null");
        } else {
            if (className != null && !className.equals("")) {
                trace("Creating new replicated object with class: " + className);
                if (target == null) {
                    try {
                        Class clazz = Class.forName(className);
                        Object inst = clazz.newInstance();
                        if (!(inst instanceof ISharedObject)) {
                            throw new InstantiationException("Exception creating instance of class: "+className+".  Does not implement ISharedObject");
                        }
                        if (inst instanceof ISharedObjectContainerTransaction) {
                            crs.getSharedObjectManager().addSharedObject(newID,(ISharedObject) inst,map);
                        } else {
                        SharedObjectDescription sd = new SharedObjectDescription(newID
                                ,
                                className, map);
                        crs.getSharedObjectManager()
                                .createSharedObject(sd);
                        }
                    } catch (Exception e) {
                        traceDump("Exception creating replicated object.", e);
                        throw e;
                    }
                } else {
                    throw new Exception(
                            "Server hasn't given permission for this operation");
                }
                // Success
                return newID;
            } else {
                trace("Invalid classname '" + className
                        + "'.  Cannot make object.");
                throw new InstantiationException("Invalid classname '"
                        + className);
            }
        }
    }

    public String getNewUniqueIDString() {
        return String.valueOf((new Random()).nextLong());
    }
}