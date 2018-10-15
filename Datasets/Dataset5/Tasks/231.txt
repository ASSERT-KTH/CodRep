final Iterator i = packet.getExtensions().iterator();

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp;

import java.io.IOException;
import java.net.ConnectException;
import java.util.*;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.*;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.filetransfer.ISendFileTransferContainerAdapter;
import org.eclipse.ecf.internal.provider.xmpp.*;
import org.eclipse.ecf.internal.provider.xmpp.Messages;
import org.eclipse.ecf.internal.provider.xmpp.events.*;
import org.eclipse.ecf.internal.provider.xmpp.filetransfer.XMPPOutgoingFileTransferHelper;
import org.eclipse.ecf.internal.provider.xmpp.search.XMPPUserSearchManager;
import org.eclipse.ecf.internal.provider.xmpp.smack.*;
import org.eclipse.ecf.presence.IAccountManager;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.roster.IRosterManager;
import org.eclipse.ecf.presence.search.IUserSearchManager;
import org.eclipse.ecf.presence.service.IPresenceService;
import org.eclipse.ecf.provider.comm.*;
import org.eclipse.ecf.provider.generic.*;
import org.eclipse.ecf.provider.xmpp.identity.XMPPID;
import org.eclipse.osgi.util.NLS;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.packet.*;
import org.jivesoftware.smackx.packet.MUCUser;
import org.jivesoftware.smackx.packet.XHTMLExtension;

/**
 * @since 3.0
 */
