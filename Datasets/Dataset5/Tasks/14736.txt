data.length > 1 ? (String[]) data[1] : null);

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

    private static final String[] NO_PATHS = {};

    private static final int JOIN = 0;

    private static final int LEAVE = 1;

    private static final int ADD = 2;

    private static final int REMOVE = 3;

    private class Table {

        private final Hashtable paths = new Hashtable();

        private final Hashtable containers = new Hashtable();

        public synchronized void add(ID containerID, String[] path) {
            HashSet list = (HashSet) paths.get(containerID);
            if (list == null) {
                list = new HashSet();
                paths.put(containerID, list);
            }

            list.addAll(Arrays.asList(path));
            for (int i = 0; i < path.length; ++i) {
                list = (HashSet) containers.get(path[i]);
                if (list == null) {
                    list = new HashSet();
                    containers.put(path[i], list);
                }

                list.add(containerID);
            }
        }

        public synchronized void remove(ID containerID, String path) {
            HashSet list = (HashSet) paths.get(containerID);
            if (list != null) {
                list.remove(path);
                if (list.isEmpty())
                    paths.remove(containerID);
            }

            list = (HashSet) containers.get(path);
            if (list != null) {
                list.remove(containerID);
                if (list.isEmpty())
                    containers.remove(path);
            }
        }

        public synchronized void remove(ID containerID) {
            HashSet list = (HashSet) paths.get(containerID);
            if (list != null) {
                for (Iterator i = list.iterator(); i.hasNext();) {
                    String path = (String) i.next();
                    list = (HashSet) containers.get(path);
                    if (list != null) {
                        list.remove(containerID);
                        if (list.isEmpty())
                            containers.remove(path);
                    }
                }
            }
        }

        public synchronized boolean contains(String path) {
            return containers.contains(path);
        }

        public synchronized String[] getPaths(ID containerID) {
            HashSet list = (HashSet) paths.get(containerID);
            return list == null ? NO_PATHS : (String[]) list
                    .toArray(new String[list.size()]);
        }
    }

    private final Table table = new Table();

    private ISharedObjectConfig config;

    public synchronized void add(String path) throws ECFException {
        if (config == null)
            throw new ECFException("Not connected.");

        String[] paths = new String[] { path };
        try {
            config.getContext().sendMessage(null,
                    new Object[] { new Integer(ADD), paths });
        } catch (IOException e) {
            throw new ECFException(e);
        }

        handleAdd(config.getContext().getLocalContainerID(), paths);
    }

    public synchronized void remove(String path) throws ECFException {
        if (config == null)
            throw new ECFException("Not connected.");

        try {
            config.getContext().sendMessage(null,
                    new Object[] { new Integer(REMOVE), path });
        } catch (IOException e) {
            throw new ECFException(e);
        }

        handleRemove(config.getContext().getLocalContainerID(), path);
    }

    public synchronized boolean isPublished(String path) {
        return table.contains(path);
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
                        data.length > 2 ? (String[]) data[1] : null);
                break;

            case LEAVE:
                handleLeave(e.getRemoteContainerID());
                break;

            case ADD:
                handleAdd(e.getRemoteContainerID(), (String[]) data[1]);
                break;

            case REMOVE:
                handleRemove(e.getRemoteContainerID(), (String) data[1]);
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
            if (((ISharedObjectActivatedEvent) event).getActivatedID().equals(
                    config.getSharedObjectID()))
                handleJoined();
        } else if (event instanceof ISharedObjectDeactivatedEvent) {
            if (((ISharedObjectDeactivatedEvent) event).getDeactivatedID()
                    .equals(config.getSharedObjectID()))
                handleDeactivated();
        }
    }

    private void handleJoin(ID containerID, String[] paths) {
        if (paths != null)
            table.add(containerID, paths);

        paths = table.getPaths(config.getContext().getLocalContainerID());
        if (paths.length > 0)
            try {
                config.getContext().sendMessage(containerID,
                        new Object[] { new Integer(ADD), paths });
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
    }

    private void handleLeave(ID containerID) {
        table.remove(containerID);
    }

    private void handleAdd(ID containerID, String[] paths) {
        table.add(containerID, paths);
    }

    private void handleRemove(ID containerID, String path) {
        table.remove(containerID, path);
    }

    private void handleJoined() {
        String[] paths = table.getPaths(config.getContext()
                .getLocalContainerID());
        Object[] data = paths.length == 0 ? new Object[] { new Integer(JOIN) }
                : new Object[] { new Integer(JOIN), paths };
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