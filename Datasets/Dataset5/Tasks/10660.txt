handleLeave(groupID, null);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp;

import java.io.IOException;
import java.net.ConnectException;
import java.util.HashMap;
import java.util.Iterator;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.ObjectCallback;
import org.eclipse.ecf.core.security.UnsupportedCallbackException;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.filetransfer.IOutgoingFileTransferContainerAdapter;
import org.eclipse.ecf.internal.provider.xmpp.XMPPChatRoomContainer;
import org.eclipse.ecf.internal.provider.xmpp.XMPPChatRoomManager;
import org.eclipse.ecf.internal.provider.xmpp.XMPPContainerAccountManager;
import org.eclipse.ecf.internal.provider.xmpp.XMPPContainerContext;
import org.eclipse.ecf.internal.provider.xmpp.XMPPContainerPresenceHelper;
import org.eclipse.ecf.internal.provider.xmpp.XMPPDebugOptions;
import org.eclipse.ecf.internal.provider.xmpp.XmppPlugin;
import org.eclipse.ecf.internal.provider.xmpp.events.IQEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.MessageEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.PresenceEvent;
import org.eclipse.ecf.internal.provider.xmpp.filetransfer.XMPPOutgoingFileTransferHelper;
import org.eclipse.ecf.internal.provider.xmpp.identity.XMPPID;
import org.eclipse.ecf.internal.provider.xmpp.smack.ECFConnection;
import org.eclipse.ecf.internal.provider.xmpp.smack.ECFConnectionObjectPacketEvent;
import org.eclipse.ecf.internal.provider.xmpp.smack.ECFConnectionPacketEvent;
import org.eclipse.ecf.presence.IAccountManager;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.roster.IRosterManager;
import org.eclipse.ecf.provider.comm.AsynchEvent;
import org.eclipse.ecf.provider.comm.ConnectionCreateException;
import org.eclipse.ecf.provider.comm.ISynchAsynchConnection;
import org.eclipse.ecf.provider.generic.ClientSOContainer;
import org.eclipse.ecf.provider.generic.ContainerMessage;
import org.eclipse.ecf.provider.generic.SOConfig;
import org.eclipse.ecf.provider.generic.SOContainerConfig;
import org.eclipse.ecf.provider.generic.SOContext;
import org.eclipse.ecf.provider.generic.SOWrapper;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.packet.IQ;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Packet;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smackx.packet.MUCUser;
import org.jivesoftware.smackx.packet.VCardTempXUpdateExtension;
import org.jivesoftware.smackx.packet.XHTMLExtension;

