fireContainerEvent(new ContainerEjectedEvent(getID(), fromID, e.getException()));

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

import java.io.IOException;
import java.io.Serializable;
import java.net.*;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.IConnectHandlerPolicy;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerGroupManager;
import org.eclipse.ecf.internal.provider.Messages;
import org.eclipse.ecf.provider.comm.*;
import org.eclipse.ecf.provider.generic.gmm.Member;

public class ServerSOContainer extends SOContainer implements ISharedObjectContainerGroupManager {

	protected IConnectHandlerPolicy connectHandlerPolicy;

	public ServerSOContainer(ISharedObjectContainerConfig config) {
		super(config);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#isGroupManager()
	 */
	public boolean isGroupManager() {
		return true;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#getConnectedID()
	 */
	public ID getConnectedID() {
		return getID();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#disconnect()
	 */
	public void disconnect() {
		ejectAllGroupMembers(null);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.ISharedObjectContainerGroupManager#ejectGroupMember(org.eclipse.ecf.core.identity.ID,
	 *      java.io.Serializable)
	 */
	public void ejectGroupMember(ID memberID, Serializable reason) {
		if (memberID == null)
			return;
		ISynchConnection conn = null;
		synchronized (getGroupMembershipLock()) {
			conn = getSynchConnectionForID(memberID);
			if (conn == null)
				return;
			try {
				conn.sendSynch(memberID, serialize(ContainerMessage.createLeaveGroupMessage(getID(), memberID, getNextSequenceNumber(), reason)));
			} catch (final Exception e) {
				traceStack("Exception in ejectGroupMember.sendAsynch()", e); //$NON-NLS-1$
			}
			handleLeave(memberID, conn);
		}
		// Notify listeners
		fireContainerEvent(new ContainerEjectedEvent(memberID, getID(), reason));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.ISharedObjectContainerGroupManager#ejectAllGroupMembers(java.io.Serializable)
	 */
	public void ejectAllGroupMembers(Serializable reason) {
		synchronized (getGroupMembershipLock()) {
			final Object[] members = groupManager.getMembers();
			for (int i = 0; i < members.length; i++) {
				ejectGroupMember(((Member) members[i]).getID(), reason);
			}
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#dispose()
	 */
	public void dispose() {
		// For servers, we'll eject all members
		ejectAllGroupMembers(null);
		super.dispose();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID groupID, IConnectContext joinContext) throws ContainerConnectException {
		final ContainerConnectException e = new ContainerConnectException(Messages.ServerSOContainer_Server_Application_Cannot_Connect + groupID.getName());
		throw e;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.sharedobject.ISharedObjectContainerGroupManager#setConnectPolicy(org.eclipse.ecf.core.security.IConnectHandlerPolicy)
	 */
	public void setConnectPolicy(IConnectHandlerPolicy policy) {
		synchronized (getGroupMembershipLock()) {
			this.connectHandlerPolicy = policy;
		}
	}

	protected void queueContainerMessage(ContainerMessage message) throws IOException {
		if (message.getToContainerID() == null) {
			queueToAll(message);
		} else {
			final IAsynchConnection conn = getConnectionForID(message.getToContainerID());
			if (conn != null)
				conn.sendAsynch(message.getToContainerID(), serialize(message));
		}
	}

	protected void forwardToRemote(ID from, ID to, ContainerMessage data) throws IOException {
		queueContainerMessage(new ContainerMessage(from, to, getNextSequenceNumber(), data.getData()));
	}

	protected void forwardExcluding(ID from, ID excluding, ContainerMessage data) throws IOException {
		if (excluding == null) {
			queueContainerMessage(new ContainerMessage(from, null, getNextSequenceNumber(), data.getData()));
		} else {
			final Object ms[] = groupManager.getMembers();
			for (int i = 0; i < ms.length; i++) {
				final Member m = (Member) ms[i];
				final ID oldID = m.getID();
				if (!excluding.equals(oldID) && !from.equals(oldID)) {
					final IAsynchConnection conn = (IAsynchConnection) m.getData();
					if (conn != null) {
						try {
							conn.sendAsynch(oldID, serialize(new ContainerMessage(from, oldID, getNextSequenceNumber(), data.getData())));
						} catch (final IOException e) {
							traceStack("Exception in forwardExcluding from " //$NON-NLS-1$
									+ from + " with oldID " + oldID, e); //$NON-NLS-1$
						}
					}
				}
			}
		}
	}

	/**
	 * @param mess
	 * @throws IOException not thrown by this implementation.
	 */
	protected void handleViewChangeMessage(ContainerMessage mess) throws IOException {
		// ServerApplication should never receive change messages
		debug("handleViewChangeMessage(" + mess + ")"); //$NON-NLS-1$ //$NON-NLS-2$
	}

	protected ContainerMessage acceptNewClient(Socket socket, String target, Serializable data, ISynchAsynchConnection conn) {
		debug("acceptNewClient(" + socket + "," + target + "," + data + "," + conn + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$ //$NON-NLS-5$
		ContainerMessage connectMessage = null;
		ID remoteID = null;
		try {
			connectMessage = (ContainerMessage) data;
			if (connectMessage == null)
				throw new NullPointerException(Messages.ServerSOContainer_Connect_Request_Null);
			remoteID = connectMessage.getFromContainerID();
			if (remoteID == null)
				throw new NullPointerException(Messages.ServerSOContainer_FromID_Null);
			final ContainerMessage.JoinGroupMessage jgm = (ContainerMessage.JoinGroupMessage) connectMessage.getData();
			if (jgm == null)
				throw new NullPointerException(Messages.ServerSOContainer_Connect_Request_Null);
			ID memberIDs[] = null;
			synchronized (getGroupMembershipLock()) {
				if (isClosing) {
					final Exception e = new IllegalStateException(Messages.ServerSOContainer_Server_Closing);
					throw e;
				}
				// Now check to see if this request is going to be allowed
				checkJoin(socket.getRemoteSocketAddress(), remoteID, target, jgm.getData());

				// Here we check to see if the given remoteID is already
				// connected,
				// if it is, then we close the old connection and cleanup
				final ISynchConnection oldConn = getSynchConnectionForID(remoteID);
				if (oldConn != null)
					handleLeave(remoteID, oldConn);
				// Now we add the new connection
				if (addNewRemoteMember(remoteID, conn)) {
					// Notify existing remotes about new member
					try {
						forwardExcluding(getID(), remoteID, ContainerMessage.createViewChangeMessage(getID(), remoteID, getNextSequenceNumber(), new ID[] {remoteID}, true, null));
					} catch (final IOException e) {
						traceStack("Exception in acceptNewClient sending view change message", e); //$NON-NLS-1$
					}
					// Get current membership
					memberIDs = groupManager.getMemberIDs();
					// Start messaging to new member
					conn.start();
				} else {
					final ConnectException e = new ConnectException(Messages.ServerSOContainer_Exception_Server_Refused);
					throw e;
				}
			}
			// notify listeners
			fireContainerEvent(new ContainerConnectedEvent(this.getID(), remoteID));

			return ContainerMessage.createViewChangeMessage(getID(), remoteID, getNextSequenceNumber(), memberIDs, true, null);
		} catch (final Exception e) {
			traceStack("Exception in acceptNewClient(" + socket + "," //$NON-NLS-1$ //$NON-NLS-2$
					+ target + "," + data + "," + conn, e); //$NON-NLS-1$ //$NON-NLS-2$
			// And then return leave group message...which means refusal
			return ContainerMessage.createViewChangeMessage(getID(), remoteID, getNextSequenceNumber(), null, false, e);
		}
	}

	protected Object checkJoin(SocketAddress saddr, ID fromID, String target, Serializable data) throws Exception {
		if (this.connectHandlerPolicy != null) {
			return this.connectHandlerPolicy.checkConnect(saddr, fromID, getID(), target, data);
		}
		return null;
	}

	protected void handleLeaveGroupMessage(ContainerMessage mess) {
		final ID fromID = mess.getFromContainerID();
		if (fromID == null)
			return;
		synchronized (getGroupMembershipLock()) {
			final IAsynchConnection conn = getConnectionForID(fromID);
			if (conn == null)
				return;
			handleLeave(fromID, conn);
		}
		// Notify listeners
		fireContainerEvent(new ContainerDisconnectedEvent(getID(), fromID));
	}

	// Support methods
	protected ID getIDForConnection(IAsynchConnection conn) {
		final Object ms[] = groupManager.getMembers();
		for (int i = 0; i < ms.length; i++) {
			final Member m = (Member) ms[i];
			if (conn == (IAsynchConnection) m.getData())
				return m.getID();
		}
		return null;
	}

	protected IAsynchConnection getConnectionForID(ID memberID) {
		final Member mem = groupManager.getMemberForID(memberID);
		if (mem == null || !(mem.getData() instanceof IAsynchConnection))
			return null;
		return (IAsynchConnection) mem.getData();
	}

	protected ISynchConnection getSynchConnectionForID(ID memberID) {
		final Member mem = groupManager.getMemberForID(memberID);
		if (mem == null || !(mem.getData() instanceof ISynchConnection))
			return null;

		return (ISynchConnection) mem.getData();
	}

	private final void queueToAll(ContainerMessage message) {
		final Object[] members = groupManager.getMembers();
		for (int i = 0; i < members.length; i++) {
			final IAsynchConnection conn = (IAsynchConnection) ((Member) members[i]).getData();
			if (conn != null) {
				try {
					conn.sendAsynch(message.getToContainerID(), serialize(message));
				} catch (final IOException e) {
					traceStack("Exception in queueToAll for ContainerMessage " + message, e); //$NON-NLS-1$
				}
			}
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#processDisconnect(org.eclipse.ecf.provider.comm.DisconnectEvent)
	 */
	protected void processDisconnect(DisconnectEvent e) {
		final IAsynchConnection conn = (IAsynchConnection) e.getConnection();

		ID fromID = null;
		synchronized (getGroupMembershipLock()) {
			fromID = getIDForConnection(conn);
			if (fromID == null)
				return;
			handleLeave(fromID, conn);
		}
		if (fromID != null)
			fireContainerEvent(new ContainerDisconnectedEvent(getID(), fromID));
	}

}
 No newline at end of file