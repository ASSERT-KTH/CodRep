public interface IContainer extends IAdaptable, IIdentifiable {

package org.eclipse.ecf.core;

import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.IJoinContext;

/**
 * Distributed container contract
 */
public interface IContainer extends IAdaptable {

	/**
	 * Join a container group. The group to join is identified by the first
	 * parameter (groupID) using any required authentication provided via the
	 * second parameter (joinContext). This method provides an implementation
	 * independent way for container implementations to connect, authenticate,
	 * and communicate with a remote service or group of services. Providers are
	 * responsible for implementing this operation in a way appropriate to the
	 * given remote service and expected protocol.
	 * 
	 * @param groupID
	 *            the ID of the remote service to join
	 * @param joinContext
	 *            any required context to allow this container to authenticate
	 *            on join with remote containers
	 * @exception ContainerJoinException
	 *                thrown if communication cannot be established with remote
	 *                service
	 */
	public void joinGroup(ID groupID, IJoinContext joinContext)
			throws ContainerJoinException;

	/**
	 * Get the group id that this container has joined. Return null if no group
	 * has previously been joined.
	 * 
	 * @return ID of the group previously joined
	 */
	public ID getGroupID();

	/**
	 * Leave a container group. This operation will disconnect the local
	 * container instance from any previously joined group.
	 */
	public void leaveGroup();

	/**
	 * Dispose this ISharedObjectContainer instance. The container instance will
	 * be made inactive after the completion of this method and will be
	 * unavailable for subsequent usage
	 * 
	 * @param waittime
	 */
	public void dispose(long waittime);


}