public class XMPPContainer extends ClientSOContainer implements
		IPresenceContainerAdapter {

	public static final int DEFAULT_KEEPALIVE = 30000;

	public static final String CONNECT_NAMESPACE = XmppPlugin.getDefault()
			.getNamespaceIdentifier();

	public static final String CONTAINER_HELPER_ID = XMPPContainer.class
			.getName()
			+ ".xmpphandler";

	protected static final String GOOGLE_SERVICENAME = "gmail.com";

	protected int keepAlive = 0;

	protected XMPPContainerAccountManager accountManager = null;

	protected XMPPChatRoomManager chatRoomManager = null;

	protected XMPPOutgoingFileTransferHelper outgoingFileTransferContainerAdapter = null;

	protected XMPPContainerPresenceHelper presenceHelper = null;

	protected ID presenceHelperID = null;

	protected XMPPContainer(SOContainerConfig config, int keepAlive)
			throws Exception {
		super(config);
		this.keepAlive = keepAlive;
		accountManager = new XMPPContainerAccountManager();
		chatRoomManager = new XMPPChatRoomManager(getID());
		this.presenceHelperID = IDFactory.getDefault().createStringID(
				CONTAINER_HELPER_ID);
		presenceHelper = new XMPPContainerPresenceHelper(this);
		outgoingFileTransferContainerAdapter = new XMPPOutgoingFileTransferHelper(
				this);
	}

	public XMPPContainer() throws Exception {
		this(DEFAULT_KEEPALIVE);
	}

	public XMPPContainer(int ka) throws Exception {
		this(new SOContainerConfig(IDFactory.getDefault().createGUID()), ka);
	}

	public XMPPContainer(String userhost, int ka) throws Exception {
		this(new SOContainerConfig(IDFactory.getDefault().createStringID(
				userhost)), ka);
	}

	public IRosterManager getRosterManager() {
		return presenceHelper.getRosterManager();
	}

	public IAccountManager getAccountManager() {
		return accountManager;
	}

	public IChatRoomManager getChatRoomManager() {
		return chatRoomManager;
	}

	public IChatManager getChatManager() {
		return presenceHelper.getChatManager();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(
				XmppPlugin.getDefault().getNamespaceIdentifier());
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID remote, IConnectContext joinContext)
			throws ContainerConnectException {
		try {
			getSharedObjectManager().addSharedObject(presenceHelperID,
					presenceHelper, new HashMap());
			super.connect(remote, joinContext);
		} catch (ContainerConnectException e) {
			disconnect();
			throw e;
		} catch (SharedObjectAddException e1) {
			disconnect();
			throw new ContainerConnectException(
					"Exception adding shared object " + presenceHelperID, e1);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#disconnect()
	 */
	public void disconnect() {
		ID groupID = getConnectedID();
		fireContainerEvent(new ContainerDisconnectingEvent(this.getID(),
				groupID));
		synchronized (getConnectLock()) {
			// If we are currently connected
			if (isConnected()) {
				ISynchAsynchConnection conn = getConnection();
				synchronized (conn) {
					synchronized (getGroupMembershipLock()) {
						memberLeave(groupID, null);
					}
				}
			}
			connectionState = DISCONNECTED;
			this.connection = null;
			remoteServerID = null;
			accountManager.setConnection(null);
			chatRoomManager.setConnection(null, null, null);
			outgoingFileTransferContainerAdapter.setConnection(null);
			presenceHelper.disconnect();
			getSharedObjectManager().removeSharedObject(presenceHelperID);
		}
		// notify listeners
		fireContainerEvent(new ContainerDisconnectedEvent(this.getID(), groupID));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#dispose()
	 */
	public void dispose() {
		if (presenceHelper != null) {
			presenceHelperID = null;
			presenceHelper = null;
		}
		if (chatRoomManager != null)
			chatRoomManager.dispose();
		chatRoomManager = null;
		if (accountManager != null)
			accountManager.dispose();
		accountManager = null;
		if (outgoingFileTransferContainerAdapter != null)
			outgoingFileTransferContainerAdapter.dispose();
		outgoingFileTransferContainerAdapter = null;
		super.dispose();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		if (clazz.equals(IPresenceContainerAdapter.class))
			return this;
		if (clazz.equals(IOutgoingFileTransferContainerAdapter.class))
			return outgoingFileTransferContainerAdapter;
		else
			return super.getAdapter(clazz);
	}

	protected ID handleConnectResponse(ID originalTarget, Object serverData)
			throws Exception {
		if (originalTarget != null && !originalTarget.equals(getID())) {
			addNewRemoteMember(originalTarget, null);

			ECFConnection conn = getECFConnection();
			accountManager.setConnection(conn.getXMPPConnection());
			chatRoomManager.setConnection(getConnectNamespace(),
					originalTarget, conn);
			presenceHelper.setUser(new User(originalTarget));
			outgoingFileTransferContainerAdapter.setConnection(conn
					.getXMPPConnection());
			return originalTarget;

		} else
			throw new ConnectException("invalid response from server");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#createConnection(org.eclipse.ecf.core.identity.ID,
	 *      java.lang.Object)
	 */
	protected ISynchAsynchConnection createConnection(ID remoteSpace,
			Object data) throws ConnectionCreateException {
		boolean google = false;
		if (remoteSpace instanceof XMPPID) {
			XMPPID theID = (XMPPID) remoteSpace;
			String host = theID.getHostname();
			if (host.toLowerCase().equals(GOOGLE_SERVICENAME)) {
				google = true;
			}
		}
		return new ECFConnection(google, getConnectNamespace(), receiver);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#getConnectData(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	protected Object getConnectData(ID remote, IConnectContext joinContext)
			throws IOException, UnsupportedCallbackException {
		Callback[] callbacks = createAuthorizationCallbacks();
		if (joinContext != null && callbacks != null && callbacks.length > 0) {
			CallbackHandler handler = joinContext.getCallbackHandler();
			if (handler != null) {
				handler.handle(callbacks);
			}
			if (callbacks[0] instanceof ObjectCallback) {
				ObjectCallback cb = (ObjectCallback) callbacks[0];
				return cb.getObject();
			}
		}
		return null;
	}

	protected Object createConnectData(ID target, Callback[] cbs, Object data) {
		// first one is password callback
		if (cbs.length > 0) {
			if (cbs[0] instanceof ObjectCallback) {
				ObjectCallback cb = (ObjectCallback) cbs[0];
				return cb.getObject();
			}
		}
		return data;
	}

	protected Callback[] createAuthorizationCallbacks() {
		Callback[] cbs = new Callback[1];
		cbs[0] = new ObjectCallback();
		return cbs;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#getConnectTimeout()
	 */
	protected int getConnectTimeout() {
		return keepAlive;
	}

	protected Roster getRoster() throws IOException {
		ECFConnection connection = getECFConnection();
		if (connection != null) {
			return connection.getRoster();
		} else
			return null;
	}

	protected void deliverEvent(Event evt) {
		SOWrapper wrap = getSharedObjectWrapper(presenceHelperID);
		if (wrap != null)
			wrap.deliverEvent(evt);
		else
			trace("deliverEvent(" + evt + ") wrapper object is unavailable");
	}

	protected void handleXMPPMessage(Packet aPacket) throws IOException {
		if (!handleAsExtension(aPacket)) {
			if (aPacket instanceof IQ) {
				deliverEvent(new IQEvent((IQ) aPacket));
			} else if (aPacket instanceof Message) {
				deliverEvent(new MessageEvent((Message) aPacket));
			} else if (aPacket instanceof Presence) {
				deliverEvent(new PresenceEvent((Presence) aPacket));
			} else {
				// unexpected message
				debug("got unexpected packet " + aPacket.toXML());
			}
		}
	}

	protected boolean handleAsExtension(Packet packet) {
		Iterator i = packet.getExtensions();
		for (; i.hasNext();) {
			Object extension = i.next();
			if (extension instanceof VCardTempXUpdateExtension) {
				VCardTempXUpdateExtension photoExtension = (VCardTempXUpdateExtension) extension;
				deliverEvent(new PresenceEvent((Presence) packet,
						photoExtension.getPhotoDataAsBytes()));
				return true;
			} else if (extension instanceof XHTMLExtension) {
				XHTMLExtension xhtmlExtension = (XHTMLExtension) extension;
				deliverEvent(new MessageEvent((Message) packet, xhtmlExtension
						.getBodies()));
				return true;
			}
			trace("XMPPContainer.handleAsExtension(ext=" + extension
					+ ",packet=" + packet.toXML() + ")");
			if (packet instanceof Presence && extension instanceof MUCUser) {
				trace("XMPPContainer.handleAsExtension: received presence for MUCUser");
				return true;
			}
		}
		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.SOContainer#createSharedObjectContext(org.eclipse.ecf.provider.generic.SOConfig,
	 *      org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue)
	 */
	protected SOContext createSharedObjectContext(SOConfig soconfig,
			IQueueEnqueue queue) {
		return new XMPPContainerContext(soconfig.getSharedObjectID(), soconfig
				.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#processAsynch(org.eclipse.ecf.provider.comm.AsynchEvent)
	 */
	protected void processAsynch(AsynchEvent e) {
		try {
			if (e instanceof ECFConnectionPacketEvent) {
				// It's a regular xmpp message
				handleXMPPMessage((Packet) e.getData());
				return;
			} else if (e instanceof ECFConnectionObjectPacketEvent) {
				// It's an ECF object message
				ECFConnectionObjectPacketEvent evt = (ECFConnectionObjectPacketEvent) e;
				Object obj = evt.getObjectValue();
				// this should be a ContainerMessage
				Object cm = deserializeContainerMessage((byte[]) obj);
				if (cm == null)
					throw new IOException("deserialized object is null");
				ContainerMessage contMessage = (ContainerMessage) cm;
				IChatRoomContainer chat = chatRoomManager
						.findReceiverChatRoom(contMessage.getToContainerID());
				if (chat != null && chat instanceof XMPPChatRoomContainer) {
					XMPPChatRoomContainer cont = (XMPPChatRoomContainer) chat;
					cont.handleContainerMessage(contMessage);
					return;
				}
				Object data = contMessage.getData();
				if (data instanceof ContainerMessage.CreateMessage) {
					handleCreateMessage(contMessage);
				} else if (data instanceof ContainerMessage.CreateResponseMessage) {
					handleCreateResponseMessage(contMessage);
				} else if (data instanceof ContainerMessage.SharedObjectMessage) {
					handleSharedObjectMessage(contMessage);
				} else if (data instanceof ContainerMessage.SharedObjectDisposeMessage) {
					handleSharedObjectDisposeMessage(contMessage);
				} else {
					debug("got unrecognized container message...ignoring: "
							+ contMessage);
				}
			} else {
				// Unexpected type...
				debug("got unexpected event: " + e);
			}
		} catch (Exception except) {
			dumpStack("Exception processing event " + e, except);
		}
	}

	public ECFConnection getECFConnection() {
		return (ECFConnection) super.getConnection();
	}

	public XMPPConnection getXMPPConnection() {
		ECFConnection conn = getECFConnection();
		if (conn == null)
			return null;
		else
			return conn.getXMPPConnection();
	}

	// utility methods

	protected void trace(String msg) {
		Trace.trace(XmppPlugin.PLUGIN_ID, msg);
	}

	protected void dumpStack(String msg, Throwable t) {
		Trace.catching(XmppPlugin.PLUGIN_ID,
				XMPPDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), "", t);
	}

}
 No newline at end of file