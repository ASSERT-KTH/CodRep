package org.eclipse.ecf.internal.provider.irc.container;

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
package org.eclipse.ecf.provider.irc.container;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.StringID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.TimeoutException;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;
import org.schwering.irc.lib.IRCUser;

/**
 * IContainer class used to represent a specific IRC channel (e.g. #eclipse-dev)
 *
 */
public class IRCChannelContainer extends IRCAbstractContainer implements
		IChatRoomContainer {
	
	private static final long CONNECT_TIMEOUT = 10000;

	protected List participantListeners = new ArrayList();
	protected IRCRootContainer rootContainer;
	protected  IRCUser ircUser = null;
	protected boolean channelOperator = false;
	
	protected Object connectLock = new Object();
	protected boolean connectWaiting = false;
	
	protected IChatRoomMessageSender sender = new IChatRoomMessageSender() {
		public void sendMessage(String message) throws ECFException {
			rootContainer.doSendChannelMessage(targetID.getName(), ircUser
			.toString(), message);
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
	public void addChatRoomParticipantListener(
			IChatRoomParticipantListener participantListener) {
		participantListeners.add(participantListener);
	}
	public void removeChatRoomParticipantListener(
			IChatRoomParticipantListener participantListener) {
		participantListeners.remove(participantListener);
	}
	protected void handleUserQuit(String name) {
		firePresenceListeners(false, new String[] { name });
	}
	private IPresence createPresence(final boolean available) {
		return new IPresence() {
			private static final long serialVersionUID = 1L;

			public Mode getMode() {
				return (available ? IPresence.Mode.AVAILABLE
						: IPresence.Mode.AWAY);
			}
			public Map getProperties() {
				return null;
			}
			public String getStatus() {
				return "";
			}
			public Type getType() {
				return (available ? IPresence.Type.AVAILABLE
						: IPresence.Type.UNAVAILABLE);
			}
			public Object getAdapter(Class adapter) {
				return null;
			}
			public byte[] getPictureData() {
				return new byte[0];
			}
		};
	}
	
	protected boolean isLocalUserChannelOperator(String user) {
		if (!user.startsWith(OPERATOR_PREFIX)) return false;
		String localUserName = (ircUser==null)?null:(OPERATOR_PREFIX+ircUser.getNick());
		if (localUserName==null) return false;
		if (user.equals(localUserName)) return true;
		return false;
	}
	
	protected void firePresenceListeners(boolean joined, String[] users) {
		for(Iterator i=participantListeners.iterator(); i.hasNext(); ) {
			IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();
			for(int j=0; j < users.length; j++) {
				ID fromID = createIDFromString(users[j]);
				boolean localUserIsChannelOperator = isLocalUserChannelOperator(users[j]);
				if (localUserIsChannelOperator) setChannelOperator(true);
				l.handlePresence(fromID,createPresence(joined));
				if (joined) l.handleArrivedInChat(fromID);
				else l.handleDepartedFromChat(fromID);
			}
		}
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
		if (user == null)
			return null;
		else
			return user.toString();
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
		}
		else
			firePresenceListeners(true, new String[] { getIRCUserName(user) });
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
	public void connect(ID targetID, IConnectContext connectContext)
			throws ContainerConnectException {
		// Actually do join here
		if (targetID == null)
			throw new ContainerConnectException("targetID cannot be null");
		if (connectWaiting) throw new ContainerConnectException("Connecting");
		// Get channel name
		String channelName = targetID.getName();
		fireContainerEvent(new ContainerConnectingEvent(this.getID(), targetID,
				connectContext));
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
					throw new TimeoutException(CONNECT_TIMEOUT, "Timeout connecting to "+targetID.getName());
				this.targetID = targetID;
				fireContainerEvent(new ContainerConnectedEvent(this.getID(), this.targetID));
			} catch (Exception e){
				throw new ContainerConnectException("Connect failed to "
						+ targetID.getName(), e);
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
		rootContainer.doPartChannel(targetID.getName());
		fireContainerEvent(new ContainerDisconnectedEvent(getID(), targetID));
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class serviceType) {
		return null;
	}
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(
				StringID.class.getName());
	}
	protected boolean isChannelOperator() {
		return channelOperator;
	}
	protected void setChannelOperator(boolean channelOperator) {
		this.channelOperator = channelOperator;
	}
}