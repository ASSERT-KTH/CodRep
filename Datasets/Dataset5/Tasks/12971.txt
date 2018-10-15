groupManager.removeNonLocalMembers();

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
import java.io.InvalidObjectException;
import java.io.Serializable;
import java.net.ConnectException;
import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.SharedObjectContainerJoinException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.comm.AsynchConnectionEvent;
import org.eclipse.ecf.core.comm.ConnectionInstantiationException;
import org.eclipse.ecf.core.comm.DisconnectConnectionEvent;
import org.eclipse.ecf.core.comm.IAsynchConnection;
import org.eclipse.ecf.core.comm.IConnection;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.comm.SynchConnectionEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.provider.generic.gmm.Member;

public abstract class ClientSOContainer extends SOContainer {
    ISynchAsynchConnection connection;
    ID remoteServerID;
    byte connectionState;
    public static final byte UNCONNECTED = 0;
    public static final byte CONNECTING = 1;
    public static final byte CONNECTED = 2;

    static final class Lock {
    }

    Lock connectLock;

    public ClientSOContainer(ISharedObjectContainerConfig config) {
        super(config);
        connection = null;
        connectionState = UNCONNECTED;
        connectLock = new Lock();
    }

    public void dispose(long wait) {
        synchronized (connectLock) {
            isClosing = true;
            if (isConnected()) {
                this.leaveGroup();
            } else if (isConnecting()) {
                killConnection(connection);
            }
            remoteServerID = null;
        }
        super.dispose(wait);
    }

    public final boolean isGroupServer() {
        return false;
    }

    public final boolean isGroupManager() {
        return false;
    }

    public ID getGroupID() {
        return remoteServerID;
    }

    public void joinGroup(ID remote, Object data)
            throws SharedObjectContainerJoinException {
        try {
            if (isClosing)
                throw new IllegalStateException("container is closing");
            debug("joingroup:" + remote + ":" + data);
            ISynchAsynchConnection aConnection = getClientConnection(remote,
                    data);
            if (aConnection == null) {
                ConnectException c = new ConnectException("join failed to"
                        + ":" + remote.getName());
                throw c;
            }
            ContainerMessage response;
            synchronized (connectLock) {
                if (isConnected()) {
                    killConnection(aConnection);
                    aConnection = null;
                    ConnectException c = new ConnectException(
                            "already connected to " + getGroupID());
                    throw c;
                }
                if (isConnecting()) {
                    killConnection(aConnection);
                    aConnection = null;
                    ConnectException c = new ConnectException(
                            "currently connecting");
                    throw c;
                }
                connectionState = CONNECTING;
                connection = aConnection;
            }
            synchronized (aConnection) {
                try {
                    Object connectData = getConnectData(remote, data);
                    response = (ContainerMessage) aConnection.connect(remote,
                            connectData, 0);
                } catch (IOException e) {
                    synchronized (connectLock) {
                        killConnection(aConnection);
                        if (connection != aConnection) {
                            aConnection = null;
                            throw e;
                        }
                        connectionState = UNCONNECTED;
                        connection = null;
                        remoteServerID = null;
                    }
                    throw e;
                }
                synchronized (connectLock) {
                    // If not in correct state, disconnect and return
                    if (connection != aConnection) {
                        killConnection(aConnection);
                        aConnection = null;
                        ConnectException c = new ConnectException(
                                "join failed because not in correct state");
                        throw c;
                    }
                    ID serverID = null;
                    try {
                        serverID = acceptNewServer(response);
                    } catch (Exception e) {
                        killConnection(aConnection);
                        aConnection = null;
                        connection = null;
                        remoteServerID = null;
                        connectionState = UNCONNECTED;
                        ConnectException c = new ConnectException(
                                "join refused locally via acceptNewServer");
                        throw c;
                    }
                    aConnection.start();
                    remoteServerID = serverID;
                    connectionState = CONNECTED;
                }
            }
        } catch (Exception e) {
            throw new SharedObjectContainerJoinException("could not join", e);
        }
    }

    protected void handleViewChangeMessage(ContainerMessage mess)
            throws IOException {
        debug("handleViewChangeMessage(" + mess + ")");
        ContainerMessage.ViewChangeMessage vc = (ContainerMessage.ViewChangeMessage) mess
                .getData();
        if (vc == null)
            throw new IOException("view change message is null");
        ID fromID = mess.getFromContainerID();
        ID toID = mess.getToContainerID();
        if (fromID == null || !fromID.equals(remoteServerID)) {
            throw new IOException("view change message from " + fromID
                    + " is not same as " + remoteServerID);
        }
        ID[] changeIDs = vc.getChangeIDs();
        if (changeIDs == null) {
            // do nothing if we've got no changes
        } else {
            for (int i = 0; i < changeIDs.length; i++) {
                if (vc.isAdd()) {
                    groupManager.addMember(new Member(changeIDs[i]));
                } else {
                    groupManager.removeMember(changeIDs[i]);
                }
            }
        }
    }

    protected void forwardExcluding(ID from, ID excluding, ContainerMessage data)
            throws IOException {
        // NOP
    }

