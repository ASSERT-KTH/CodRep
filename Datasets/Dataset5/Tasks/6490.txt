import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.sharedobject;

import java.io.IOException;
import java.util.Map;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.IQueueEnqueue;

/**
 * Context reference provided to all ISharedObjects upon initialization.
 * Implementers of this interface provide a runtime context for ISharedObject
 * instances. Upon initialization within a container (see
 * {@link ISharedObject#init(ISharedObjectConfig)}, ISharedObject instances can
 * access an instance of this context by calling
 * {@link ISharedObjectConfig#getContext()}. They then can have access to the
 * functions provided by this context object for use in implementing their
 * behavior.
 * 
 * @see ISharedObject#init
 * @see ISharedObjectConfig#getContext()
 */
public interface ISharedObjectContext extends IAdaptable {
	public boolean isActive();

	/**
	 * Get the local container instance's ID
	 * 
	 * @return the ID of the enclosing container
	 */
	public ID getLocalContainerID();

	/**
	 * Get the ISharedObjectManager for this context
	 * 
	 * @return ISharedObjectManager the shared object manager instance for this
	 *         container. Null if none available.
	 */
	public ISharedObjectManager getSharedObjectManager();

	/**
	 * Get the IQueueEnqueue instance associated with this ISharedObject. If the
	 * given container provides a queue for this ISharedObject, this method will
	 * return a IQueueEnqueue reference to the appropriate queue.
	 * 
	 * @return IQueueEnqueue instance if an active queue is associated with this
	 *         ISharedObject. If no active queue is associated with the
	 *         ISharedObject, returns null.
	 */
	public IQueueEnqueue getQueue();

	/**
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#connect(ID,IConnectContext)
	 */
	public void connect(ID groupID, IConnectContext connectContext)
			throws ContainerConnectException;

	/**
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect();

	/**
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectedID()
	 */
	public ID getConnectedID();

	/**
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.ISharedObjectContainer#isGroupManager()
	 */
	public boolean isGroupManager();

	/**
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.ISharedObjectContainer#getGroupMemberIDs()
	 */
	public ID[] getGroupMemberIDs();

	/**
	 * Send message to create a remote instance of an ISharedObject with the
	 * same ID as this instance. This method allows ISharedObject instances
	 * (with a reference to a valid ISharedObjectContext) to send messages to
	 * remote containers asking them to create an instance of a new
	 * ISharedObject. The given ReplicaSharedObjectDescription provides the
	 * specification of the new object.
	 * 
	 * @param toContainerID
	 *            the ID of the remote ISharedObjectContainer that is the target
	 *            of the create request. If this parameter is null, the request
	 *            is assumed to be made of <b>all </b> remote containers
	 *            currently in the given group (excepting the local container).
	 * @param sd
	 *            the ReplicaSharedObjectDescription describing the class,
	 *            constructor and other properties to be associated with the new
	 *            instance
	 * @throws IOException
	 *             thrown if message cannot be sent by container
	 */
	public void sendCreate(ID toContainerID, ReplicaSharedObjectDescription sd)
			throws IOException;

	/**
	 * Send create response back to an ISharedObject with the same ID as this
	 * instance. This method allows ISharedObject instances (with a reference to
	 * a valid ISharedObjectContext) to send messages to remote containers
	 * asking them to deliver the create response status back to the
	 * ISharedObject.
	 * 
	 * @param toContainerID
	 *            the ID of the container that is to receive this response
	 * @param throwable
	 *            a throwable associated with the creation. Null means that no
	 *            exception occured
	 * @param identifier
	 *            the identifier used in the original create message (in the
	 *            shared object description)
	 * @exception IOException
	 *                thrown if the create response cannot be sent
	 */
	public void sendCreateResponse(ID toContainerID, Throwable throwable,
			long identifier) throws IOException;

	/**
	 * Send message to dispose of a remote instance of the ISharedObject with
	 * same ID as this instance. This method allows ISharedObject instances to
	 * control the destruction of remote replicas.
	 * 
	 * @param toContainerID
	 *            the ID of the remote ISharedObjectContainer that is the target
	 *            of the dispose request. If this parameter is null, the request
	 *            is assumed to be made of <b>all </b> remote containers
	 *            currently in the given group (excepting the local container).
	 * @throws IOException
	 *             thrown if message cannot be sent by container
	 */
	public void sendDispose(ID toContainerID) throws IOException;

	/**
	 * Send arbitrary message to remote instance of the ISharedObject with same
	 * ID as this instance. This method allows ISharedObject instances to send
	 * arbitrary data to one or more remote replicas of this ISharedObject.
	 * 
	 * @param toContainerID
	 *            the ID of the remote ISharedObjectContainer that is the target
	 *            container for the message request. If this parameter is null,
	 *            the request is assumed to be made of <b>all </b> remote
	 *            containers currently in the given group (excepting the local
	 *            container).
	 * @param data
	 *            arbitrary message object. The allowable types of this
	 *            parameter are dependent upon the type of the underlying
	 *            implementing container
	 * @throws IOException
	 *             thrown if message cannot be sent by container, or if data
	 *             cannot be serialized
	 */
	public void sendMessage(ID toContainerID, Object data) throws IOException;

	/**
	 * Get the Namespace instance that defines the ID type expected by the
	 * remote target container
	 * 
	 * @return Namespace the namespace by the target for a call to connect().
	 *         Null if container namespace no longer available
	 */
	public Namespace getConnectNamespace();

	/**
	 * Get local container properties that it wishes to expose to shared object
	 * access
	 * 
	 * @return Map of properties available to calling shared object. Map
	 *         returned must not be null.
	 */
	public Map getLocalContainerProperties();
}
 No newline at end of file