public class XMPPContainer extends ClientSOContainer implements
		IPresenceService {

	public static final int DEFAULT_KEEPALIVE = 30000;

	public static final String CONNECT_NAMESPACE = XmppPlugin.getDefault()
			.getNamespaceIdentifier();

	public static final String CONTAINER_HELPER_ID = XMPPContainer.class
			.getName()
			+ ".xmpphandler"; //$NON-NLS-1$

	protected static final String GOOGLE_SERVICENAME = "gmail.com"; //$NON-NLS-1$

	private static final String[] googleHosts = { GOOGLE_SERVICENAME,
			"talk.google.com", "googlemail.com" }; //$NON-NLS-1$ //$NON-NLS-2$

	public static final String XMPP_GOOGLE_OVERRIDE_PROP_NAME = "ecf.xmpp.google.override"; //$NON-NLS-1$

	private static Set googleNames = new HashSet();

	static {
		for (int i = 0; i < googleHosts.length; i++)
			googleNames.add(googleHosts[i]);
		final String override = System
				.getProperty(XMPP_GOOGLE_OVERRIDE_PROP_NAME);
		if (override != null)
			googleNames.add(override.toLowerCase());
	}

	protected int keepAlive = 0;

	XMPPContainerAccountManager accountManager = null;

	XMPPChatRoomManager chatRoomManager = null;

	XMPPOutgoingFileTransferHelper outgoingFileTransferContainerAdapter = null;

	XMPPContainerPresenceHelper presenceHelper = null;

	/**
	 * @since 3.0
	 */
	XMPPUserSearchManager searchManager = null;

	protected ID presenceHelperID = null;

	protected XMPPContainer(SOContainerConfig config, int keepAlive)
			throws Exception {
		super(config);
		this.keepAlive = keepAlive;
		accountManager = new XMPPContainerAccountManager();
		chatRoomManager = new XMPPChatRoomManager(getID());
		searchManager = new XMPPUserSearchManager();
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

	/**
	 * @since 3.0
	 */
	public IUserSearchManager getUserSearchManager() {
		return searchManager;
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
	 * @see
	 * org.eclipse.ecf.provider.generic.ClientSOContainer#connect(org.eclipse
	 * .ecf.core.identity.ID, org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID remote, IConnectContext joinContext)
			throws ContainerConnectException {
		try {
			getSharedObjectManager().addSharedObject(presenceHelperID,
					presenceHelper, null);
			super.connect(remote, joinContext);
			XmppPlugin.getDefault().registerService(this);
		} catch (final ContainerConnectException e) {
			disconnect();
			throw e;
		} catch (final SharedObjectAddException e1) {
			disconnect();
			throw new ContainerConnectException(NLS.bind(
					Messages.XMPPContainer_EXCEPTION_ADDING_SHARED_OBJECT,
					presenceHelperID), e1);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.generic.ClientSOContainer#disconnect()
	 */
	public void disconnect() {
		final ID groupID = getConnectedID();
		fireContainerEvent(new ContainerDisconnectingEvent(this.getID(),
				groupID));
		synchronized (getConnectLock()) {
			// If we are currently connected
			if (isConnected()) {
				XmppPlugin.getDefault().unregisterService(this);
				final ISynchAsynchConnection conn = getConnection();
				synchronized (conn) {
					synchronized (getGroupMembershipLock()) {
						handleLeave(groupID, conn);
					}
				}
			}
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
		chatRoomManager.dispose();
		accountManager.dispose();
		outgoingFileTransferContainerAdapter.dispose();
		super.dispose();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.provider.generic.SOContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class clazz) {
		if (clazz.equals(IPresenceContainerAdapter.class))
			return this;
		if (clazz.equals(ISendFileTransferContainerAdapter.class))
			return outgoingFileTransferContainerAdapter;
		else
			return super.getAdapter(clazz);
	}

	protected ID handleConnectResponse(ID originalTarget, Object serverData)
			throws Exception {
		if (originalTarget != null && !originalTarget.equals(getID())) {
			addNewRemoteMember(originalTarget, null);

			final ECFConnection conn = getECFConnection();
			accountManager.setConnection(conn.getXMPPConnection());
			chatRoomManager.setConnection(getConnectNamespace(),
					originalTarget, conn);
			searchManager.setConnection(getConnectNamespace(), originalTarget,
					conn);
			searchManager.setEnabled(!isGoogle(originalTarget));
			presenceHelper.setUser(new User(originalTarget));
			outgoingFileTransferContainerAdapter.setConnection(conn
					.getXMPPConnection());
			return originalTarget;

		} else
			throw new ConnectException(
					Messages.XMPPContainer_EXCEPTION_INVALID_RESPONSE_FROM_SERVER);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.provider.generic.ClientSOContainer#createConnection(org
	 * .eclipse.ecf.core.identity.ID, java.lang.Object)
	 */
	protected ISynchAsynchConnection createConnection(ID remoteSpace,
			Object data) throws ConnectionCreateException {
		final boolean google = isGoogle(remoteSpace);
		return new ECFConnection(google, getConnectNamespace(), receiver);
	}

	protected boolean isGoogle(ID remoteSpace) {
		if (remoteSpace instanceof XMPPID) {
			final XMPPID theID = (XMPPID) remoteSpace;
			final String host = theID.getHostname();
			if (host == null)
				return false;
			return googleNames.contains(host.toLowerCase());
		}
		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.provider.generic.ClientSOContainer#getConnectData(org
	 * .eclipse.ecf.core.identity.ID,
	 * org.eclipse.ecf.core.security.IConnectContext)
	 */
	protected Object getConnectData(ID remote, IConnectContext joinContext)
			throws IOException, UnsupportedCallbackException {
		final Callback[] callbacks = createAuthorizationCallbacks();
		if (joinContext != null && callbacks != null && callbacks.length > 0) {
			final CallbackHandler handler = joinContext.getCallbackHandler();
			if (handler != null) {
				handler.handle(callbacks);
			}
			if (callbacks[0] instanceof ObjectCallback) {
				final ObjectCallback cb = (ObjectCallback) callbacks[0];
				return cb.getObject();
			}
		}
		return null;
	}

	protected Object createConnectData(ID target, Callback[] cbs, Object data) {
		// first one is password callback
		if (cbs.length > 0) {
			if (cbs[0] instanceof ObjectCallback) {
				final ObjectCallback cb = (ObjectCallback) cbs[0];
				return cb.getObject();
			}
		}
		return data;
	}

	protected Callback[] createAuthorizationCallbacks() {
		final Callback[] cbs = new Callback[1];
		cbs[0] = new ObjectCallback();
		return cbs;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.provider.generic.ClientSOContainer#getConnectTimeout()
	 */
	protected int getConnectTimeout() {
		return keepAlive;
	}

	protected Roster getRoster() throws IOException {
		final ECFConnection connection = getECFConnection();
		if (connection != null) {
			return connection.getRoster();
		} else
			return null;
	}

	protected void deliverEvent(Event evt) {
		final SOWrapper wrap = getSharedObjectWrapper(presenceHelperID);
		if (wrap != null)
			wrap.deliverEvent(evt);
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
				log(NLS.bind(Messages.XMPPContainer_UNEXPECTED_XMPP_MESSAGE,
						aPacket.toXML()), null);
			}
		}
	}

	protected boolean handleAsExtension(Packet packet) {
		final Iterator i = packet.getExtensions();
		for (; i.hasNext();) {
			final Object extension = i.next();
			if (extension instanceof XHTMLExtension) {
				final XHTMLExtension xhtmlExtension = (XHTMLExtension) extension;
				deliverEvent(new MessageEvent((Message) packet, xhtmlExtension
						.getBodies()));
				return true;
			}
			if (packet instanceof Presence && extension instanceof MUCUser) {
				return true;
			}
		}
		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.provider.generic.SOContainer#createSharedObjectContext
	 * (org.eclipse.ecf.provider.generic.SOConfig,
	 * org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue)
	 */
	protected SOContext createSharedObjectContext(SOConfig soconfig,
			IQueueEnqueue queue) {
		return new XMPPContainerContext(soconfig.getSharedObjectID(), soconfig
				.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.eclipse.ecf.provider.generic.ClientSOContainer#processAsynch(org.
	 * eclipse.ecf.provider.comm.AsynchEvent)
	 */
	protected void processAsynch(AsynchEvent e) {
		try {
			if (e instanceof ECFConnectionPacketEvent) {
				// It's a regular xmpp message
				handleXMPPMessage((Packet) e.getData());
				return;
			} else if (e instanceof ECFConnectionObjectPacketEvent) {
				// It's an ECF object message
				final ECFConnectionObjectPacketEvent evt = (ECFConnectionObjectPacketEvent) e;
				final Object obj = evt.getObjectValue();
				// this should be a ContainerMessage
				final Object cm = deserializeContainerMessage((byte[]) obj);
				if (cm == null)
					throw new IOException(
							Messages.XMPPContainer_EXCEPTION_DESERIALIZED_OBJECT_NULL);
				final ContainerMessage contMessage = (ContainerMessage) cm;
				final IChatRoomContainer chat = chatRoomManager
						.findReceiverChatRoom(contMessage.getToContainerID());
				if (chat != null && chat instanceof XMPPChatRoomContainer) {
					final XMPPChatRoomContainer cont = (XMPPChatRoomContainer) chat;
					cont.handleContainerMessage(contMessage);
					return;
				}
				final Object data = contMessage.getData();
				if (data instanceof ContainerMessage.CreateMessage) {
					handleCreateMessage(contMessage);
				} else if (data instanceof ContainerMessage.CreateResponseMessage) {
					handleCreateResponseMessage(contMessage);
				} else if (data instanceof ContainerMessage.SharedObjectMessage) {
					handleSharedObjectMessage(contMessage);
				} else if (data instanceof ContainerMessage.SharedObjectDisposeMessage) {
					handleSharedObjectDisposeMessage(contMessage);
				} else {
					debug(NLS
							.bind(
									Messages.XMPPContainer_UNRECOGONIZED_CONTAINER_MESSAGE,
									contMessage));
				}
			} else {
				// Unexpected type...
				log(NLS.bind(Messages.XMPPContainer_UNEXPECTED_EVENT, e), null);
			}
		} catch (final Exception except) {
			log(NLS.bind(Messages.XMPPContainer_EXCEPTION_HANDLING_ASYCH_EVENT,
					e), except);
		}
	}

	public ECFConnection getECFConnection() {
		return (ECFConnection) super.getConnection();
	}

	public XMPPConnection getXMPPConnection() {
		final ECFConnection conn = getECFConnection();
		if (conn == null)
			return null;
		else
			return conn.getXMPPConnection();
	}

	// utility methods
	protected void log(String msg, Throwable e) {
		XmppPlugin.log(msg, e);
	}
}
 No newline at end of file