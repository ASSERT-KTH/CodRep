throw new TimeoutException(NLS.bind(Messages.IRCChannelContainer_Exception_Connect_Timeout, connectID.getName()), CONNECT_TIMEOUT);

/****************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.irc.container;

import java.util.*;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.TimeoutException;
import org.eclipse.ecf.internal.provider.irc.Messages;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chatroom.*;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.osgi.util.NLS;
import org.schwering.irc.lib.IRCUser;

/**
 * IContainer class used to represent a specific IRC channel (e.g. #eclipse-dev)
 * 
 */
public class IRCChannelContainer extends IRCAbstractContainer implements IChatMessageSender, IChatRoomContainer {

	private static final long CONNECT_TIMEOUT = 10000;

	protected List participantListeners = new ArrayList();
	protected IRCRootContainer rootContainer;
	protected IRCUser ircUser = null;
	protected String channelOperator;

	protected Object connectLock = new Object();
	protected boolean connectWaiting = false;

	protected Vector channelParticipants = new Vector();

	protected IChatRoomAdminSender adminSender = null;

	protected IChatRoomMessageSender sender = new IChatRoomMessageSender() {
		public void sendMessage(String message) throws ECFException {
			rootContainer.doSendChannelMessage(targetID.getName(), ircUser.toString(), message);
		}
	};

