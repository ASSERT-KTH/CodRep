public void leaveGroup();

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core;

import java.io.IOException;
import java.io.Serializable;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.QueueEnqueue;

/**
 * Context reference provided to all ISharedObjects upon initialization.  Implementers of
 * this interface provide a runtime context for ISharedObject instances.  Upon initialization
 * within a container (see {@link ISharedObject#init(ISharedObjectConfig)}, ISharedObject instances
 * can access an instance of this context by calling {@link ISharedObjectConfig#getContext()}.  They
 * then can have access to the functions provided by this context object for use in implementing
 * their behavior.
 *
 * @see ISharedObject#init
 * @see ISharedObjectConfig#getContext()
 */
public interface ISharedObjectContext {

    /**
     * Get the local container instance's ID
     * 
     * @return the ID of the enclosing container
     */
    public ID getContainerID();
    /**
     * Get the ISharedObjectManager for this context
     * @return ISharedObjectManager the shared object manager instance for this
     * container.  Null if none available.
     */
    public ISharedObjectManager getSharedObjectManager();
    /**
     * Get the QueueEnqueue instance associated with this ISharedObject. If the
     * given container provides a queue for this ISharedObject, this method will
     * return a QueueEnqueue reference to the appropriate queue.
     * 
     * @return QueueEnqueue instance if an active queue is associated with this
     *         ISharedObject. If no active queue is associated with the
     *         ISharedObject, returns null.
     *  
     */
    public QueueEnqueue getQueue();

    /**
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#joinGroup(org.eclipse.ecf.core.identity.ID,
     *      java.lang.Object)
     */
    public void joinGroup(ID groupID, Object loginData)
            throws SharedObjectContainerJoinException;
    /**
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#leaveGroup()
     */
    public Object leaveGroup();

    /**
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupID()
     */
    public ID getGroupID();
    /**
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupManager()
     */
    public boolean isGroupManager();
    /**
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#isGroupServer()
     */
    public boolean isGroupServer();
    /**
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.core.ISharedObjectContainer#getGroupMembership()
     */
    public ID[] getGroupMembership();

    /**
     * Send message to create a remote instance of an ISharedObject with the
     * same ID as this instance (ISharedObject.getID() returns same unique
     * value). This method allows ISharedObject instances (with a reference to a
     * valid ISharedObjectContext) to send messages to remote containers asking
     * them to create an instance of a new ISharedObject. The given
     * ISharedObjectDescription provides the specification of the new object.
     * 
     * @param toContainerID
     *            the ID of the remote ISharedObjectContainer that is the target
     *            of the create request. If this parameter is null, the request
     *            is assumed to be made of <b>all </b> remote containers
     *            currently in the given group (excepting the local container).
     * 
     * @param sd
     *            the SharedObjectDescription describing the class, constructor
     *            and other properties to be associated with the new instance
     * 
     * @throws IOException
     *             thrown if message cannot be sent by container
     */
    public void sendCreate(ID toContainerID, SharedObjectDescription sd)
            throws IOException;
    /**
     * Send message to dispose of a remote instance of the ISharedObject with
     * same ID as this instance (ISharedObject.getID() returns same unique
     * value). This method allows ISharedObject instances to control the
     * destruction of remote replicas.
     * 
     * @param toContainerID
     *            the ID of the remote ISharedObjectContainer that is the target
     *            of the dispose request. If this parameter is null, the request
     *            is assumed to be made of <b>all </b> remote containers
     *            currently in the given group (excepting the local container).
     * 
     * @throws IOException
     *             thrown if message cannot be sent by container
     */
    public void sendDispose(ID toContainerID) throws IOException;
    /**
     * Send arbitrary message to remote instance of the ISharedObject with same
     * ID as this instance (ISharedObject.getID() returns same unique value).
     * This method allows ISharedObject instances to send arbitrary data to one
     * or more remote replicas of this ISharedObject.
     * 
     * @param toContainerID
     *            the ID of the remote ISharedObjectContainer that is the target
     *            container for the message request. If this parameter is null,
     *            the request is assumed to be made of <b>all </b> remote
     *            containers currently in the given group (excepting the local
     *            container).
     * 
     * @throws IOException
     *             thrown if message cannot be sent by container
     */
    public void sendMessage(ID toContainerID, byte[] data) throws IOException;
    /**
     * Send arbitrary message to remote instance of the ISharedObject with same
     * ID as this instance (ISharedObject.getID() returns same unique value).
     * This method allows ISharedObject instances to send arbitrary data to one
     * or more remote replicas of this ISharedObject.
     * 
     * @param toContainerID
     *            the ID of the remote ISharedObjectContainer that is the target
     *            container for the message request. If this parameter is null,
     *            the request is assumed to be made of <b>all </b> remote
     *            containers currently in the given group (excepting the local
     *            container).
     * 
     * @throws IOException
     *             thrown if message cannot be sent by container, or if data
     *             cannot be serialized
     */
    public void sendMessage(ID toContainerID, Serializable data)
            throws IOException;

    /**
     * Returns an object which is an instance of the given class associated with
     * this object.
     * 
     * @param clazz
     *            the adapter class to lookup
     * @return Object a object castable to the given class, or null if this
     *         object does not have an adapter for the given class
     */
    public Object getAdapter(Class clazz);

    /**
     * Get a reference to a proxy instance that allows the registration and
     * access to local OSGI-platform-provided services. If this method returns
     * null, then such services are not available.
     * 
     * @return null if OSGI platform services cannot be accessed, a valid
     *         instance of the given interface if the context allows access to
     *         such services
     */
    public IOSGIService getServiceAccess();
}
 No newline at end of file