throw new TimeoutException(NLS.bind(Messages.IRCRootContainer_Connect_Timeout, tID.getName()), CONNECT_TIMEOUT);

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *    Jacek Pospychala <jacek.pospychala@pl.ibm.com> - bug 197604, 197329
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.irc.container;

import java.util.*;
import org.eclipse.ecf.core.*;
import org.eclipse.ecf.core.events.*;
import org.eclipse.ecf.core.identity.*;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.core.util.TimeoutException;
import org.eclipse.ecf.internal.provider.irc.Activator;
import org.eclipse.ecf.internal.provider.irc.Messages;
import org.eclipse.ecf.internal.provider.irc.identity.IRCID;
import org.eclipse.ecf.internal.provider.irc.identity.IRCNamespace;
import org.eclipse.ecf.presence.chatroom.*;
import org.eclipse.ecf.presence.history.IHistory;
import org.eclipse.ecf.presence.history.IHistoryManager;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.ecf.presence.im.IChatMessage.Type;
import org.eclipse.osgi.util.NLS;
import org.schwering.irc.lib.*;
import org.schwering.irc.lib.ssl.SSLIRCConnection;

/**
 * IRC 'root' container implementation. This class implements the
 * IChatRoomManager and the IChatRoomContainer interfaces, allowing it to
 * function as both a manager of IRC channels and as an IRC channel itself.
 * 
 */
public class IRCRootContainer extends IRCAbstractContainer implements IContainer, IChatMessageSender, IChatRoomInvitationSender, IChatRoomManager, IChatRoomContainer, IRCMessageChannel, IChatRoomContainerOptionsAdapter {

	private static final long CONNECT_TIMEOUT = 20000;

	protected IRCConnection connection = null;

	protected ReplyHandler replyHandler = null;

	protected Map channels = new HashMap();

	protected String username;

	protected String encoding = null;

	private ArrayList invitationListeners;

	protected Object connectLock = new Object();
	protected boolean connectWaiting = false;
	protected Exception connectException = null;

	public IRCRootContainer(ID localID) throws IDCreateException {
		this.localID = localID;
		this.unknownID = IDFactory.getDefault().createStringID(Messages.IRCRootContainer_0);
		this.replyHandler = new ReplyHandler();
		invitationListeners = new ArrayList();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID,
	 *      org.eclipse.ecf.core.security.IConnectContext)
	 */
	public void connect(ID connectID, IConnectContext connectContext) throws ContainerConnectException {
		if (connection != null)
			throw new ContainerConnectException(Messages.IRCRootContainer_Exception_Already_Connected);
		if (connectID == null)
			throw new ContainerConnectException(Messages.IRCRootContainer_Exception_TargetID_Null);
		if (!(connectID instanceof IRCID))
			throw new ContainerConnectException(NLS.bind(Messages.IRCRootContainer_Exception_TargetID_Wrong_Type, new Object[] {targetID, IRCID.class.getName()}));
		if (connectWaiting)
			throw new ContainerConnectException(Messages.IRCRootContainer_Connecting);

		fireContainerEvent(new ContainerConnectingEvent(this.getID(), connectID, connectContext));
		// Get password via callback in connectContext
		String pw = getPasswordFromConnectContext(connectContext);
		IRCID tID = (IRCID) connectID;
		String host = tID.getHost();
		int port = tID.getPort();
		String pass = pw;
		String nick = tID.getUser();
		String user = nick;
		this.username = user;
		String name = null;
		boolean ssl = false;
		if (!ssl) {
			connection = new IRCConnection(host, new int[] {port}, pass, nick, user, name);
		} else {
			connection = new SSLIRCConnection(host, new int[] {port}, pass, nick, user, name);
		}
		// connection setup
		connection.addIRCEventListener(getIRCEventListener());
		connection.setPong(true);
		connection.setDaemon(false);
		connection.setColors(true);
		if (encoding != null)
			connection.setEncoding(encoding);
		trace(Messages.IRCRootContainer_Connecting_To + targetID);
		synchronized (connectLock) {
			connectWaiting = true;
			connectException = null;
			try {
				connection.connect();
				long timeout = CONNECT_TIMEOUT + System.currentTimeMillis();
				while (connectWaiting && (timeout > System.currentTimeMillis())) {
					connectLock.wait(2000);
				}
				if (connectWaiting)
					throw new TimeoutException(CONNECT_TIMEOUT, NLS.bind(Messages.IRCRootContainer_Connect_Timeout, tID.getName()));
				if (connectException != null)
					throw connectException;
				this.targetID = tID;
				fireContainerEvent(new ContainerConnectedEvent(getID(), this.targetID));
			} catch (Exception e) {
				this.targetID = null;
				throw new ContainerConnectException(NLS.bind(Messages.IRCRootContainer_Exception_Connect_Failed, connectID.getName()), e);
			} finally {
				connectWaiting = false;
				connectException = null;
			}
		}
	}

