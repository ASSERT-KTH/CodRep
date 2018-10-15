public void deliverEvent(Event evt) {

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

package org.eclipse.ecf.provider.generic;

import java.io.Serializable;
import java.security.AccessController;
import java.security.PrivilegedAction;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.events.RemoteSharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.events.RemoteSharedObjectEvent;
import org.eclipse.ecf.core.events.SharedObjectActivatedEvent;
import org.eclipse.ecf.core.events.SharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.events.SharedObjectContainerJoinedEvent;
import org.eclipse.ecf.core.events.SharedObjectDeactivatedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.SimpleQueueImpl;
import org.eclipse.ecf.provider.Trace;
import org.eclipse.ecf.provider.generic.gmm.Member;

public class SOWrapper {
    static Trace debug = Trace.create("sharedobjectwrapper");
    protected ISharedObject sharedObject;
    private SOConfig sharedObjectConfig;
    private ID sharedObjectID;
    private ID sharedObjectHomeID;
    private SOContainer container;
    private ID containerID;
    private Thread thread;
    private SimpleQueueImpl queue;

    protected SOWrapper(SOContainer.LoadingSharedObject obj, SOContainer cont) {
        sharedObjectID = obj.getID();
        sharedObjectHomeID = obj.getHomeID();
        sharedObject = obj;
        container = cont;
        containerID = cont.getID();
        sharedObjectConfig = null;
        thread = null;
        queue = new SimpleQueueImpl();
    }

    protected SOWrapper(SOConfig aConfig, ISharedObject obj, SOContainer cont) {
        sharedObjectConfig = aConfig;
        sharedObjectID = sharedObjectConfig.getSharedObjectID();
        sharedObjectHomeID = sharedObjectConfig.getHomeContainerID();
        sharedObject = obj;
        container = cont;
        containerID = cont.getID();
        thread = null;
        queue = new SimpleQueueImpl();
    }

    protected void init() throws SharedObjectInitException {
        debug("init()");
        sharedObject.init(sharedObjectConfig);
    }

    protected ID getObjID() {
        return sharedObjectConfig.getSharedObjectID();
    }

    protected ID getHomeID() {
        return sharedObjectConfig.getHomeContainerID();
    }

    protected void activated(ID[] ids) {
        debug("activated");
        sharedObjectConfig.makeActive(new QueueEnqueueImpl(queue));
        thread = (Thread) AccessController.doPrivileged(new PrivilegedAction() {
            public Object run() {
                // Get thread instance
                Thread aThread = getThread();
                return aThread;
            }
        });
        thread.start();
        send(new SharedObjectActivatedEvent(containerID, sharedObjectID, ids));
        container.notifySharedObjectActivated(sharedObjectID);
    }

    protected void deactivated() {
        debug("deactivated()");
        send(new SharedObjectDeactivatedEvent(containerID, sharedObjectID));
        container.notifySharedObjectDeactivated(sharedObjectID);
        destroyed();
    }

    protected  void destroyed() {
        if (!queue.isStopped()) {
            sharedObjectConfig.makeInactive();
            if (thread != null)
                queue.enqueue(new DisposeEvent());
            queue.close();
        }
    }

    protected void otherChanged(ID otherID, boolean activated) {
        debug("otherChanged(" + otherID + "," + activated);
        if (activated && thread != null) {
            send(new SharedObjectActivatedEvent(containerID, otherID, null));
        } else {
            send(new SharedObjectDeactivatedEvent(containerID, otherID));
        }
    }

    protected void memberChanged(Member m, boolean add) {
        debug("memberChanged(" + m + "," + add);
        if (thread != null) {
            if (add) {
                send(new SharedObjectContainerJoinedEvent(containerID, m
                        .getID()));
            } else {
                send(new SharedObjectContainerDepartedEvent(containerID, m
                        .getID()));
            }
        }
    }

    protected Thread getThread() {
        return container.getNewSharedObjectThread(sharedObjectID,
                new Runnable() {
                    public void run() {
                        debug("runner(" + sharedObjectID + ")");
                        Event evt = null;
                        for (;;) {
                            if (Thread.currentThread().isInterrupted())
                                break;
                            evt = (Event) queue.dequeue();
                            if (Thread.currentThread().isInterrupted()
                                    || evt == null)
                                break;
                            try {
                                if (evt instanceof ProcEvent) {
                                    SOWrapper.this.svc(((ProcEvent) evt)
                                            .getEvent());
                                } else if (evt instanceof DisposeEvent) {
                                    SOWrapper.this.doDestroy();
                                }
                            } catch (Throwable t) {
                                handleRuntimeException(t);
                            }
                        }
                        if (Thread.currentThread().isInterrupted()) {
                            debug("runner(" + sharedObjectID
                                    + ") terminating interrupted");
                        } else {
                            debug("runner(" + sharedObjectID
                                    + ") terminating normally");
                        }
                    }
                });
    }

    private void send(Event evt) {
        queue.enqueue(new ProcEvent(evt));
    }

    protected static class ProcEvent implements Event {
        Event theEvent = null;

        ProcEvent(Event event) {
            theEvent = event;
        }

        Event getEvent() {
            return theEvent;
        }
    }

    protected static class DisposeEvent implements Event {
        DisposeEvent() {
        }
    }

    protected void svc(Event evt) {
        sharedObject.handleEvent(evt);
    }

    protected void doDestroy() {
        sharedObject.dispose(containerID);
    }

    protected void deliverSharedObjectMessage(ID fromID, Serializable data) {
        send(new RemoteSharedObjectEvent(getObjID(), fromID, data));
    }

    protected void deliverCreateResponse(ID fromID,
            ContainerMessage.CreateResponseMessage resp) {
        send(new RemoteSharedObjectCreateResponseEvent(
                resp.getSharedObjectID(), fromID, resp.getSequence(), resp
                        .getException()));
    }
    protected void deliverEvent(Event evt) {
        send(evt);
    }
    protected void destroySelf() {
        debug("destroySelf()");
        send(new DisposeEvent());
    }

    public String toString() {
        StringBuffer sb = new StringBuffer();
        sb.append("SharedObjectWrapper[").append(getObjID()).append("]");
        return sb.toString();
    }

    protected void debug(String msg) {
        if (Trace.ON && debug != null) {
            debug.msg(msg);
        }
    }

    protected void dumpStack(String msg, Throwable e) {
        if (Trace.ON && debug != null) {
            debug.dumpStack(e, msg);
        }
    }

    protected void handleRuntimeException(Throwable except) {
        dumpStack(
                "runner:unhandledexception(" + sharedObjectID.getName() + ")",
                except);
    }

    protected ISharedObject getSharedObject() {
        return sharedObject;
    }

    public SimpleQueueImpl getQueue() {
        return queue;
    }
}
 No newline at end of file