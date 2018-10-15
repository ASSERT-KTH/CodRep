import org.eclipse.ecf.core.sharedobject.security.ISharedObjectPolicy;

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

/*
 * Created on Dec 20, 2004
 *  
 */
package org.eclipse.ecf.provider.generic;

import java.lang.reflect.Constructor;
import java.security.AccessController;
import java.security.PrivilegedExceptionAction;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.Map;
import java.util.Vector;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.security.ISharedObjectPolicy;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectConnector;
import org.eclipse.ecf.core.sharedobject.ISharedObjectManager;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.core.sharedobject.SharedObjectConnectException;
import org.eclipse.ecf.core.sharedobject.SharedObjectCreateException;
import org.eclipse.ecf.core.sharedobject.SharedObjectDescription;
import org.eclipse.ecf.core.sharedobject.SharedObjectDisconnectException;
import org.eclipse.ecf.core.sharedobject.SharedObjectFactory;
import org.eclipse.ecf.core.sharedobject.SharedObjectTypeDescription;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectManagerAddEvent;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectManagerConnectEvent;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectManagerCreateEvent;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectManagerDisconnectEvent;
import org.eclipse.ecf.core.sharedobject.events.SharedObjectManagerRemoveEvent;
import org.eclipse.ecf.core.util.AbstractFactory;
import org.eclipse.ecf.core.util.IQueueEnqueue;
import org.eclipse.ecf.provider.Trace;

/**
 * 
 */
public class SOManager implements ISharedObjectManager {
	private static final int GUID_SIZE = 20;

	static Trace debug = Trace.create("sharedobjectmanager");

	SOContainer container = null;
	Vector connectors = null;

	public SOManager(SOContainer cont) {
		super();
		this.container = cont;
		connectors = new Vector();
	}

	protected void debug(String msg) {
		if (Trace.ON && debug != null) {
			debug.msg(msg + ":" + container.getID());
		}
	}

	protected void dumpStack(String msg, Throwable e) {
		if (Trace.ON && debug != null) {
			debug.dumpStack(e, msg + ":" + container.getID());
		}
	}

	protected void addConnector(ISharedObjectConnector conn) {
		connectors.add(conn);
	}

	protected boolean removeConnector(ISharedObjectConnector conn) {
		return connectors.remove(conn);
	}

	protected List getConnectors() {
		return connectors;
	}

	protected Class[] getArgTypes(String[] argTypes, Object[] args,
			ClassLoader cl) throws ClassNotFoundException {
		return AbstractFactory.getClassesForTypes(argTypes, args, cl);
	}

	protected ISharedObject createSharedObjectInstance(final Class newClass,
			final Class[] argTypes, final Object[] args) throws Exception {
		Object newObject = null;
		try {
			newObject = AccessController
					.doPrivileged(new PrivilegedExceptionAction() {
						public Object run() throws Exception {
							Constructor aConstructor = newClass
									.getConstructor(argTypes);
							aConstructor.setAccessible(true);
							return aConstructor.newInstance(args);
						}
					});
		} catch (java.security.PrivilegedActionException e) {
			throw e.getException();
		}
		return verifySharedObject(newObject);
	}

	protected ISharedObject verifySharedObject(Object newSharedObject) {
		if (newSharedObject instanceof ISharedObject)
			return (ISharedObject) newSharedObject;
		else
			throw new ClassCastException("Object " + newSharedObject.toString()
					+ " does not implement " + ISharedObject.class.getName());
	}

