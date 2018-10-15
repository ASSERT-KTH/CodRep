public ID[] getGroupMemberIDs();

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core;

import org.eclipse.ecf.core.identity.ID;

/**
 * Core interface that must be implemented by all ECF container instances.
 * Instances are typically
 * created via {@link SharedObjectContainerFactory}  
 */
public interface ISharedObjectContainer {

    /**
     * Return the ISharedObjectContainerConfig for this ISharedObjectContainer.
     * The returned value must always be non-null.
     * 
     * @return ISharedObjectContainerConfig for the given ISharedObjectContainer
     *         instance
     */
    public ISharedObjectContainerConfig getConfig();
    /**
     * Add listener to ISharedObjectContainer. Listener will be notified when
     * container events occur
     * 
     * @param l
     *            the ISharedObjectContainerListener to add
     * @param filter
     * 			  the filter to define types of container events to receive
     */
    public void addListener(ISharedObjectContainerListener l, String filter);
    /**
     * Remove listener from ISharedObjectContainer.
     * 
     * @param l
     *            the ISharedObjectContainerListener to remove
     */
    public void removeListener(ISharedObjectContainerListener l);
    /**
     * Dispose this ISharedObjectContainer instance. The container instance
     * will be made inactive after the completion of this method and will be
     * unavailable for subsequent usage
     * 
     * @param waittime
     */
    public void dispose(long waittime);
    /**
     * Join a container group. The group to join is identified by the first
     * parameter (groupID) using any required authentication provided via the
     * second parameter (loginData). This method provides an implementation
     * independent way for container implementations to connect, authenticate,
     * and communicate with a remote service or group of services. Providers are
     * responsible for implementing this operation in a way appropriate to the
     * given remote service and expected protocol.
     * 
     * @param groupID
     *            the ID of the remote service to join
     * @param loginData
     *            any required login/authentication data to allow this container
     *            to authenticate
     * @exception SharedObjectContainerJoinException
     *                thrown if communication cannot be established with remote
     *                service
     */
    public void joinGroup(ID groupID, Object loginData)
            throws SharedObjectContainerJoinException;
    /**
     * Leave a container group. This operation will disconnect the local
     * container instance from any previously joined group.
     */
    public void leaveGroup();
    /**
     * Get the group id that this container has joined. Return null if no group has
     * previously been joined.
     * 
     * @return ID of the group previously joined
     */
    public ID getGroupID();
    /**
     * Get the current membership of the joined group. This method will
     * accurately report the current group membership of the connected group.
     * 
     * @return ID[] the IDs of the current group membership
     */
    public ID[] getGroupMembership();
    /**
     * @return true if this ISharedObjectContainer instance is in the
     *         'manager' role for the group, false otherwise
     */
    public boolean isGroupManager();
    /**
     * @return true if this ISharedObjectContainer instance is in a server
     *         role for the group, false otherwise
     */
    public boolean isGroupServer();
    
    /**
     * Get SharedObjectManager for this container
     * 
     * @return ISharedObjectManager for this container instance
     */
    public ISharedObjectManager getSharedObjectManager();
    
    /**
     * Returns an object which is an instance of the given class associated with
     * this object.
     * 
     * @param adapter
     *            the adapter class to lookup
     * @return Object a object castable to the given class, or null if this
     *         object does not have an adapter for the given class
     */
    public Object getAdapter(Class adapter);

}
 No newline at end of file