	protected void handleDisconnected() {
		for (Iterator i = channels.values().iterator(); i.hasNext();) {
			IRCChannelContainer c = (IRCChannelContainer) i.next();
			c.disconnect();
		}
		fireContainerEvent(new ContainerDisconnectedEvent(getID(), targetID));
		channels.clear();
	}

	protected void handleErrorIfConnecting(String message) {
		synchronized (connectLock) {
			if (connectWaiting)
				this.connectException = new Exception(message);
		}
	}

	protected IRCEventListener getIRCEventListener() {
		return new IRCEventListener() {
			public void onRegistered() {
				trace("handleOnRegistered()"); //$NON-NLS-1$
				synchronized (connectLock) {
					connectWaiting = false;
					connectLock.notify();
				}
			}

			public void onDisconnected() {
				trace("handleOnDisconnected()"); //$NON-NLS-1$
				synchronized (connectLock) {
					if (connectWaiting) {
						if (connectException == null)
							connectException = new Exception(Messages.IRCRootContainer_Exception_Unexplained_Disconnect);
						connectWaiting = false;
						connectLock.notify();
					}
				}
				if (targetID != null) {
					showMessage(null, NLS.bind(Messages.IRCRootContainer_Disconnected, targetID.getName()));
					handleDisconnected();
				}
			}

			public void onError(String arg0) {
				trace("handleOnError(" + arg0 + ")"); //$NON-NLS-1$ //$NON-NLS-2$
				showMessage(null, NLS.bind(Messages.IRCRootContainer_Error, arg0));
				handleErrorIfConnecting(arg0);
			}

			public void onError(int arg0, String arg1) {
				String msg = arg0 + "," + arg1; //$NON-NLS-1$
				trace("handleOnError(" + msg + ")"); //$NON-NLS-1$ //$NON-NLS-2$
				showMessage(null, NLS.bind(Messages.IRCRootContainer_Error, msg));
				handleErrorIfConnecting(arg0 + msg);
			}

			public void onInvite(String arg0, IRCUser arg1, String arg2) {
				handleInvite(createIDFromString(arg0), createIDFromString(arg1.getNick()));
			}

			public void onJoin(String arg0, IRCUser arg1) {
				trace("handleOnJoin(" + arg0 + "," + arg1 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
				IRCChannelContainer container = getChannel(arg0);
				if (container != null) {
					container.setIRCUser(arg1);
				}
			}

			public void onKick(String channelName, IRCUser kicker, String kicked, String reason) {
				trace("handleOnKick(" + channelName + "," + kicker + "," //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
						+ kicked + "," + reason + ")"); //$NON-NLS-1$ //$NON-NLS-2$
				// retrieve the channel that this kick is happening at
				IRCChannelContainer channel = getChannel(channelName);
				if (channel != null) {
					// display a message to indicate that a user has been kicked
					// from the channel
					showMessage(channelName, NLS.bind(Messages.IRCRootContainer_UserKicked, new Object[] {kicker.getNick(), kicked, channelName, reason}));
					// check if we are the ones that have been kicked
					if (kicked.equals(((IRCID) targetID).getUsername())) {
						// fire disconnection events for this channel container
						channel.fireContainerEvent(new ContainerDisconnectingEvent(channel.getID(), channel.targetID));
						channel.firePresenceListeners(false, new String[] {kicked});
						channel.fireContainerEvent(new ContainerDisconnectedEvent(channel.getID(), channel.targetID));
					} else {
						channel.firePresenceListeners(false, new String[] {kicked});
					}
				}
			}

			public void onMode(String arg0, IRCUser arg1, IRCModeParser arg2) {
				trace("handleOnMode(" + arg0 + "," + arg1 + "," + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
			}

			public void onMode(IRCUser arg0, String arg1, String arg2) {
				trace("handleOnMode(" + arg0 + "," + arg1 + "," + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
			}

			public void onNick(IRCUser arg0, String arg1) {
				trace("handleOnNick(" + arg0 + "," + arg1 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
			}

			public void onNotice(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnNotice(" + arg0 + "," + arg1 + "," + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
				showMessage(arg0, arg2);
			}

			public void onPart(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnPart(" + arg0 + "," + arg1 + "," + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
				IRCChannelContainer channel = (IRCChannelContainer) channels.get(arg0);
				if (channel != null) {
					channel.firePresenceListeners(false, new String[] {getIRCUserName(arg1)});
				}
			}

			public void onPing(String arg0) {
				trace("handleOnPing(" + arg0 + ")"); //$NON-NLS-1$ //$NON-NLS-2$
				synchronized (IRCRootContainer.this) {
					if (connection != null) {
						connection.doPong(arg0);
					}
				}
			}

			public void onPrivmsg(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnPrivmsg(" + arg0 + "," + arg1 + "," + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$ 
				if (arg2.equals("\01VERSION\01")) { //$NON-NLS-1$
					showMessage(null, NLS.bind(Messages.IRCRootContainer_CTCP_VERSION_Request, arg1.toString()));
				} else {
					showMessage(arg0, arg1.toString(), arg2);
				}

			}

			public void onQuit(IRCUser arg0, String arg1) {
				trace("handleOnQuit(" + arg0 + "," + arg1 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
				for (Iterator i = channels.values().iterator(); i.hasNext();) {
					IRCChannelContainer container = (IRCChannelContainer) i.next();
					container.handleUserQuit(getIRCUserName(arg0));
				}
			}

			public void onReply(int arg0, String arg1, String arg2) {
				trace("handleOnReply(" + arg0 + "|" + arg1 + "|" + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
				replyHandler.handleReply(arg0, arg1, arg2);
			}

			public void onTopic(String arg0, IRCUser arg1, String arg2) {
				trace("handleOnTopic(" + arg0 + "," + arg1 + "," + arg2 + ")"); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
				handleSetSubject(arg0, arg1, arg2);
			}

			public void unknown(String arg0, String arg1, String arg2, String arg3) {
				trace("handleUnknown(" + arg0 + "," + arg1 + "," + arg2 + "," //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$ //$NON-NLS-4$
						+ arg3 + ")"); //$NON-NLS-1$
				showMessage(null, NLS.bind(Messages.IRCRootContainer_Unknown_Message, new Object[] {arg0, arg1, arg2, arg3}));
			}
		};
	}

	protected String getIRCUserName(IRCUser user) {
		return user == null ? null : user.toString();
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
			targetID = null;
		}
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
		return IDFactory.getDefault().getNamespaceByName(IRCNamespace.IRC_SCHEME);
	}

	public IChatRoomInfo getChatRoomInfo(final String roomName) {
		if (roomName == null)
			return new IChatRoomInfo() {
				public IChatRoomContainer createChatRoomContainer() throws ContainerCreateException {
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
		return new IChatRoomInfo() {
			public IChatRoomContainer createChatRoomContainer() throws ContainerCreateException {
				try {
					IRCChannelContainer newChannelContainer = new IRCChannelContainer(IRCRootContainer.this, IDFactory.getDefault().createGUID());
					addChannel(roomName, newChannelContainer);
					return newChannelContainer;
				} catch (Exception e) {
					throw new ContainerCreateException(Messages.IRCRootContainer_Exception_Create_ChatRoom, e);
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
		return new IChatRoomInfo[0];
	}

	public IChatRoomManager[] getChildren() {
		return new IChatRoomManager[0];
	}

	public IChatRoomManager getParent() {
		return null;
	}

	public void addChatRoomParticipantListener(IChatRoomParticipantListener participantListener) {
		// for root container, no participant listening
	}

	public void removeChatRoomParticipantListener(IChatRoomParticipantListener participantListener) {
		// for root container, no participant listening
	}

	public IChatRoomMessageSender getChatRoomMessageSender() {
		return new IChatRoomMessageSender() {
			public void sendMessage(String message) throws ECFException {
				if (isCommand(message))
					parseCommandAndSend(message, null, null);
				else
					showErrorMessage(null, NLS.bind(Messages.IRCRootContainer_Command_Error, message, COMMAND_PREFIX));
			}
		};
	}

	/**
	 * Returns string from the buffer beginning up to nearest COMMAND_DELIM. Strips trailing COMMAND_DELIMs.
	 * 
	 * @param buffer
	 * @return String up to first COMMAND_DELIM occurrence in buffer.
	 */
	protected String nextToken(StringBuffer buffer) {
		if (buffer.length() == 0) {
			return null;
		}

		String token;

		int index = buffer.indexOf(COMMAND_DELIM);

		if (index == -1) { // no delim until the end of buffer
			token = buffer.toString();
			buffer.delete(0, buffer.length());
			return token;
		}

		token = buffer.substring(0, index);

		/*if (token.length() == buffer.length()) {
			//index = token.length() - 1;
		} */

		// trim trailing command delims
		while ((buffer.length() > index) && (buffer.indexOf(COMMAND_DELIM, index) == index)) {
			index += COMMAND_DELIM.length();
		}
		if (index > 0) {
			buffer.delete(0, index);
		}

		return token;
	}

	protected void parseCommandAndSend(String commandMessage, String channelName, String ircUser) {
		synchronized (this) {
			if (connection != null) {
				try {
					String lowerCase = commandMessage.toLowerCase();
					StringBuffer command = new StringBuffer(commandMessage);

					if (lowerCase.startsWith("/msg ")) { //$NON-NLS-1$
						commandMessage = commandMessage.substring(5);
						int index = commandMessage.indexOf(COMMAND_DELIM);
						if (index != -1) {
							connection.doPrivmsg(commandMessage.substring(0, index), commandMessage.substring(index + 1));
						}
					} else if (lowerCase.startsWith("/privmsg ")) { //$NON-NLS-1$
						commandMessage = commandMessage.substring(9);
						int index = commandMessage.indexOf(COMMAND_DELIM);
						if (index != -1) {
							connection.doPrivmsg(commandMessage.substring(0, index), commandMessage.substring(index + 1));
						}
					} else if (lowerCase.startsWith("/op ")) { //$NON-NLS-1$
						nextToken(command); // skip command

						String nick = nextToken(command);

						if (nick != null) {
							connection.doMode(channelName, "+o " + nick); //$NON-NLS-1$
						}
					} else if (lowerCase.startsWith("/dop ")) { //$NON-NLS-1$
						nextToken(command); // skip command

						String nick = nextToken(command);

						if (nick != null) {
							connection.doMode(channelName, "-o " + nick); //$NON-NLS-1$
						}
					} else if (lowerCase.startsWith("/ban ")) { //$NON-NLS-1$
						nextToken(command); // skip command

						String nick = nextToken(command);

						if (nick != null) {
							connection.doMode(channelName, "+b " + nick); //$NON-NLS-1$
						}
					} else if (lowerCase.startsWith("/unban ")) { //$NON-NLS-1$
						nextToken(command); // skip command

						String nick = nextToken(command);

						if (nick != null) {
							connection.doMode(channelName, "-b " + nick); //$NON-NLS-1$ 
						}
					} else if (lowerCase.startsWith("/kick ")) { //$NON-NLS-1$
						nextToken(command); // skip command

						String nick = nextToken(command);

						if (nick.startsWith("#")) { //$NON-NLS-1$
							channelName = nick;
							nick = nextToken(command);
						}

						String comment = command.toString(); // rest of command

						if (comment.length() > 0) {
							connection.doKick(channelName, nick, comment);
						} else {
							connection.doKick(channelName, nick);
						}
					} else if (lowerCase.startsWith("/mode ")) { //$NON-NLS-1$
						commandMessage = commandMessage.substring(6);
						int index = commandMessage.indexOf(COMMAND_DELIM);
						if (index != -1) {
							connection.doMode(channelName, commandMessage);
						}
					} else if (lowerCase.startsWith("/me ")) { //$NON-NLS-1$
						nextToken(command); // skip command

						String message = command.toString();
						if (message.length() > 0) {
							message = "\01ACTION " + message + "\01"; //$NON-NLS-1$ //$NON-NLS-2$
							connection.doPrivmsg(channelName, message);
							showMessage(channelName, ircUser, message);
						}
					} else {
						String[] tokens = parseCommandTokens(commandMessage);
						handleCommandMessage(tokens, channelName);
					}
				} catch (Exception e) {
					showErrorMessage(channelName, NLS.bind(Messages.IRCRootContainer_Exception_Parse, new Object[] {e.getClass().getName(), e.getLocalizedMessage()}));
					traceStack(e, "PARSE ERROR: " + commandMessage); //$NON-NLS-1$
				}
			} else {
				trace("parseMessageAndSend(" + commandMessage //$NON-NLS-1$
						+ ") Not connected for IRCContainer " + getID()); //$NON-NLS-1$
			}
		}
	}

	private synchronized void handleCommandMessage(String[] tokens, String channelName) {
		// Look at first one and switch
		String origCommand = tokens[0];
		String command = origCommand;
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
			String msg = NLS.bind(Messages.IRCRootContainer_Command_Unrecognized, origCommand);
			trace(msg + " in IRCContainer: " + getID()); //$NON-NLS-1$
			showErrorMessage(channelName, msg);
		}
	}

	protected void handleInvite(ID channelID, ID fromID) {
		synchronized (invitationListeners) {
			for (int i = 0; i < invitationListeners.size(); i++) {
				IChatRoomInvitationListener icril = (IChatRoomInvitationListener) invitationListeners.get(i);
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

	protected void showMessage(String channel, String msg) {
		IRCChannelContainer msgChannel = getChannel(channel);
		if (msgChannel != null)
			msgChannel.fireChatRoomMessageEvent(createIDFromString(channel), msg);
		else
			fireChatRoomMessageEvent((channel == null) ? getSystemID() : createIDFromString(channel), msg);
	}

	protected void showMessage(String channel, String user, String msg) {
		IRCChannelContainer msgChannel = getChannel(channel);
		if (msgChannel != null) {
			msgChannel.fireChatRoomMessageEvent(createIDFromString(user), msg);
		} else {
			fireChatMessageEvent(createIDFromString(user), msg);
			for (Iterator it = channels.values().iterator(); it.hasNext();) {
				msgChannel = (IRCChannelContainer) it.next();
				msgChannel.fireChatMessageEvent(createIDFromString(user), msg);
			}
		}
	}

	void showErrorMessage(String channel, String msg) {
		IRCChannelContainer msgChannel = getChannel(channel);
		if (msgChannel != null)
			msgChannel.fireChatRoomMessageEvent((username == null) ? getSystemID() : createIDFromString(username), msg);
		else
			fireChatRoomMessageEvent((username == null) ? getSystemID() : createIDFromString(username), msg);
	}

	ID getSystemID() {
		if (targetID == null)
			return unknownID;
		try {
			return IDFactory.getDefault().createStringID(((IRCID) targetID).getHost());
		} catch (IDCreateException e) {
			Activator.log("ID creation exception in IRCContainer.getSystemID()", e); //$NON-NLS-1$
			return unknownID;
		}
	}

	protected void handle353Reply(String channel, String[] strings) {
		IRCChannelContainer container = getChannel(channel);
		if (container == null) {
			showMessage(null, NLS.bind(Messages.IRCRootContainer_353_Error, channel));
		} else
			container.firePresenceListeners(true, strings);
	}

	protected class ReplyHandler {
		public void handleReply(int code, String arg1, String arg2) {
			String[] users = parseUsers(arg1);
			switch (code) {
				case 353 :
					handle353Reply(users[2], parseUserNames(arg2));
					break;
				case 311 :
					showMessage(null, NLS.bind(Messages.IRCRootContainer_Whois, users[1]));
					showMessage(null, trimUsername(users[2]) + "@" + users[3]); //$NON-NLS-1$
					break;
				case 312 :
					showMessage(null, NLS.bind(Messages.IRCRootContainer_Server, new Object[] {users[2], arg2}));
					break;
				case 317 :
					showMessage(null, NLS.bind(Messages.IRCRootContainer_Idle, users[2]));
					break;
				case 318 :
					showMessage(null, Messages.IRCRootContainer_Whois_End);
					break;
				case 319 :
					showMessage(null, NLS.bind(Messages.IRCRootContainer_Channels, arg2));
					break;
				case 320 :
					break;
				case 331 :
				case 332 :
					// Subject changes
					String[] args = parseCommandTokens(arg1);
					String channel = (args.length == 2) ? args[1] : ((args.length == 1) ? args[0] : null);
					handleSetSubject(channel, null, arg2);
					break;
				default :
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

	protected void handleSetSubject(String channelName, IRCUser user, String newSubject) {
		IRCChannelContainer channel = (IRCChannelContainer) channels.get(channelName);
		if (channel == null) {
			showMessage(null, newSubject);
			fireSubjectListeners(null, newSubject);
		} else {
			String nickname = (user == null) ? null : user.getNick();
			ID fromID = (user == null) ? null : createIDFromString(getIRCUserName(user));
			// Put out message to channel
			if (nickname == null)
				showMessage(channelName, newSubject);
			else
				showMessage(channelName, NLS.bind(Messages.IRCRootContainer_TopicChange, new Object[] {nickname, newSubject}));
			// Also notify subject listeners
			channel.fireSubjectListeners(fromID, newSubject);
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

	protected void doSendChannelMessage(String channelName, String ircUser, String msg) {
		if (connection != null) {
			// If it's a command,
			if (isCommand(msg)) {
				parseCommandAndSend(msg, channelName, ircUser);
			} else {
				connection.doPrivmsg(channelName, msg);
				showMessage(channelName, ircUser, msg);
			}
		}
	}

	protected void doSendSubjectChangeMessage(String channelName, String topic) throws ECFException {
		if (connection == null)
			throw new ECFException(Messages.IRCRootContainer_Exception_Unexplained_Disconnect);
		connection.doTopic(channelName, topic);
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
		}
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
	public IChatRoomInfo createChatRoom(String roomname, Map properties) throws ChatRoomCreateException {
		throw new ChatRoomCreateException(roomname, Messages.IRCRootContainer_Exception_Create_Not_Supported, null);
	}

	protected IHistoryManager chatRoomHistoryManager = new IHistoryManager() {

		public IHistory getHistory(ID chatRoomID, Map options) {
			// TODO Auto-generated method stub
			return null;
		}

		public boolean isActive() {
			// TODO Auto-generated method stub
			return false;
		}

		public void setActive(boolean active) {
			// TODO Auto-generated method stub

		}

		public Object getAdapter(Class adapter) {
			// TODO Auto-generated method stub
			return null;
		}

	};

	public IHistoryManager getHistoryManager() {
		return chatRoomHistoryManager;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomManager#getInvitationSender()
	 */
	public IChatRoomInvitationSender getInvitationSender() {
		return this;
	}

	public void sendInvitation(ID room, ID targetUser, String subject, String body) throws ECFException {
		if (connection == null)
			throw new ECFException(Messages.IRCRootContainer_EXCEPTION_CONNECTION_CANNOT_BE_NULL);
		connection.doInvite(targetUser.getName(), room.getName());
	}

	public void sendChatMessage(ID toID, ID threadID, Type type, String subject, String body, Map properties) throws ECFException {
		sendChatMessage(toID, body);
	}

	public void sendChatMessage(ID toID, String body) throws ECFException {
		if (toID == null) {
			throw new ECFException(Messages.IRCRootContainer_EXCEPTION_TARGETID_CANNOT_BE_NULL);
		}

		// FIXME: temporary workaround to allow for the sending of messages to users that are operators
		String name = toID.getName();
		if (name.charAt(0) == '@') {
			name = name.substring(1);
		}
		connection.doPrivmsg(name, body);
	}

	public IChatMessageSender getPrivateMessageSender() {
		return this;
	}

	public ID[] getChatRoomParticipants() {
		// root channel has no participants
		return new ID[0];
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#getChatRoomAdminSender()
	 */
	public IChatRoomAdminSender getChatRoomAdminSender() {
		return null;
	}

}