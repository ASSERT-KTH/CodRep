import org.eclipse.ecf.internal.provider.Trace;

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

import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.SharedObjectInitException;
import org.eclipse.ecf.core.sharedobject.events.RemoteSharedObjectCreateResponseEvent;
import org.eclipse.ecf.core.sharedobject.events.RemoteSharedObjectEvent;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectActivatedEvent;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectDeactivatedEvent;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.SimpleQueueImpl;
import org.eclipse.ecf.provider.Trace;
import org.eclipse.ecf.provider.generic.gmm.Member;

public class SOWrapper {
    static Trace debug = Trace.create("sharedobjectwrapper");
    protected ISharedObject sharedObject;
    private SOConfig sharedObjectConfig;
    private ID sharedObjectID;
    private SOContainer container;
    private ID containerID;
    private Thread thread;
    private SimpleQueueImpl queue;

    protected SOWrapper(SOContainer.LoadingSharedObject obj, SOContainer cont) {
        sharedObjectID = obj.getID();
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
        sharedObject = obj;
        container = cont;
        containerID = cont.getID();
        thread = null;
        queue = new SimpleQueueImpl();
    }

    protected void init() throws SharedObjectInitException {
        debug("init()");
        sharedObjectConfig.makeActive(new QueueEnqueueImpl(queue));
        sharedObject.init(sharedObjectConfig);
    }

    protected ID getObjID() {
        return sharedObjectConfig.getSharedObjectID();
    }

    protected ID getHomeID() {
        return sharedObjectConfig.getHomeContainerID();
    }

    protected SOConfig getConfig() {
        return sharedObjectConfig;
    }
    protected void activated() {
        debug("activated");
        thread = (Thread) AccessController.doPrivileged(new PrivilegedAction() {
            public Object run() {
                Thread aThread = getThread();
                return aThread;
            }
        });
        // Notify container and listeners
        container.notifySharedObjectActivated(sharedObjectID);
        // Start thread
        thread.start();
        // Send message
        send(new SharedObjectActivatedEvent(containerID, sharedObjectID));
    }

    protected void deactivated() {
        debug("deactivated()");
        container.notifySharedObjectDeactivated(sharedObjectID);
        send(new SharedObjectDeactivatedEvent(containerID, sharedObjectID));
        destroyed();
    }

    protected  void destroyed() {
        if (!queue.isStopped()) {
            if (thread != null)
                queue.enqueue(new DisposeEvent());
            queue.close();
        }
    }

    protected void otherChanged(ID otherID, boolean activated) {
        debug("otherChanged(" + otherID + "," + activated);
        if (activated && thread != null) {
            send(new SharedObjectActivatedEvent(containerID, otherID));
        } else {
            send(new SharedObjectDeactivatedEvent(containerID, otherID));
        }
    }

    protected void memberChanged(Member m, boolean add) {
        debug("memberChanged(" + m + "," + add);
        if (thread != null) {
            if (add) {
                send(new ContainerConnectedEvent(containerID, m
                        .getID()));
            } else {
                send(new ContainerDisconnectedEvent(containerID, m
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
                                } else {
                                    SOWrapper.this.svc(evt);
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
    	debug("queue("+evt+")");
        queue.enqueue(new ProcEvent(evt));
    }

    protected static class ProcEvent implements Event {
		private static final long serialVersionUID = 3257002142513378616L;
		Event theEvent = null;

        ProcEvent(Event event) {
            theEvent = event;
        }

        Event getEvent() {
            return theEvent;
        }
    }

    protected static class DisposeEvent implements Event {
		private static final long serialVersionUID = 3688503311859135536L;

		DisposeEvent() {
        }
    }

    protected void svc(Event evt) {
        sharedObject.handleEvent(evt);
    }

    protected void doDestroy() {
        sharedObject.dispose(containerID);
        // make config inactive
        sharedObjectConfig.makeInactive();
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
    public void deliverEvent(Event evt) {
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
        except.printStackTrace(System.err);
        dumpStack(
                "runner:handleRuntimeException(" + sharedObjectID.getName() + ")",
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