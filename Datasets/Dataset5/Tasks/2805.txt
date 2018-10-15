protected SOContext makeSharedObjectContext(SOConfig config,

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.container;

import java.io.IOException;
import java.util.HashMap;
import org.eclipse.ecf.core.SharedObjectAddException;
import org.eclipse.ecf.core.SharedObjectContainerJoinException;
import org.eclipse.ecf.core.comm.AsynchConnectionEvent;
import org.eclipse.ecf.core.comm.ConnectionInstantiationException;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.events.SharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.events.SharedObjectContainerLeaveGroupEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.IQueueEnqueue;
import org.eclipse.ecf.provider.generic.ClientSOContainer;
import org.eclipse.ecf.provider.generic.ContainerMessage;
import org.eclipse.ecf.provider.generic.SOConfig;
import org.eclipse.ecf.provider.generic.SOContext;
import org.eclipse.ecf.provider.generic.SOWrapper;
import org.eclipse.ecf.provider.xmpp.events.IQEvent;
import org.eclipse.ecf.provider.xmpp.events.MessageEvent;
import org.eclipse.ecf.provider.xmpp.events.PresenceEvent;
import org.eclipse.ecf.provider.xmpp.smack.ChatConnectionObjectPacketEvent;
import org.eclipse.ecf.provider.xmpp.smack.ChatConnectionPacketEvent;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.XMPPException;
import org.jivesoftware.smack.packet.IQ;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Packet;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smackx.muc.MultiUserChat;

public class XMPPGroupChatSOContainer extends ClientSOContainer {
    public static final String XMPP_GROUP_CHAT_SHARED_OBJECT_ID = XMPPClientSOContainer.class
            .getName()
            + ".xmppgroupchathandler";
    XMPPConnection connection;
    ID sharedObjectID;
    XMPPGroupChatSharedObject sharedObject;
    MultiUserChat multiuserchat;
    IGroupChatContainerConfig gcconfig;

    public XMPPGroupChatSOContainer(IGroupChatContainerConfig config,
            XMPPConnection conn) throws Exception {
        super(config);
        this.connection = conn;
        this.gcconfig = config;
        initializeSharedObject();
        initializeGroupChat();
    }
    protected IGroupChatContainerConfig getGroupChatConfig() {
        return gcconfig;
    }
    protected void initializeGroupChat() throws XMPPException {
        multiuserchat = new MultiUserChat(connection,getGroupChatConfig().getRoomName());
        multiuserchat.create(getGroupChatConfig().getOwnerName());
    }
    public void dispose(long time) {
        super.dispose(time);
        connection = null;
    }

    protected void handleChatMessage(Message mess) throws IOException {
        SOWrapper wrap = getSharedObjectWrapper(sharedObjectID);
        if (wrap != null) {
            wrap.deliverEvent(new MessageEvent(mess));
        }
    }

    protected void handleContainerMessage(ContainerMessage mess)
            throws IOException {
        if (mess == null) {
            debug("got null container message...ignoring");
            return;
        }
        Object data = mess.getData();
        if (data instanceof ContainerMessage.CreateMessage) {
            handleCreateMessage(mess);
        } else if (data instanceof ContainerMessage.CreateResponseMessage) {
            handleCreateResponseMessage(mess);
        } else if (data instanceof ContainerMessage.SharedObjectMessage) {
            handleSharedObjectMessage(mess);
        } else if (data instanceof ContainerMessage.SharedObjectDisposeMessage) {
            handleSharedObjectDisposeMessage(mess);
        } else {
            debug("got unrecognized container message...ignoring: " + mess);
        }
    }

    protected void handleIQMessage(IQ mess) throws IOException {
        SOWrapper wrap = getSharedObjectWrapper(sharedObjectID);
        if (wrap != null) {
            wrap.deliverEvent(new IQEvent(mess));
        }
    }

    protected void handlePresenceMessage(Presence mess) throws IOException {
        SOWrapper wrap = getSharedObjectWrapper(sharedObjectID);
        if (wrap != null) {
            wrap.deliverEvent(new PresenceEvent(mess));
        }
    }

    protected void handleXMPPMessage(Packet aPacket) throws IOException {
        if (aPacket instanceof IQ) {
            handleIQMessage((IQ) aPacket);
        } else if (aPacket instanceof Message) {
            handleChatMessage((Message) aPacket);
        } else if (aPacket instanceof Presence) {
            handlePresenceMessage((Presence) aPacket);
        } else {
            // unexpected message
            debug("got unexpected packet " + aPacket);
        }
    }

    protected void initializeSharedObject() throws Exception {
        sharedObjectID = IDFactory.makeStringID(XMPP_GROUP_CHAT_SHARED_OBJECT_ID);
        sharedObject = new XMPPGroupChatSharedObject();
    }

    protected void addSharedObjectToContainer(ID remote)
            throws SharedObjectAddException {
        getSharedObjectManager().addSharedObject(sharedObjectID, sharedObject,
                new HashMap(), null);
    }

    protected void cleanUpConnectFail() {
        if (sharedObject != null) {
            getSharedObjectManager().removeSharedObject(sharedObjectID);
        }
        dispose(0);
    }

    public void joinGroup(ID remote, Object data)
            throws SharedObjectContainerJoinException {
        String nickname = "";
        String password = "";
        try {
            addSharedObjectToContainer(remote);
            IGroupChatContainerConfig config = getGroupChatConfig();
            nickname = config.getNickname();
            password = config.getPassword();
            multiuserchat.join(nickname,password);
        } catch (XMPPException e) {
            cleanUpConnectFail();
            SharedObjectContainerJoinException ce = new SharedObjectContainerJoinException("Exception joining with nickname "+nickname);
            ce.setStackTrace(e.getStackTrace());
            throw ce;
        } catch (SharedObjectAddException e1) {
            cleanUpConnectFail();
            SharedObjectContainerJoinException ce = new SharedObjectContainerJoinException("Exception adding shared object " + sharedObjectID);
            ce.setStackTrace(e1.getStackTrace());
            throw ce;
        }
    }

    public void leaveGroup() {
        ID groupID = getGroupID();
        fireContainerEvent(new SharedObjectContainerLeaveGroupEvent(this
                .getID(), groupID));
        synchronized (getConnectLock()) {
            // If we are currently connected
            if (isConnected()) {
                ISynchAsynchConnection connection = getConnection();
                synchronized (connection) {
                    synchronized (getGroupMembershipLock()) {
                        memberLeave(groupID, null);
                    }
                    try {
                        connection.disconnect();
                    } catch (IOException e) {
                        dumpStack("Exception disconnecting", e);
                    }
                }
            }
            connectionState = UNCONNECTED;
            connection = null;
            remoteServerID = null;
        }
        // notify listeners
        fireContainerEvent(new SharedObjectContainerDepartedEvent(this.getID(),
                groupID));
    }

    protected SOContext makeNewSharedObjectContext(SOConfig config,
            IQueueEnqueue queue) {
        return new XMPPContainerContext(config.getSharedObjectID(), config
                .getHomeContainerID(), this, config.getProperties(), queue);
    }

    protected void processAsynch(AsynchConnectionEvent e) {
        try {
            if (e instanceof ChatConnectionPacketEvent) {
                // It's a regular message...just print for now
                ChatConnectionPacketEvent evt = (ChatConnectionPacketEvent) e;
                Packet chatMess = (Packet) e.getData();
                handleXMPPMessage(chatMess);
                return;
            } else if (e instanceof ChatConnectionObjectPacketEvent) {
                ChatConnectionObjectPacketEvent evt = (ChatConnectionObjectPacketEvent) e;
                Object obj = evt.getObjectValue();
                // this should be a ContainerMessage
                Object cm = deserializeContainerMessage((byte[]) obj);
                if (cm == null)
                    throw new IOException("deserialized object is null");
                ContainerMessage contMessage = (ContainerMessage) cm;
                Object cmdata = contMessage.getData();
                handleContainerMessage(contMessage);
            } else {
                // Unexpected type...
                debug("got unexpected event: " + e);
            }
        } catch (Exception except) {
            System.err.println("Exception in processAsynch");
            except.printStackTrace(System.err);
            dumpStack("Exception processing event " + e, except);
        }
    }

    /*
     * (non-Javadoc)
     * 
     * @see org.eclipse.ecf.provider.generic.ClientSOContainer#getClientConnection(org.eclipse.ecf.core.identity.ID,
     *      java.lang.Object)
     */
    protected ISynchAsynchConnection makeConnection(ID remoteSpace,
            Object data) throws ConnectionInstantiationException {
        return null;
    }
}
 No newline at end of file