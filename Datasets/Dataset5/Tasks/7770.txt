traceStack("Exception in handleXMPPMessage", e); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.xmpp;

import java.io.IOException;
import java.util.HashMap;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.NameCallback;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.core.sharedobject.util.IQueueEnqueue;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.provider.xmpp.events.ChatMembershipEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.IQEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.MessageEvent;
import org.eclipse.ecf.internal.provider.xmpp.events.PresenceEvent;
import org.eclipse.ecf.internal.provider.xmpp.identity.XMPPRoomID;
import org.eclipse.ecf.internal.provider.xmpp.smack.ECFConnection;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomAdminListener;
import org.eclipse.ecf.provider.comm.ConnectionCreateException;
import org.eclipse.ecf.provider.comm.ISynchAsynchConnection;
import org.eclipse.ecf.provider.generic.ClientSOContainer;
import org.eclipse.ecf.provider.generic.ContainerMessage;
import org.eclipse.ecf.provider.generic.SOConfig;
import org.eclipse.ecf.provider.generic.SOContainerConfig;
import org.eclipse.ecf.provider.generic.SOContext;
import org.eclipse.ecf.provider.generic.SOWrapper;
import org.eclipse.ecf.provider.xmpp.XMPPContainer;
import org.eclipse.osgi.util.NLS;
import org.jivesoftware.smack.PacketListener;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.packet.IQ;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Packet;
import org.jivesoftware.smack.packet.Presence;
import org.jivesoftware.smackx.muc.InvitationRejectionListener;
import org.jivesoftware.smackx.muc.MultiUserChat;
import org.jivesoftware.smackx.muc.ParticipantStatusListener;

