channel.firePresenceListeners(false, kicked);

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.irc.container;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.provider.irc.Activator;
import org.eclipse.ecf.presence.chatroom.ChatRoomCreateException;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainerOptionsAdapter;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomInvitationListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;
import org.eclipse.ecf.provider.irc.identity.IRCID;
import org.schwering.irc.lib.IRCConnection;
import org.schwering.irc.lib.IRCEventListener;
import org.schwering.irc.lib.IRCModeParser;
import org.schwering.irc.lib.IRCUser;
import org.schwering.irc.lib.ssl.SSLIRCConnection;

/**
 * IRC 'root' container implementation. This class implements the
 * IChatRoomManager and the IChatRoomContainer interfaces, allowing it to
 * function as both a manager of IRC channels and as an IRC channel itself.
 * 
 */
public class IRCRootContainer extends IRCAbstractContainer implements
		IContainer, IChatRoomManager, IChatRoomContainer, IRCMessageChannel,
		IChatRoomContainerOptionsAdapter {

	protected IRCConnection connection = null;

	protected ReplyHandler replyHandler = null;

	protected Map channels = new HashMap();

	protected IRCUser ircUser;

	protected String encoding = null;

	private ArrayList invitationListeners;

	public IRCRootContainer(ID localID) throws IDCreateException {
		this.localID = localID;
		this.unknownID = IDFactory.getDefault().createStringID("host");
		this.replyHandler = new ReplyHandler();
		invitationListeners = new ArrayList();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID targetID, IConnectContext connectContext)
			throws ContainerConnectException {
		if (connection != null)
			throw new ContainerConnectException("Already connected");
		if (targetID == null)
			throw new ContainerConnectException("targetID cannot be null");
		if (!(targetID instanceof IRCID))
			throw new ContainerConnectException("targetID " + targetID
					+ " not instance of IRCID");
		fireContainerEvent(new ContainerConnectingEvent(this.getID(), targetID,
				connectContext));
		// Get password via callback in connectContext
		String pw = getPasswordFromConnectContext(connectContext);
		IRCID tID = (IRCID) targetID;
		String host = tID.getHost();
		int port = tID.getPort();
		String pass = pw;
		String nick = tID.getUser();
		String user = nick;
		String name = null;
		boolean ssl = false;
		if (!ssl) {
			connection = new IRCConnection(host, new int[] { port }, pass,
					nick, user, name);
		} else {
			connection = new SSLIRCConnection(host, new int[] { port }, pass,
					nick, user, name);
		}
		// connection setup
		connection.addIRCEventListener(getIRCEventListener());
		connection.setPong(true);
		connection.setDaemon(false);
		connection.setColors(false);
		if (encoding != null)
			connection.setEncoding(encoding);
		trace("connecting to " + targetID);
		try {
			connection.connect();
		} catch (IOException e) {
			throw new ContainerConnectException("IRC connect exception", e);
		}
		this.targetID = tID;
	}

	protected void handleDisconnected() {
		for (Iterator i = channels.values().iterator(); i.hasNext();) {
			IRCChannelContainer c = (IRCChannelContainer) i.next();
			c.disconnect();
		}
		fireContainerEvent(new ContainerDisconnectedEvent(getID(), targetID));
		channels.clear();
	}

	protected IRCEventListener getIRCEventListener() {
		return new IRCEventListener() {
			public void onRegistered() {
				trace("handleOnRegistered()");
				fireContainerEvent(new ContainerConnectedEvent(
						IRCRootContainer.this.getID(), targetID));
			}

			public void onDisconnected() {
				trace("handleOnDisconnected()");
				showMessage(null, "Disconnected");
				handleDisconnected();
			}

			public void onError(String arg0) {
				trace("handleOnError(" + arg0 + ")");
				showMessage(null, "ERROR: " + arg0);
			}

			public void onError(int arg0, String arg1) {
				trace("handleOnError(" + arg0 + "," + arg1 + ")");
				showMessage(null, "ERROR: " + arg0 + "," + arg1);
			}

			public void onInvite(String arg0, IRCUser arg1, String arg2) {
				handleInvite(createIDFromString(arg0), createIDFromString(arg1
						.getNick()));
			}

			public void onJoin(String arg0, IRCUser arg1) {
				trace("handleOnJoin(" + arg0 + "," + arg1 + ")");
				IRCChannelContainer container = getChannel(arg0);
				if (container != null) {
					container.setIRCUser(arg1);
				}
			}

			public void onKick(String channelName, IRCUser kicker,
					String kicked, String kickerName) {
				trace("handleOnKick(" + channelName + "," + kicker + ","
						+ kicked + "," + kickerName + ")");
				// retrieve the channel that this kick is happening at
				IRCChannelContainer channel = getChannel(channelName);
				if (channel != null) {
					// display a message to indicate the kicking
					showMessage(channelName, kickerName + " has kicked "
							+ kicked + " from " + channelName + ".");
					// check if we are the ones that have been kicked
					if (kicked.equals(((IRCID) targetID).getUsername())) {
						// fire disconnection events for this channel container
						channel.fireContainerDisconnectingEvent();
						// FIXME: we don't fire presence listeners for ourselves
						// to prevent hanging the Eclipse workbench with
						// org.eclipse.ecf.examples.collab, this is a HACK
						// channel.firePresenceListeners(false, kicked);
						channel.fireContainerDisconnectedEvent();
					} else {
						channel.firePresenceListeners(false, kicked);
					}
				}
			}

			public void onMode(String arg0, IRCUser arg1, IRCModeParser arg2) {
				trace("handleOnMode(" + arg0 + "," + arg1 + "," + arg2 + ")");
			}

			public void onMode(IRCUser arg0, String arg1, String arg2) {
				trace("handleOnMode(" + arg0 + "," + arg1 + "," + arg2 + ")");
			}

			public void onNick(IRCUser arg0, String arg1) {
				trace("handleOnNick(" + arg0 + "," + arg1 + ")");
			}

			public void onNotice(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnNotice(" + arg0 + "," + arg1 + "," + arg2 + ")");
				showMessage(arg0, arg2);
			}

			public void onPart(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnPart(" + arg0 + "," + arg1 + "," + arg2 + ")");
				IRCChannelContainer channel = (IRCChannelContainer) channels
						.get(arg0);
				if (channel != null) {
					channel.firePresenceListeners(false, getIRCUserName(arg1));
				}
			}

			public void onPing(String arg0) {
				trace("handleOnPing(" + arg0 + ")");
				synchronized (IRCRootContainer.this) {
					if (connection != null) {
						connection.doPong(arg0);
					}
				}
			}

			public void onPrivmsg(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnPrivmsg(" + arg0 + "," + arg1 + "," + arg2 + ")");
				showMessage(arg0, arg1.toString(), arg2);
			}

			public void onQuit(IRCUser arg0, String arg1) {
				trace("handleOnQuit(" + arg0 + "," + arg1 + ")");
				for (Iterator i = channels.values().iterator(); i.hasNext();) {
					IRCChannelContainer container = (IRCChannelContainer) i
							.next();
					container.handleUserQuit(getIRCUserName(arg0));
				}
			}

			public void onReply(int arg0, String arg1, String arg2) {
				trace("handleOnReply(" + arg0 + "|" + arg1 + "|" + arg2 + ")");
				replyHandler.handleReply(arg0, arg1, arg2);
			}

			public void onTopic(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnTopic(" + arg0 + "," + arg1 + "," + arg2 + ")");
				showMessage(arg0, arg1.getNick()
						+ " has changed the topic to: " + arg2);
			}

			public void unknown(String arg0, String arg1, String arg2,
					String arg3) {
				trace("handleUnknown(" + arg0 + "," + arg1 + "," + arg2 + ","
						+ arg3 + ")");
				showMessage(null, "UNKNOWN MESSAGE: " + arg0 + "," + arg1 + ","
						+ arg2 + "," + arg3);
			}
		};
	}

	protected String getIRCUserName(IRCUser user) {
		if (user == null)
			return null;
		else
			return user.toString();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
		if (connection != null) {
			connection.close();
			connection = null;
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class serviceType) {
		if (serviceType == null)
			return null;
		if (serviceType.equals(IChatRoomManager.class)
				|| serviceType.equals(IChatRoomContainerOptionsAdapter.class))
			return this;
		else
			return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(
				Activator.NAMESPACE_IDENTIFIER);
	}

	public IChatRoomInfo getChatRoomInfo(final String roomName) {
		if (roomName == null)
			return new IChatRoomInfo() {
				public IChatRoomContainer createChatRoomContainer()
						throws ContainerCreateException {
					return IRCRootContainer.this;
				}

				public ID getConnectedID() {
					return IRCRootContainer.this.getConnectedID();
				}

				public String getDescription() {
					return ""; //$NON-NLS-1$
				}

				public String getName() {
					return ROOT_ROOMNAME;
				}

				public int getParticipantsCount() {
					return 0;
				}

				public ID getRoomID() {
					return getSystemID();
				}

				public String getSubject() {
					return ""; //$NON-NLS-1$
				}

				public boolean isModerated() {
					return false;
				}

				public boolean isPersistent() {
					return false;
				}

				public boolean requiresPassword() {
					return false;
				}

				public Object getAdapter(Class adapter) {
					return null;
				}
			};
		else
			return new IChatRoomInfo() {
				public IChatRoomContainer createChatRoomContainer()
						throws ContainerCreateException {
					try {
						IRCChannelContainer newChannelContainer = new IRCChannelContainer(
								IRCRootContainer.this, IDFactory.getDefault()
										.createGUID());
						addChannel(roomName, newChannelContainer);
						return newChannelContainer;
					} catch (Exception e) {
						throw new ContainerCreateException(
								"Exception creating IRCChannelContainer", e);
					}
				}

				public ID getConnectedID() {
					return IRCRootContainer.this.getConnectedID();
				}

				public String getDescription() {
					return ""; //$NON-NLS-1$
				}

				public String getName() {
					return roomName;
				}

				public int getParticipantsCount() {
					return 0;
				}

				public ID getRoomID() {
					return createIDFromString(roomName);
				}

				public String getSubject() {
					return ""; //$NON-NLS-1$
				}

				public boolean isModerated() {
					return false;
				}

				public boolean isPersistent() {
					return false;
				}

				public boolean requiresPassword() {
					return false;
				}

				public Object getAdapter(Class adapter) {
					return null;
				}
			};
	}

	public IChatRoomInfo[] getChatRoomInfos() {
		return null;
	}

	public IChatRoomManager[] getChildren() {
		return null;
	}

	public IChatRoomManager getParent() {
		return null;
	}

	public void addChatRoomParticipantListener(
			IChatRoomParticipantListener participantListener) {
		// for root container, no participant listening
	}

	public void removeChatRoomParticipantListener(
			IChatRoomParticipantListener participantListener) {
	}

	public IChatRoomMessageSender getChatRoomMessageSender() {
		return new IChatRoomMessageSender() {
			public void sendMessage(String message) throws ECFException {
				parseMessageAndSend(message);
			}
		};
	}

	protected void parseMessageAndSend(String message) {
		if (isCommand(message)) {
			String[] tokens = parseCommandTokens(message);
			synchronized (this) {
				if (connection != null) {
					handleCommandMessage(tokens);
				} else {
					trace("parseMessageAndSend(" + message
							+ ") Not connected for IRCContainer " + getID());
				}
			}
		} else {
			trace(message + " is not a command");
		}
	}

	private synchronized void handleCommandMessage(String[] tokens) {
		// Look at first one and switch
		String command = tokens[0];
		while (command.startsWith(COMMAND_PREFIX))
			command = command.substring(1);
		String[] args = new String[tokens.length - 1];
		System.arraycopy(tokens, 1, args, 0, tokens.length - 1);
		if (command.equalsIgnoreCase(JOIN_COMMAND)) {
			if (args.length > 1) {
				connection.doJoin(args[0], args[1]);
			} else if (args.length > 0) {
				connection.doJoin(args[0]);
			}
		} else if (command.equalsIgnoreCase(LIST_COMMAND)) {
			if (args.length > 0) {
				connection.doList(args[0]);
			} else
				connection.doList();
		} else if (command.equalsIgnoreCase(PART_COMMAND)) {
			if (args.length > 1) {
				connection.doPart(args[0], args[1]);
			} else if (args.length > 0) {
				connection.doPart(args[0]);
			}
		} else if (command.equalsIgnoreCase(NICK_COMMAND)) {
			if (args.length > 0) {
				connection.doNick(args[0]);
			}
		} else if (command.equalsIgnoreCase(MSG_COMMAND)) {
			if (args.length > 1) {
				connection.doPrivmsg(args[0], args[1]);
			}
		} else if (command.equalsIgnoreCase(NOTICE_COMMAND)) {
			if (args.length > 1) {
				connection.doNotice(args[0], args[1]);
			}
		} else if (command.equalsIgnoreCase(WHOIS_COMMAND)) {
			if (args.length > 0) {
				connection.doWhois(args[0]);
			}
		} else if (command.equalsIgnoreCase(QUIT_COMMAND)) {
			if (args.length > 0) {
				connection.doQuit(args[0]);
			} else {
				connection.doQuit();
			}
		} else if (command.equalsIgnoreCase(AWAY_COMMAND)) {
			if (args.length > 0) {
				connection.doAway(args[0]);
			} else {
				connection.doAway();
			}
		} else if (command.equalsIgnoreCase(TOPIC_COMMAND)) {
			if (args.length > 1) {
				StringBuffer sb = new StringBuffer();
				for (int i = 1; i < args.length; i++) {
					if (i > 1) {
						sb.append(COMMAND_DELIM);
					}
					sb.append(args[i]);
				}
				connection.doTopic(args[0], sb.toString());
			} else if (args.length > 0) {
				connection.doTopic(args[0]);
			}
		} else if (command.equalsIgnoreCase(INVITE_COMMAND)) {
			if (args.length > 1) {
				connection.doInvite(args[0], args[1]);
			}
		} else {
			trace("Unrecognized command '" + command + "' in IRCContainer "
					+ getID());
		}
	}

	private void handleInvite(ID channelID, ID fromID) {
		synchronized (invitationListeners) {
			for (int i = 0; i < invitationListeners.size(); i++) {
				IChatRoomInvitationListener icril = (IChatRoomInvitationListener) invitationListeners
						.get(i);
				icril.handleInvitationReceived(channelID, fromID, null, null);
			}
		}
	}

	protected IRCChannelContainer getChannel(String channel) {
		if (channel == null)
			return null;
		IRCChannelContainer container = getContainerForChannel(channel);
		if (container == null)
			return null;
		return container;
	}

	private void showMessage(String channel, String msg) {
		IRCChannelContainer msgChannel = getChannel(channel);
		if (msgChannel != null)
			msgChannel.fireMessageListeners(createIDFromString(channel), msg);
		else
			fireMessageListeners((channel == null) ? getSystemID()
					: createIDFromString(channel), msg);
	}

	private void showMessage(String channel, String user, String msg) {
		IRCChannelContainer msgChannel = getChannel(channel);
		if (msgChannel != null)
			msgChannel.fireMessageListeners(createIDFromString(user), msg);
		else
			fireMessageListeners(createIDFromString(user), msg);
	}

	private ID getSystemID() {
		if (targetID == null)
			return unknownID;
		try {
			return IDFactory.getDefault().createStringID(
					((IRCID) targetID).getHost());
		} catch (IDCreateException e) {
			Activator.log(
					"ID creation exception in IRCContainer.getSystemID()", e);
			return unknownID;
		}
	}

	protected void handle353Reply(String channel, String[] strings) {
		IRCChannelContainer container = getChannel(channel);
		if (container == null) {
			showMessage(null, "353 reply for channel " + channel + " not found");
		} else
			container.firePresenceListeners(true, strings);
	}

	protected class ReplyHandler {
		public void handleReply(int code, String arg1, String arg2) {
			String[] users = parseUsers(arg1);
			switch (code) {
			case 353:
				handle353Reply(users[2], parseUserNames(arg2));
				break;
			case 311:
				showMessage(null, "whois " + users[1]);
				showMessage(null, trimUsername(users[2]) + "@" + users[3]);
				break;
			case 312:
				showMessage(null, "server: " + users[2] + " - " + arg2);
				break;
			case 317:
				showMessage(null, users[2] + " seconds idle");
				break;
			case 318:
				showMessage(null, "whois end");
				break;
			case 319:
				showMessage(null, "channels: " + arg2);
				break;
			case 320:
				break;
			default:
				// first user always expected to be us
				if (users.length < 2)
					showMessage(null, arg2);
				else {
					showMessage(users[1], concat(users, 2, arg2));
				}
			}
		}

		private String trimUsername(String un) {
			int eq = un.indexOf('=');
			return un.substring(eq + 1);
		}
	}

	protected void doJoinChannel(String channelName, String key) {
		if (connection != null) {
			if (key == null || key.equals("")) { //$NON-NLS-1$
				connection.doJoin(channelName);
			} else {
				connection.doJoin(channelName, key);
			}
		}
	}

	protected void doPartChannel(String channelName) {
		if (connection != null) {
			connection.doPart(channelName);
		}
	}

	protected void doSendChannelMessage(String channelName, String ircUser,
			String msg) {
		if (connection != null) {
			connection.doPrivmsg(channelName, msg);
			showMessage(channelName, ircUser, msg);
		}
	}

	protected void addChannel(String channel, IRCChannelContainer container) {
		channels.put(channel, container);
	}

	protected IRCChannelContainer getContainerForChannel(String channel) {
		return (IRCChannelContainer) channels.get(channel);
	}

	protected void removeChannel(String channel) {
		channels.remove(channel);
	}

	public boolean setEncoding(String encoding) {
		if (connection == null) {
			this.encoding = encoding;
			return true;
		} else
			return false;
	}

	public void addInvitationListener(IChatRoomInvitationListener listener) {
		if (listener != null) {
			synchronized (invitationListeners) {
				if (!invitationListeners.contains(listener)) {
					invitationListeners.add(listener);
				}
			}
		}
	}

	public void removeInvitationListener(IChatRoomInvitationListener listener) {
		if (listener != null) {
			synchronized (invitationListeners) {
				invitationListeners.remove(listener);
			}
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomManager#createChatRoom(java.lang.String,
	 *      java.util.Map)
	 */
	public IChatRoomInfo createChatRoom(String roomname, Map properties)
			throws ChatRoomCreateException {
		throw new ChatRoomCreateException(roomname, "creation not supported",
				null);
	}
}