	public IRCChannelContainer(IRCRootContainer root, ID localID) {
		this.rootContainer = root;
		this.localID = localID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#addChatParticipantListener(org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener)
	 */
	public void addChatRoomParticipantListener(IChatRoomParticipantListener participantListener) {
		participantListeners.add(participantListener);
	}

	public void removeChatRoomParticipantListener(IChatRoomParticipantListener participantListener) {
		participantListeners.remove(participantListener);
	}

	protected void handleUserQuit(String name) {
		if (containsChannelParticipant(createIDFromString(name)) != null)
			firePresenceListeners(false, new String[] {name});
	}

	private IPresence createPresence(final boolean available) {
		return new IPresence() {

			private static final long serialVersionUID = -7514227760059471898L;
			Map properties = new HashMap();

			public Mode getMode() {
				return (available ? IPresence.Mode.AVAILABLE : IPresence.Mode.AWAY);
			}

			public Map getProperties() {
				return properties;
			}

			public String getStatus() {
				return null;
			}

			public Type getType() {
				return (available ? IPresence.Type.AVAILABLE : IPresence.Type.UNAVAILABLE);
			}

			public Object getAdapter(Class adapter) {
				return null;
			}

			public byte[] getPictureData() {
				return new byte[0];
			}
		};
	}

	protected boolean addChannelParticipant(ID participantID) {
		if (containsChannelParticipant(participantID) == null) {
			channelParticipants.add(participantID);
			return true;
		}
		return false;
	}

	protected ID removeChannelParticipant(ID participantID) {
		if (channelParticipants.remove(participantID))
			return participantID;
		ID operatorID = createIDFromString(OPERATOR_PREFIX + participantID.getName());
		if (channelParticipants.remove(operatorID))
			return operatorID;
		return null;
	}

	protected ID containsChannelParticipant(ID participantID) {
		if (channelParticipants.contains(participantID))
			return participantID;
		ID operatorID = createIDFromString(OPERATOR_PREFIX + participantID.getName());
		if (channelParticipants.contains(operatorID))
			return operatorID;
		return null;
	}

	protected void firePresenceListeners(boolean joined, String[] users) {
		for (int j = 0; j < users.length; j++) {
			if (joined) {
				if (isChannelOperator(users[j]))
					setChannelOperator(users[j]);
				ID participantID = createIDFromString(users[j]);
				if (addChannelParticipant(participantID)) {
					// Notify all listeners
					for (Iterator i = participantListeners.iterator(); i.hasNext();) {
						IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();

						l.handleArrived(new User(participantID));
						l.handlePresenceUpdated(participantID, createPresence(true));
					}
				}
			} else {
				ID removeID = removeChannelParticipant(createIDFromString(users[j]));
				if (removeID != null) {
					// Notify all listeners
					for (Iterator i = participantListeners.iterator(); i.hasNext();) {
						IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();

						l.handlePresenceUpdated(removeID, createPresence(false));
						l.handleDeparted(new User(removeID));
					}

				}
			}
		}
	}

	protected boolean isChannelOperator(String user) {
		if (user != null && user.startsWith(OPERATOR_PREFIX))
			return true;
		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#getChatMessageSender()
	 */
	public IChatRoomMessageSender getChatRoomMessageSender() {
		return sender;
	}

	protected String getIRCUserName(IRCUser user) {
		return user == null ? null : user.toString();
	}

	protected void setIRCUser(IRCUser user) {
		if (this.ircUser == null) {
			this.ircUser = user;
			synchronized (connectLock) {
				if (connectWaiting) {
					connectWaiting = false;
					connectLock.notify();
				}
			}
		} else
			firePresenceListeners(true, new String[] {getIRCUserName(user)});
	}

	protected void fireContainerEvent(IContainerEvent event) {
		super.fireContainerEvent(event);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID connectID, IConnectContext connectContext) throws ContainerConnectException {
		// Actually do join here
		if (connectID == null)
			throw new ContainerConnectException(Messages.IRCChannelContainer_Exception_TargetID_Null);
		if (connectWaiting)
			throw new ContainerConnectException(Messages.IRCChannelContainer_Exception_Connecting);
		// Get channel name
		String channelName = connectID.getName();
		fireContainerEvent(new ContainerConnectingEvent(this.getID(), connectID, connectContext));
		// Get password via callback in connectContext
		String pw = getPasswordFromConnectContext(connectContext);
		synchronized (connectLock) {
			connectWaiting = true;
			try {
				rootContainer.doJoinChannel(channelName, pw);
				long timeout = CONNECT_TIMEOUT + System.currentTimeMillis();
				while (connectWaiting && timeout > System.currentTimeMillis()) {
					connectLock.wait(2000);
				}
				if (connectWaiting)
					throw new TimeoutException(CONNECT_TIMEOUT, NLS.bind(Messages.IRCChannelContainer_Exception_Connect_Timeout, connectID.getName()));
				this.targetID = connectID;
				fireContainerEvent(new ContainerConnectedEvent(this.getID(), this.targetID));
			} catch (Exception e) {
				this.targetID = null;
				throw new ContainerConnectException(NLS.bind(Messages.IRCChannelContainer_Exception_Connect_Failed, connectID.getName()), e);
			} finally {
				connectWaiting = false;
			}
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
		fireContainerEvent(new ContainerDisconnectingEvent(getID(), targetID));
		if (targetID != null)
			rootContainer.doPartChannel(targetID.getName());
		fireContainerEvent(new ContainerDisconnectedEvent(getID(), targetID));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class serviceType) {
		if (serviceType != null && serviceType.isInstance(this)) {
			return this;
		}
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(StringID.class.getName());
	}

	protected boolean isLocalUserChannelOperator() {
		return (channelOperator != null && isLocalUserChannelOperator(channelOperator));
	}

	protected boolean isLocalUserChannelOperator(String chOperator) {
		if (!isChannelOperator(chOperator))
			return false;
		String localUserName = (ircUser == null) ? null : (OPERATOR_PREFIX + ircUser.getNick());
		if (localUserName == null)
			return false;
		if (chOperator.equals(localUserName))
			return true;
		return false;
	}

	protected void setChannelOperator(String channelOperator) {
		this.channelOperator = channelOperator;
	}

	public void sendChatMessage(ID toID, ID threadID, org.eclipse.ecf.presence.im.IChatMessage.Type type, String subject, String body, Map properties) throws ECFException {
		rootContainer.sendChatMessage(toID, body);
	}

	public void sendChatMessage(ID toID, String body) throws ECFException {
		rootContainer.sendChatMessage(toID, body);
	}

	public IChatMessageSender getPrivateMessageSender() {
		return this;
	}

	public ID[] getChatRoomParticipants() {
		return (ID[]) channelParticipants.toArray(new ID[channelParticipants.size()]);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#getChatRoomAdminSender()
	 */
	public IChatRoomAdminSender getChatRoomAdminSender() {
		synchronized (this) {
			if (adminSender == null) {
				adminSender = new IChatRoomAdminSender() {
					public void sendSubjectChange(String newsubject) throws ECFException {
						rootContainer.doSendSubjectChangeMessage(targetID.getName(), newsubject);
					}
				};
			}
		}
		return adminSender;
	}
}