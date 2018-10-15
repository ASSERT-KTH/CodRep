public ID[] getGroupMemberIDs() {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.internal.impl.standalone;

import java.io.Serializable;
import java.lang.reflect.Constructor;
import java.security.AccessController;
import java.security.PrivilegedActionException;
import java.security.PrivilegedExceptionAction;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import org.eclipse.ecf.core.IOSGIService;
import org.eclipse.ecf.core.ISharedObject;
import org.eclipse.ecf.core.ISharedObjectConnector;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.ISharedObjectContainerListener;
import org.eclipse.ecf.core.ISharedObjectContainerTransaction;
import org.eclipse.ecf.core.ISharedObjectManager;
import org.eclipse.ecf.core.SharedObjectAddException;
import org.eclipse.ecf.core.SharedObjectConnectException;
import org.eclipse.ecf.core.SharedObjectContainerJoinException;
import org.eclipse.ecf.core.SharedObjectCreateException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.SharedObjectDisconnectException;
import org.eclipse.ecf.core.SharedObjectNotFoundException;
import org.eclipse.ecf.core.events.ContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.AbstractFactory;
import org.osgi.framework.BundleContext;

public class StandaloneContainer implements ISharedObjectContainer,
        ISharedObjectManager {

    protected static final Object[] nullArgs = new Object[0];
    protected static final Class[] nullTypes = new Class[0];

    ISharedObjectContainerConfig config = null;
    Vector listeners = new Vector();
    Hashtable sharedObjectTable;
    
    BundleContext context = null;

    public static final String STANDALONE_NAME = "standalone";

    public StandaloneContainer(StandaloneConfig config, BundleContext ctx) {
        super();
        this.config = config;
        sharedObjectTable = new Hashtable();
        this.context = ctx;
    }

    public ISharedObjectManager getSharedObjectManager() {
        return this;
    }
    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getPeerID()
     */
    public ID getID() {
        return config.getID();
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getPeerConfig()
     */
    public ISharedObjectContainerConfig getConfig() {
        return config;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#addPeerListener(org.eclipse.ecf.core.ISharedObjectContainerListener)
     */
    public void addListener(ISharedObjectContainerListener l, String filter) {
        listeners.add(l);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#removePeerListener(org.eclipse.ecf.core.ISharedObjectContainerListener)
     */
    public void removeListener(ISharedObjectContainerListener l) {
        listeners.remove(l);
    }
    protected void fireListeners(ContainerEvent evt) {
        for (Enumeration e = listeners.elements(); e.hasMoreElements();) {
            ISharedObjectContainerListener l = (ISharedObjectContainerListener) e
                    .nextElement();
            l.handleEvent(evt);
        }
    }

    private void disposeSharedObjects() {
        Enumeration e = sharedObjectTable.elements();
        while (e.hasMoreElements()) {
            StandaloneSharedObjectWrapper wrapper = (StandaloneSharedObjectWrapper) e
                    .nextElement();
            wrapper.deactivated();
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#terminatePeer(long)
     */
    public void dispose(long waittime) {
        synchronized (sharedObjectTable) {
            disposeSharedObjects();
            sharedObjectTable.clear();
        }
    }
    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#joinGroup(org.eclipse.ecf.identity.ID,
     *      java.lang.Object)
     */
    public void joinGroup(ID groupID, Object loginData)
            throws SharedObjectContainerJoinException {
        throw new SharedObjectContainerJoinException(
                "Standalone container cannot join external groups");
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#leaveGroup()
     */
    public void leaveGroup() {
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupID()
     */
    public ID getGroupID() {
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupMembership()
     */
    public ID[] getGroupMembership() {
        return new ID[] { getID() };
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupManager()
     */
    public boolean isGroupManager() {
        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupServer()
     */
    public boolean isGroupServer() {
        return false;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getAdapter(java.lang.Class)
     */
    public Object getAdapter(Class clazz) {
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObjectIDs()
     */
    public ID[] getSharedObjectIDs() {
        return (ID[]) sharedObjectTable.keySet().toArray(new ID[0]);
    }

    protected static Object loadObject(final ClassLoader cl, String className,
            String[] argTypes, Object[] a) throws Exception {
        final Class[] types = AbstractFactory.getClassesForTypes(argTypes, a,
                cl);
        final Object[] args = (a == null) ? nullArgs : a;
        // Load RepObject class(es), after getting appropriate classloader
        final Class newClass = Class.forName(className, true, cl);
        Object newObject = null;
        try {
            // Do privileged operation. Get appropriate constructor from new
            // class,
            // and create new instance.
            newObject = AccessController
                    .doPrivileged(new PrivilegedExceptionAction() {
                        public Object run() throws Exception {
                            Constructor aConstructor = newClass
                                    .getConstructor(types);
                            aConstructor.setAccessible(true);
                            // Now actually create the object.
                            return aConstructor.newInstance(args);
                        }
                    });
        } catch (PrivilegedActionException e) {
            throw e.getException();
        }
        return newObject;
    }
    protected ISharedObject loadSharedObject(SharedObjectDescription desc)
            throws Exception {
        ClassLoader descClassLoader = desc.getClassLoader();
        Map dict = desc.getProperties();
        String[] constructorArgTypes = null;
        Object[] constructorArgs = null;
        if (dict != null) {
            constructorArgTypes = (String[]) dict.get("constructorArgTypes");
            constructorArgs = (Object[]) dict.get("constructorArgs");
        }
        return (ISharedObject) loadObject(
                (descClassLoader == null) ? getSharedObjectClassLoader(desc)
                        : descClassLoader, desc.getClassname(),
                constructorArgTypes, constructorArgs);
    }
    protected ClassLoader getSharedObjectClassLoader(
            SharedObjectDescription desc) {
        return this.getClass().getClassLoader();
    }

    protected ISharedObject addSharedObjectAndWait(SharedObjectDescription sd,
            ISharedObject s, ISharedObjectContainerTransaction t)
            throws Exception {
        if (sd.getID() == null || s == null)
            return null;
        // Wait right here until committed
        ISharedObject so = addSharedObject0(sd, s);
        if (t != null)
            t.waitToCommit();
        return s;
    }
    protected ISharedObject addSharedObject0(SharedObjectDescription sd,
            ISharedObject s) throws Exception {
        addSharedObjectWrapper(makeNewSharedObjectWrapper(sd, s));
        return s;
    }
    protected StandaloneSharedObjectWrapper makeNewSharedObjectWrapper(
            SharedObjectDescription sd, ISharedObject s) {
        StandaloneSharedObjectConfig newConfig = makeNewSharedObjectConfig(sd,
                this);
        return new StandaloneSharedObjectWrapper(newConfig, s, this);
    }
    protected StandaloneSharedObjectConfig makeNewSharedObjectConfig(
            SharedObjectDescription sd, StandaloneContainer cont) {
        ID homeID = sd.getHomeID();
        if (homeID == null)
            homeID = getID();
        return new StandaloneSharedObjectConfig(sd.getID(), homeID, this, sd
                .getProperties());
    }
    protected StandaloneSharedObjectWrapper addSharedObjectWrapper(
            StandaloneSharedObjectWrapper wrapper) throws Exception {
        if (wrapper == null)
            return null;
        ID id = wrapper.getObjID();
        synchronized (sharedObjectTable) {
            if (sharedObjectTable.get(id) != null) {
                throw new SharedObjectAddException("SharedObject with id " + id
                        + " already in use");
            }
            // Put in table
            sharedObjectTable.put(id, wrapper);
            // Call initialize
            wrapper.init();
            // Send activated message
            wrapper.activated(getSharedObjectIDs());
        }
        return wrapper;
    }

    protected void notifySharedObjectActivated(ID activated) {
        synchronized (sharedObjectTable) {
            for (Enumeration e = sharedObjectTable.elements(); e
                    .hasMoreElements();) {
                StandaloneSharedObjectWrapper w = (StandaloneSharedObjectWrapper) e
                        .nextElement();
                if (!activated.equals(w.getObjID())) {
                    w.otherChanged(activated, getSharedObjectIDs(), true);
                }
            }
        }
    }
    protected void notifySharedObjectDeactivated(ID deactivated) {
        synchronized (sharedObjectTable) {
            for (Enumeration e = sharedObjectTable.elements(); e
                    .hasMoreElements();) {
                StandaloneSharedObjectWrapper w = (StandaloneSharedObjectWrapper) e
                        .nextElement();
                if (!deactivated.equals(w.getObjID())) {
                    w.otherChanged(deactivated, getSharedObjectIDs(), false);
                }
            }
        }
    }

    protected Thread getSharedObjectThread(ID id, Runnable target, String name) {
        return new Thread(target, name);
    }
    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#createSharedObject(org.eclipse.ecf.core.SharedObjectDescription)
     */
    public ID createSharedObject(SharedObjectDescription sd,
            ISharedObjectContainerTransaction trans)
            throws SharedObjectCreateException {
        ID result = null;
        try {
            ISharedObject so = loadSharedObject(sd);
            result = sd.getID();
            addSharedObjectAndWait(sd, so, trans);
        } catch (Exception e) {
            throw new SharedObjectCreateException(
                    "Exception creating shared object", e);
        }
        return result;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#addSharedObject(org.eclipse.ecf.identity.ID,
     *      org.eclipse.ecf.core.ISharedObject, java.util.Map,
     *      org.eclipse.ecf.core.ISharedObjectContainerTransaction)
     */
    public ID addSharedObject(ID sharedObjectID, ISharedObject sharedObject,
            Map dict, ISharedObjectContainerTransaction trans)
            throws SharedObjectAddException {
        ID result = null;
        try {
            ISharedObject so = sharedObject;
            result = sharedObjectID;
            SharedObjectDescription sd = new SharedObjectDescription(
                    sharedObject.getClass().getClassLoader(), sharedObjectID,
                    getID(), sharedObject.getClass().getName(), dict, 0);
            addSharedObjectAndWait(sd, so, trans);
        } catch (Exception e) {
            throw new SharedObjectAddException(
                    "Exception creating shared object", e);
        }
        return result;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObjectAdapter(org.eclipse.ecf.identity.ID,
     *      java.lang.Class)
     */
    public Object getSharedObjectAdapter(ID sharedObjectID, Class adapterClass)
            throws SharedObjectNotFoundException {
        ISharedObject so = getSharedObject(sharedObjectID);
        if (so == null)
            throw new SharedObjectNotFoundException("Shared object "
                    + sharedObjectID.getName() + " not found");
        return so.getAdapter(adapterClass);
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getSharedObject(org.eclipse.ecf.identity.ID)
     */
    public ISharedObject getSharedObject(ID sharedObjectID) {
        StandaloneSharedObjectWrapper w = (StandaloneSharedObjectWrapper) sharedObjectTable
                .get(sharedObjectID);
        if (w == null)
            return null;
        else
            return w.sharedObject;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#removeSharedObject(org.eclipse.ecf.identity.ID)
     */
    public ISharedObject removeSharedObject(ID sharedObjectID) {
        StandaloneSharedObjectWrapper w = (StandaloneSharedObjectWrapper) sharedObjectTable
                .remove(sharedObjectID);
        if (w == null)
            return null;
        else
            return w.sharedObject;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#connectSharedObjects(org.eclipse.ecf.identity.ID,
     *      org.eclipse.ecf.identity.ID[])
     */
    public ISharedObjectConnector connectSharedObjects(ID sharedObjectFrom,
            ID[] sharedObjectsTo) throws SharedObjectConnectException {
        // TODO Auto-generated method stub
        return null;
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#disconnectSharedObjects(org.eclipse.ecf.core.ISharedObjectConnector)
     */
    public void disconnectSharedObjects(ISharedObjectConnector connector)
            throws SharedObjectDisconnectException {
        // TODO Auto-generated method stub
    }

    /**
     * Get the sharedObjectConnectors associated with the given sharedObjectID
     * 
     * @return List of ISharedObjectConnector instances
     */
    public List getSharedObjectConnectors(ID sharedObjectFrom) {
        // TODO return actual list contents
        return new ArrayList();
    }

    protected void sendCreate(ID objID, ID containerID, SharedObjectDescription sd) {
        System.out.println("Container.sendCreate("+objID+","+containerID+","+sd+")");
    }
    
    protected void sendMessage(ID objID, ID containerID, byte [] data) {
        System.out.println("Container.sendMessage("+objID+","+containerID+","+new String(data)+")");
    }

    protected void sendMessage(ID objID, ID containerID, Serializable data) {
        System.out.println("Container.sendMessage("+objID+","+containerID+","+data+")");
    }

    protected void sendDispose(ID objID, ID containerID) {
        System.out.println("Container.sendDispose("+objID+","+containerID+")");
    }
    
    protected IOSGIService getServiceAccess() {
        if (context == null) return null;
        else return new OSGIServiceAccessImpl(context);
    }
}
 No newline at end of file