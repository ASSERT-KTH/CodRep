return containers.containsKey(graph);

/*******************************************************************************
 * Copyright (c) 2004 Peter Nehrer and Composent, Inc.
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Peter Nehrer - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.example.sdo.editor;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.Iterator;

import org.eclipse.core.runtime.PlatformObject;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConfig;
import org.eclipse.ecf.core.SharedObjectInitException;
import org.eclipse.ecf.core.events.ISharedObjectActivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerJoinedEvent;
import org.eclipse.ecf.core.events.ISharedObjectDeactivatedEvent;
import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.Event;

/**
 * @author pnehrer
 */
class PublishedGraphTracker extends PlatformObject implements ISharedObject {

    private static final ID[] NO_GRAPHS = {};

    private static final int JOIN = 0;

    private static final int LEAVE = 1;

    private static final int ADD = 2;

    private static final int REMOVE = 3;

    private class Table {

        private final Hashtable graphs = new Hashtable();

        private final Hashtable containers = new Hashtable();

        public synchronized void add(ID containerID, ID[] graphs) {
            HashSet list = (HashSet) this.graphs.get(containerID);
            if (list == null) {
                list = new HashSet();
                this.graphs.put(containerID, list);
            }

            list.addAll(Arrays.asList(graphs));
            for (int i = 0; i < graphs.length; ++i) {
                list = (HashSet) containers.get(graphs[i]);
                if (list == null) {
                    list = new HashSet();
                    containers.put(graphs[i], list);
                }

                list.add(containerID);
            }
        }

        public synchronized void remove(ID containerID, ID graph) {
            HashSet list = (HashSet) graphs.get(containerID);
            if (list != null) {
                list.remove(graph);
                if (list.isEmpty())
                    graphs.remove(containerID);
            }

            list = (HashSet) containers.get(graph);
            if (list != null) {
                list.remove(containerID);
                if (list.isEmpty())
                    containers.remove(graph);
            }
        }

        public synchronized void remove(ID containerID) {
            HashSet list = (HashSet) graphs.get(containerID);
            if (list != null) {
                for (Iterator i = list.iterator(); i.hasNext();) {
                    ID graph = (ID) i.next();
                    list = (HashSet) containers.get(graph);
                    if (list != null) {
                        list.remove(containerID);
                        if (list.isEmpty())
                            containers.remove(graph);
                    }
                }
            }
        }

        public synchronized boolean contains(ID graph) {
            return containers.contains(graph);
        }

        public synchronized ID[] getGraphs(ID containerID) {
            HashSet list = (HashSet) graphs.get(containerID);
            return list == null ? NO_GRAPHS : (ID[]) list.toArray(new ID[list
                    .size()]);
        }
    }

    private final Table table = new Table();

    private ISharedObjectConfig config;

    public synchronized void add(ID graph) throws ECFException {
        if (config == null)
            throw new ECFException("Not connected.");

        ID[] graphs = new ID[] { graph };
        try {
            config.getContext().sendMessage(null,
                    new Object[] { new Integer(ADD), graphs });
        } catch (IOException e) {
            throw new ECFException(e);
        }

        handleAdd(config.getContext().getLocalContainerID(), graphs);
    }

    public synchronized boolean isPublished(ID graph) {
        return table.contains(graph);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#init(org.eclipse.ecf.core.ISharedObjectConfig)
     */
    public synchronized void init(ISharedObjectConfig initData)
            throws SharedObjectInitException {
        if (config == null)
            config = initData;
        else
            throw new SharedObjectInitException("Already initialized.");
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#handleEvent(org.eclipse.ecf.core.util.Event)
     */
    public void handleEvent(Event event) {
        if (event instanceof ISharedObjectMessageEvent) {
            ISharedObjectMessageEvent e = (ISharedObjectMessageEvent) event;
            Object[] data = (Object[]) e.getData();
            Integer type = (Integer) data[0];
            switch (type.intValue()) {
            case JOIN:
                handleJoin(e.getRemoteContainerID(),
                        data.length > 1 ? (ID[]) data[1] : null);
                break;

            case LEAVE:
                handleLeave(e.getRemoteContainerID());
                break;

            case ADD:
                handleAdd(e.getRemoteContainerID(), (ID[]) data[1]);
                break;

            case REMOVE:
                handleRemove(e.getRemoteContainerID(), (ID) data[1]);
            }
        } else if (event instanceof ISharedObjectContainerJoinedEvent) {
            if (((ISharedObjectContainerJoinedEvent) event)
                    .getJoinedContainerID().equals(
                            config.getContext().getLocalContainerID()))
                handleJoined();
        } else if (event instanceof ISharedObjectContainerDepartedEvent) {
            ISharedObjectContainerDepartedEvent e = (ISharedObjectContainerDepartedEvent) event;
            if (!e.getDepartedContainerID().equals(
                    config.getContext().getLocalContainerID()))
                handleLeave(e.getDepartedContainerID());
        } else if (event instanceof ISharedObjectActivatedEvent) {
            ISharedObjectActivatedEvent e = (ISharedObjectActivatedEvent) event;
            if (e.getActivatedID().equals(config.getSharedObjectID()))
                handleJoined();
        } else if (event instanceof ISharedObjectDeactivatedEvent) {
            ISharedObjectDeactivatedEvent e = (ISharedObjectDeactivatedEvent) event;
            if (e.getDeactivatedID().equals(config.getSharedObjectID()))
                handleDeactivated();
            else if (table.contains(e.getDeactivatedID()))
                handleRemoved(e.getDeactivatedID());
        }
    }

    private void handleJoin(ID containerID, ID[] graphs) {
        if (graphs != null)
            table.add(containerID, graphs);

        graphs = table.getGraphs(config.getContext().getLocalContainerID());
        if (graphs.length > 0)
            try {
                config.getContext().sendMessage(containerID,
                        new Object[] { new Integer(ADD), graphs });
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
    }

    private void handleLeave(ID containerID) {
        table.remove(containerID);
    }

    private void handleAdd(ID containerID, ID[] graphs) {
        table.add(containerID, graphs);
    }

    private void handleRemove(ID containerID, ID graph) {
        table.remove(containerID, graph);
    }

    private void handleJoined() {
        ID[] graphs = table
                .getGraphs(config.getContext().getLocalContainerID());
        Object[] data = graphs.length == 0 ? new Object[] { new Integer(JOIN) }
                : new Object[] { new Integer(JOIN), graphs };
        try {
            config.getContext().sendMessage(null, data);
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

    private void handleDeactivated() {
        try {
            config.getContext().sendMessage(null,
                    new Object[] { new Integer(LEAVE) });
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }

    private void handleRemoved(ID graph) {
        try {
            config.getContext().sendMessage(null,
                    new Object[] { new Integer(REMOVE), graph });
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        handleRemove(config.getContext().getLocalContainerID(), graph);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#handleEvents(org.eclipse.ecf.core.util.Event[])
     */
    public void handleEvents(Event[] events) {
        for (int i = 0; i < events.length; ++i)
            handleEvent(events[i]);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObject#dispose(org.eclipse.ecf.core.identity.ID)
     */
    public synchronized void dispose(ID containerID) {
        if (config != null
                && config.getContext().getLocalContainerID()
                        .equals(containerID))
            config = null;
    }
}