public class XMPPChatRoomContainer extends ClientSOContainer implements
		IChatRoomContainer {

	private static final String CONTAINER_HELPER_ID = XMPPContainer.class
			.getName()
			+ ".xmppgroupchathandler"; //$NON-NLS-1$

	protected ID containerHelperID;

	protected XMPPChatRoomContainerHelper containerHelper;

	protected MultiUserChat multiuserchat;

	protected Namespace usernamespace = null;

	public XMPPChatRoomContainer(ISharedObjectContainerConfig config,
			ECFConnection conn, Namespace usernamespace)
			throws IDCreateException {
		super(config);
		this.connection = conn;
		this.config = config;
		this.usernamespace = usernamespace;
		this.containerHelperID = IDFactory.getDefault().createStringID(
				CONTAINER_HELPER_ID);
		this.containerHelper = new XMPPChatRoomContainerHelper(usernamespace,
				getXMPPConnection());
	}

	public XMPPChatRoomContainer(ECFConnection conn, Namespace usernamespace)
			throws IDCreateException {
		this(new SOContainerConfig(IDFactory.getDefault().createGUID()), conn,
				usernamespace);
	}

	public void dispose() {
		disconnect();
		if (containerHelperID != null) {
			getSharedObjectManager().removeSharedObject(containerHelperID);
			containerHelperID = null;
		}
		if (containerHelper != null)
			containerHelper.dispose(getID());
		containerHelper = null;
		super.dispose();
	}

	protected void sendMessage(ContainerMessage data) throws IOException {
		synchronized (getConnectLock()) {
			ID toID = data.getToContainerID();
			if (toID == null) {
				data.setToContainerID(remoteServerID);
			}
			super.sendMessage(data);
		}
	}

	protected void handleChatMessage(Message mess) throws IOException {
		SOWrapper wrap = getSharedObjectWrapper(containerHelperID);
		if (wrap != null) {
			wrap.deliverEvent(new MessageEvent(mess));
		}
	}

	protected boolean verifyToIDForSharedObjectMessage(ID toID) {
		return true;
	}

	public void handleContainerMessage(ContainerMessage mess)
			throws IOException {
		if (mess == null) {
			debug("got null container message...ignoring"); //$NON-NLS-1$
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
			debug("got unrecognized container message...ignoring: " + mess); //$NON-NLS-1$
		}
	}

	protected void handleIQMessage(IQ mess) throws IOException {
		SOWrapper wrap = getSharedObjectWrapper(containerHelperID);
		if (wrap != null) {
			wrap.deliverEvent(new IQEvent(mess));
		}
	}

	protected void handlePresenceMessage(Presence mess) throws IOException {
		SOWrapper wrap = getSharedObjectWrapper(containerHelperID);
		if (wrap != null) {
			wrap.deliverEvent(new PresenceEvent(mess));
		}
	}

	protected void handleChatMembershipEvent(String from, boolean add) {
		SOWrapper wrap = getSharedObjectWrapper(containerHelperID);
		if (wrap != null) {
			wrap.deliverEvent(new ChatMembershipEvent(from, add));
		}
	}

	protected void handleXMPPMessage(Packet aPacket) {
		try {
			if (aPacket instanceof IQ) {
				handleIQMessage((IQ) aPacket);
			} else if (aPacket instanceof Message) {
				handleChatMessage((Message) aPacket);
			} else if (aPacket instanceof Presence) {
				handlePresenceMessage((Presence) aPacket);
			} else {
				// unexpected message
				debug("got unexpected packet " + aPacket); //$NON-NLS-1$
			}
		} catch (IOException e) {
			logException("Exception in handleXMPPMessage", e); //$NON-NLS-1$
		}
	}

	protected XMPPConnection getXMPPConnection() {
		return ((ECFConnection) getConnection()).getXMPPConnection();
	}

	protected void addSharedObjectToContainer(ID remote)
			throws SharedObjectAddException {
		getSharedObjectManager().addSharedObject(containerHelperID,
				containerHelper, new HashMap());
	}

	protected void cleanUpConnectFail() {
		if (containerHelper != null) {
			getSharedObjectManager().removeSharedObject(containerHelperID);
			containerHelper = null;
			containerHelperID = null;
		}
		connectionState = DISCONNECTED;
		remoteServerID = null;
	}

	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(
				XmppPlugin.getDefault().getRoomNamespaceIdentifier());
	}

	public void connect(ID remote, IConnectContext connectContext)
			throws ContainerConnectException {
		if (!(remote instanceof XMPPRoomID)) {
			throw new ContainerConnectException(
					NLS
							.bind(
									Messages.XMPPChatRoomContainer_Exception_Connect_Wrong_Type,
									remote));
		}
		XMPPRoomID roomID = (XMPPRoomID) remote;
		fireContainerEvent(new ContainerConnectingEvent(this.getID(), remote,
				connectContext));
		synchronized (getConnectLock()) {
			try {
				connectionState = CONNECTING;
				remoteServerID = null;
				addSharedObjectToContainer(remote);
				multiuserchat = new MultiUserChat(getXMPPConnection(), roomID
						.getMucString());
				// Get nickname from join context
				String nick = null;
				try {
					Callback[] callbacks = new Callback[1];
					callbacks[0] = new NameCallback("Nickname", roomID
							.getNickname());
					if (connectContext != null) {
						CallbackHandler handler = connectContext
								.getCallbackHandler();
						if (handler != null) {
							handler.handle(callbacks);
						}
					}
					if (callbacks[0] instanceof NameCallback) {
						NameCallback cb = (NameCallback) callbacks[0];
						nick = cb.getName();
					}
				} catch (Exception e) {
					throw new ContainerConnectException(
							"Exception in CallbackHandler.handle(<callbacks>)",
							e);
				}
				String nickname = null;
				if (nick == null || nick.equals(""))
					nickname = roomID.getNickname();
				else
					nickname = nick;
				multiuserchat.addMessageListener(new PacketListener() {
					public void processPacket(Packet arg0) {
						handleXMPPMessage(arg0);
					}
				});
				multiuserchat.addParticipantListener(new PacketListener() {
					public void processPacket(Packet arg0) {
						handleXMPPMessage(arg0);
					}
				});
				multiuserchat
						.addParticipantStatusListener(new ParticipantStatusListener() {
							public void joined(String arg0) {
								handleChatMembershipEvent(arg0, true);
							}

							public void left(String arg0) {
								handleChatMembershipEvent(arg0, false);
							}

							public void voiceGranted(String arg0) {
								// TODO Auto-generated method stub
								System.out
										.println("voiceGranted(" + arg0 + ")");
							}

							public void voiceRevoked(String arg0) {
								// TODO Auto-generated method stub
								System.out
										.println("voiceRevoked(" + arg0 + ")");
							}

							public void membershipGranted(String arg0) {
								// TODO Auto-generated method stub
								System.out.println("membershipGranted(" + arg0
										+ ")");
							}

							public void membershipRevoked(String arg0) {
								// TODO Auto-generated method stub
								System.out.println("membershipRevoked(" + arg0
										+ ")");
							}

							public void moderatorGranted(String arg0) {
								// TODO Auto-generated method stub
								System.out.println("moderatorGranted(" + arg0
										+ ")");
							}

							public void moderatorRevoked(String arg0) {
								// TODO Auto-generated method stub
								System.out.println("moderatorRevoked(" + arg0
										+ ")");
							}

							public void ownershipGranted(String arg0) {
								// TODO Auto-generated method stub
								System.out.println("ownershipGranted(" + arg0
										+ ")");
							}

							public void ownershipRevoked(String arg0) {
								// TODO Auto-generated method stub
								System.out.println("ownershipRevoked(" + arg0
										+ ")");
							}

							public void adminGranted(String arg0) {
								// TODO Auto-generated method stub
								System.out
										.println("adminGranted(" + arg0 + ")");
							}

							public void adminRevoked(String arg0) {
								// TODO Auto-generated method stub
								System.out
										.println("adminRevoked(" + arg0 + ")");
							}

							public void kicked(String arg0, String arg1,
									String arg2) {
								// TODO Auto-generated method stub
								System.out.println("kicked(" + arg0 + ","
										+ arg1 + "," + arg2 + ")");

							}

							public void banned(String arg0, String arg1,
									String arg2) {
								// TODO Auto-generated method stub
								System.out.println("banned(" + arg0 + ","
										+ arg1 + "," + arg2 + ")");

							}

							public void nicknameChanged(String arg0, String arg1) {
								// TODO Auto-generated method stub
								System.out.println("nicknameChanged(" + arg0
										+ "," + arg1 + ")");

							}
						});
				multiuserchat
						.addInvitationRejectionListener(new InvitationRejectionListener() {
							public void invitationDeclined(String arg0,
									String arg1) {
								// TODO Auto-generated method stub
								System.out.println("invitationDeclined(" + arg0
										+ "," + arg1 + ")");
							}
						});
				multiuserchat.join(nickname);
				connectionState = CONNECTED;
				remoteServerID = roomID;
				containerHelper.setRoomID(remoteServerID);
				fireContainerEvent(new ContainerConnectedEvent(this.getID(),
						roomID));
			} catch (Exception e) {
				cleanUpConnectFail();
				ContainerConnectException ce = new ContainerConnectException(
						"Exception joining " + roomID);
				ce.setStackTrace(e.getStackTrace());
				throw ce;
			}
		}
	}

	public void disconnect() {
		ID groupID = getConnectedID();
		fireContainerEvent(new ContainerDisconnectingEvent(this.getID(),
				groupID));
		synchronized (getConnectLock()) {
			// If we are currently connected
			if (isConnected()) {
				try {
					multiuserchat.leave();
				} catch (Exception e) {
					traceStack("Exception in multi user chat.leave", e);
				}
			}
			connectionState = DISCONNECTED;
			remoteServerID = null;
			containerHelper.setRoomID(null);
			this.connection = null;
		}
		// notify listeners
		fireContainerEvent(new ContainerDisconnectedEvent(this.getID(), groupID));
	}

	protected SOContext createSharedObjectContext(SOConfig soconfig,
			IQueueEnqueue queue) {
		return new XMPPContainerContext(soconfig.getSharedObjectID(), soconfig
				.getHomeContainerID(), this, soconfig.getProperties(), queue);
	}

	protected ID createChatRoomID(String groupName) throws IDCreateException {
		String username = getXMPPConnection().getUser();
		int atIndex = username.indexOf('@');
		if (atIndex > 0)
			username = username.substring(0, atIndex);
		String host = getXMPPConnection().getHost();
		Namespace ns = getConnectNamespace();
		ID targetID = IDFactory.getDefault().createID(ns,
				new Object[] { username, host, null, groupName, username });
		return targetID;
	}

	protected ISynchAsynchConnection createConnection(ID remoteSpace,
			Object data) throws ConnectionCreateException {
		return null;
	}

	public IChatRoomMessageSender getChatRoomMessageSender() {
		return new IChatRoomMessageSender() {
			public void sendMessage(String messageBody) throws ECFException {
				if (multiuserchat != null) {
					try {
						multiuserchat.sendMessage(messageBody);
					} catch (Exception e) {
						ECFException except = new ECFException(
								"Send message exception", e);
						throw except;
					}
				}
			}
		};
	}

	public void connect(String groupName) throws ContainerConnectException {
		ID targetID = null;
		try {
			targetID = createChatRoomID(groupName);
		} catch (IDCreateException e) {
			throw new ContainerConnectException(
					"Exception creating chat room id", e);
		}
		this.connect(targetID, null);
	}

	public void addChatRoomParticipantListener(
			IChatRoomParticipantListener participantListener) {
		if (containerHelper != null) {
			containerHelper.addChatParticipantListener(participantListener);
		}
	}

	public void removeChatRoomParticipantListener(
			IChatRoomParticipantListener participantListener) {
		if (containerHelper != null) {
			containerHelper.removeChatParticipantListener(participantListener);
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#addMessageListener(org.eclipse.ecf.presence.IIMMessageListener)
	 */
	public void addMessageListener(IIMMessageListener listener) {
		containerHelper.addChatRoomMessageListener(listener);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#removeMessageListener(org.eclipse.ecf.presence.IIMMessageListener)
	 */
	public void removeMessageListener(IIMMessageListener listener) {
		containerHelper.removeChatRoomMessageListener(listener);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#addChatRoomSubjectListener(org.eclipse.ecf.presence.chatroom.IChatRoomAdminListener)
	 */
	public void addChatRoomAdminListener(IChatRoomAdminListener subjectListener) {
		// TODO Auto-generated method stub

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#removeChatRoomSubjectListener(org.eclipse.ecf.presence.chatroom.IChatRoomAdminListener)
	 */
	public void removeChatRoomAdminListener(
			IChatRoomAdminListener subjectListener) {
		// TODO Auto-generated method stub

	}

}
 No newline at end of file