	protected ISharedObject loadSharedObject(SharedObjectDescription sd)
			throws Exception {
		if (sd == null) throw new NullPointerException("SharedObjectDescription cannot be null");
		// Then get args array from properties
		Object[] args = container.getArgsFromProperties(sd);
		// And arg types
		String[] types = container.getArgTypesFromProperties(sd);
		ISharedObject res = null;
		SharedObjectTypeDescription typeDesc = sd.getTypeDescription();
		String descName = typeDesc.getName();
		if (descName == null) {
			// First get classloader
			ClassLoader cl = container.getClassLoaderForSharedObject(sd);
			final Class newClass = Class.forName(typeDesc.getClassName(), true, cl);
			Class [] argTypes = getArgTypes(types, args, cl);
			res = createSharedObjectInstance(newClass, argTypes, args);
			// 'new style'
		} else {
			res = SharedObjectFactory.getDefault().createSharedObject(typeDesc, types, args);
		}
		return res;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#getSharedObjectIDs()
	 */
	public ID[] getSharedObjectIDs() {
		return container.getSharedObjectIDs();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#createSharedObject(org.eclipse.ecf.core.SharedObjectDescription)
	 */
	public ID createSharedObject(SharedObjectDescription sd)
			throws SharedObjectCreateException {
		debug("createSharedObject(" + sd + ")");
		// notify listeners
		if (sd == null)
			throw new SharedObjectCreateException(
					"SharedObjectDescription cannot be null");
		container.fireContainerEvent(new SharedObjectManagerCreateEvent(
				container.getID(), sd));
		ISharedObject newObject = null;
		ID result = null;
		try {
			newObject = loadSharedObject(sd);
			ID newID = createNewSharedObjectID(sd,newObject);
			result = addSharedObject(newID,newObject, sd
					.getProperties());
		} catch (Exception e) {
			dumpStack("Exception in createSharedObject", e);
			SharedObjectCreateException newExcept = new SharedObjectCreateException(
					"Container " + container.getID()
							+ " had exception creating shared object "
							+ sd.getID() + ": " + e.getClass().getName()
							+ ": " + e.getMessage());
			newExcept.setStackTrace(e.getStackTrace());
			throw newExcept;
		}
		return result;
	}

	protected ID createNewSharedObjectID(SharedObjectDescription sd, ISharedObject newObject) throws IDCreateException {
		ID descID = sd.getID();
		if (descID == null) {
			return IDFactory.getDefault().createGUID(GUID_SIZE);
		} else return descID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#addSharedObject(org.eclipse.ecf.core.ISharedObject, java.util.Map,
	 *      org.eclipse.ecf.core.ISharedObjectContainerTransaction)
	 */
	public ID addSharedObject(ID sharedObjectID, ISharedObject sharedObject,
			Map properties) throws SharedObjectAddException {
		debug("addSharedObject(" + sharedObjectID + "," + sharedObject + ","
				+ properties + ")");
		// notify listeners
		container.fireContainerEvent(new SharedObjectManagerAddEvent(container
				.getID(), sharedObjectID, sharedObject, properties));
		ID result = sharedObjectID;
		try {
			ISharedObject so = sharedObject;
			container.addSharedObjectAndWait(sharedObjectID, so, properties);
		} catch (Exception e) {
			dumpStack("Exception in addSharedObject", e);
			SharedObjectAddException newExcept = new SharedObjectAddException(
					"Container " + container.getID()
							+ " had exception adding shared object "
							+ sharedObjectID + ": " + e.getClass().getName()
							+ ": " + e.getMessage());
			newExcept.setStackTrace(e.getStackTrace());
			throw newExcept;
		}
		return result;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#getSharedObject(org.eclipse.ecf.core.identity.ID)
	 */
	public ISharedObject getSharedObject(ID sharedObjectID) {
		return container.getSharedObject(sharedObjectID);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#removeSharedObject(org.eclipse.ecf.core.identity.ID)
	 */
	public ISharedObject removeSharedObject(ID sharedObjectID) {
		debug("removeSharedObject(" + sharedObjectID + ")");
		// notify listeners
		container.fireContainerEvent(new SharedObjectManagerRemoveEvent(
				container.getID(), sharedObjectID));
		return container.removeSharedObject(sharedObjectID);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#connectSharedObjects(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.identity.ID[])
	 */
	public ISharedObjectConnector connectSharedObjects(ID sharedObjectFrom,
			ID[] sharedObjectsTo) throws SharedObjectConnectException {
		debug("connectSharedObjects(" + sharedObjectFrom + ","
				+ sharedObjectsTo + ")");
		// notify listeners
		container.fireContainerEvent(new SharedObjectManagerConnectEvent(
				container.getID(), sharedObjectFrom, sharedObjectsTo));
		if (sharedObjectFrom == null)
			throw new SharedObjectConnectException("sender cannot be null");
		if (sharedObjectsTo == null)
			throw new SharedObjectConnectException("receivers cannot be null");
		ISharedObjectConnector result = null;
		synchronized (container.getGroupMembershipLock()) {
			// Get from to create sure it's there
			SOWrapper wrap = container.getSharedObjectWrapper(sharedObjectFrom);
			if (wrap == null)
				throw new SharedObjectConnectException("sender object "
						+ sharedObjectFrom.getName() + " not found");
			IQueueEnqueue[] queues = new IQueueEnqueue[sharedObjectsTo.length];
			for (int i = 0; i < sharedObjectsTo.length; i++) {
				SOWrapper w = container
						.getSharedObjectWrapper(sharedObjectsTo[i]);
				if (w == null)
					throw new SharedObjectConnectException("receiver object "
							+ sharedObjectsTo[i].getName() + " not found");
				queues[i] = new QueueEnqueueImpl(w.getQueue());
			}
			// OK now we've got ids and wrappers, create a connector
			result = new SOConnector(sharedObjectFrom, sharedObjectsTo, queues);
			addConnector(result);
		}
		return result;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#disconnectSharedObjects(org.eclipse.ecf.core.ISharedObjectConnector)
	 */
	public void disconnectSharedObjects(ISharedObjectConnector connector)
			throws SharedObjectDisconnectException {
		if (connector != null) {
			debug("disconnectSharedObjects(" + connector.getSender() + ")");
			// notify listeners
			container
					.fireContainerEvent(new SharedObjectManagerDisconnectEvent(
							container.getID(), connector.getSender()));
		}
		if (connector == null)
			throw new SharedObjectDisconnectException("connect cannot be null");
		if (!removeConnector(connector)) {
			throw new SharedObjectDisconnectException("connector " + connector
					+ " not found");
		}
		connector.dispose();
	}

	protected void dispose() {
		debug("dispose()");
		for (Enumeration e = connectors.elements(); e.hasMoreElements();) {
			ISharedObjectConnector conn = (ISharedObjectConnector) e
					.nextElement();
			conn.dispose();
		}
		connectors.clear();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.ISharedObjectManager#getSharedObjectConnectors(org.eclipse.ecf.core.identity.ID)
	 */
	public List getSharedObjectConnectors(ID sharedObjectFrom) {
		debug("getSharedObjectConnectors(" + sharedObjectFrom + ")");
		List results = new ArrayList();
		for (Enumeration e = connectors.elements(); e.hasMoreElements();) {
			ISharedObjectConnector conn = (ISharedObjectConnector) e
					.nextElement();
			if (sharedObjectFrom.equals(conn.getSender())) {
				results.add(conn);
			}
		}
		return results;
	}

	public static Class[] getClassesForTypes(String[] argTypes, Object[] args,
			ClassLoader cl) throws ClassNotFoundException {
		Class clazzes[] = null;
		if (args == null || args.length == 0)
			clazzes = new Class[0];
		else if (argTypes != null) {
			clazzes = new Class[argTypes.length];
			for (int i = 0; i < argTypes.length; i++) {
				clazzes[i] = Class.forName(argTypes[i], true, cl);
			}
		} else {
			clazzes = new Class[args.length];
			for (int i = 0; i < args.length; i++) {
				if (args[i] == null)
					clazzes[i] = null;
				else
					clazzes[i] = args[i].getClass();
			}
		}
		return clazzes;
	}

	public void setRemoteAddPolicy(ISharedObjectPolicy policy) {
		container.setRemoteAddPolicy(policy);
	}
}
 No newline at end of file