    protected Serializable getConnectData(ID target, Object data) {
        return ContainerMessage.makeJoinGroupMessage(getID(), target,
                getNextSequenceNumber(), (Serializable) data);
    }

    protected Serializable getLeaveData(ID target) {
        return null;
    }

    public void leaveGroup() {
        debug("leaveGroup");
        synchronized (connectLock) {
            // If we are currently connected
            if (isConnected()) {
                synchronized (connection) {
                    try {
                        connection.sendSynch(remoteServerID,
                                getBytesForObject(ContainerMessage
                                        .makeLeaveGroupMessage(getID(),
                                                remoteServerID,
                                                getNextSequenceNumber(),
                                                getLeaveData(remoteServerID))));
                    } catch (Exception e) {
                    }
                    synchronized (getGroupMembershipLock()) {
                        memberLeave(remoteServerID, connection);
                    }
                }
            }
            connectionState = UNCONNECTED;
            connection = null;
            remoteServerID = null;
        }
    }

    protected abstract ISynchAsynchConnection getClientConnection(
            ID remoteSpace, Object data)
            throws ConnectionInstantiationException;

    protected void handleChangeMsg(ID fromID, ID toID, long seqNum,
            Serializable data) throws IOException {
        ContainerMessage.ViewChangeMessage c = null;
        // Check data in packge for validity
        ID ids[] = null;
        try {
            c = (ContainerMessage.ViewChangeMessage) data;
            if (fromID == null || c == null)
                throw new Exception();
            ids = c.changeIDs;
            if (ids == null || ids[0] == null || !fromID.equals(remoteServerID))
                throw new IOException();
        } catch (Exception e) {
            InvalidObjectException t = new InvalidObjectException("bad data"
                    + ":" + fromID + ":" + toID + ":" + seqNum);
            throw t;
        }
        // Now actually add/remove member
        Member m = new Member(ids[0]);
        synchronized (getGroupMembershipLock()) {
            if (c.add) {
                groupManager.addMember(m);
            } else
                groupManager.removeMember(m);
        }
    }

    protected void queueContainerMessage(ContainerMessage message)
            throws IOException {
        // Do it
        connection.sendAsynch(message.getToContainerID(),
                getBytesForObject(message));
    }

    protected void forwardExcluding(ID from, ID excluding, byte msg,
            Serializable data) throws IOException { /* NOP */
    }

    protected void forwardToRemote(ID from, ID to, ContainerMessage message)
            throws IOException { /* NOP */
    }

    protected ID getIDForConnection(IAsynchConnection conn) {
        return remoteServerID;
    }

    protected void memberLeave(ID fromID, IAsynchConnection conn) {
        if (fromID.equals(remoteServerID)) {
            groupManager.removeAllMembers();
            super.memberLeave(fromID, conn);
            connectionState = UNCONNECTED;
            connection = null;
            remoteServerID = null;
        } else if (fromID.equals(getID())) {
            super.memberLeave(fromID, conn);
        }
    }

    protected void sendMessage(ContainerMessage data) throws IOException {
        // Get connect lock, then call super version
        synchronized (connectLock) {
            checkConnected();
            super.sendMessage(data);
        }
    }

    protected ID[] sendCreateMsg(ID toID, SharedObjectDescription createInfo)
            throws IOException {
        // Get connect lock, then call super version
        synchronized (connectLock) {
            checkConnected();
            return super.sendCreateSharedObjectMessage(toID, createInfo);
        }
    }

    protected void processDisconnect(DisconnectConnectionEvent evt) {
        // Get connect lock, and just return if this connection has been
        // terminated
        synchronized (connectLock) {
            super.processDisconnect(evt);
        }
    }

    protected void processAsynchPacket(AsynchConnectionEvent evt)
            throws IOException {
        // Get connect lock, then call super version
        synchronized (connectLock) {
            checkConnected();
            super.processAsynch(evt);
        }
    }

    protected Serializable processSynch(SynchConnectionEvent evt)
            throws IOException {
        synchronized (connectLock) {
            checkConnected();
            IConnection conn = evt.getConnection();
            if (connection != conn)
                throw new ConnectException("not connected");
            return super.processSynch(evt);
        }
    }

    protected boolean isConnected() {
        return (connectionState == CONNECTED);
    }

    protected boolean isConnecting() {
        return (connectionState == CONNECTING);
    }

    private void checkConnected() throws ConnectException {
        if (!isConnected())
            throw new ConnectException("not connected");
    }

    protected ID acceptNewServer(ContainerMessage serverData) throws Exception {
        ContainerMessage aPacket = serverData;
        ID fromID = aPacket.getFromContainerID();
        if (fromID == null)
            throw new InvalidObjectException("server id is null");
        ID[] ids = ((ContainerMessage.ViewChangeMessage) aPacket.getData()).changeIDs;
        if (ids == null)
            throw new java.io.InvalidObjectException("id array null");
        for (int i = 0; i < ids.length; i++) {
            ID id = ids[i];
            if (id != null && !id.equals(getID()))
                addNewRemoteMember(id, null);
        }
        return fromID;
    }
}
 No newline at end of file