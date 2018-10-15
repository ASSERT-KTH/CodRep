public IChatRoomInfo[] getChatRoomInfos() {

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

import java.io.IOException;
import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;
import java.util.Vector;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisposeEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.ObjectCallback;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.provider.irc.Activator;
import org.eclipse.ecf.internal.provider.irc.Trace;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
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
import org.schwering.irc.lib.SSLIRCConnection;

public class IRCContainer implements IContainer, IChatRoomManager, IChatRoomContainer {

	private static final String COMMAND_PREFIX = "/";
	private static final String COMMAND_DELIM = " ";
	private static final String JOIN_COMMAND = "JOIN";
	private static final String LIST_COMMAND = "LIST";
	private static final String PART_COMMAND = "PART";
	private static final String NICK_COMMAND = "NICK";
	private static final String MSG_COMMAND = "MSG";
	private static final String NOTICE_COMMAND = "NOTICE";
	private static final String WHOIS_COMMAND = "WHOIS";
	private static final String QUIT_COMMAND = "QUIT";
	private static final String AWAY_COMMAND = "AWAY";
	private static final String TOPIC_COMMAND = "TOPIC";
	private static final String INVITE_COMMAND = "INVITE";
	private static final String OPERATOR_PREFIX = "@";

	Trace trace = Trace.create("irccontainer");
	
	IRCConnection connection = null;
	IRCID targetID = null;
	ID localID = null;
	Vector msgListeners = new Vector();
	Vector participantListeners = new Vector();
	
	Hashtable channels = new Hashtable();
	boolean startchannel = false;
	String startchannelname = null;
	
	String joinedChannel = null;
	IRCUser ircUser = null;
	private Vector listeners = new Vector();

	protected ID unknownID = null;
	protected ReplyHandler replyHandler = new ReplyHandler();
	
	protected void fireContainerEvent(IContainerEvent event) {
		synchronized (listeners) {
			for (Iterator i = listeners.iterator(); i.hasNext();) {
				IContainerListener l = (IContainerListener) i.next();
				l.handleEvent(event);
			}
		}
	}
	protected IRCContainer addChannel(String channel, IRCContainer container) {
		if (channel == null) return null;
		return (IRCContainer) channels.put(channel, container);
	}
	protected IRCContainer getChannel(String channel) {
		if (channel == null) return null;
		return (IRCContainer) channels.get(channel);
	}
	protected void trace(String msg) {
		if (trace != null) {
			trace.msg(msg);
		}
	}
	protected void dumpStack(Throwable t, String msg) {
		if (trace != null) {
			trace.dumpStack(t,msg);
		}
	}
	public IRCContainer(ID localID) throws IDCreateException {
		super();
		this.localID = localID;
		this.unknownID = IDFactory.getDefault().createStringID("system.unknown");
	}
	protected IRCEventListener getIRCEventListener() {
		return new IRCEventListener() {
			public void onRegistered() {
				handleOnRegistered();
			}
			public void onDisconnected() {
				handleOnDisconnected();
			}
			public void onError(String arg0) {
				handleOnError(arg0);
			}
			public void onError(int arg0, String arg1) {
				handleOnError(arg0,arg1);
			}
			public void onInvite(String arg0, IRCUser arg1, String arg2) {
				handleOnInvite(arg0,arg1,arg2);
			}
			public void onJoin(String arg0, IRCUser arg1) {
				handleOnJoin(arg0,arg1);
			}
			public void onKick(String arg0, IRCUser arg1, String arg2, String arg3) {
				handleOnKick(arg0,arg1,arg2,arg3);
			}
			public void onMode(String arg0, IRCUser arg1, IRCModeParser arg2) {
				handleOnMode(arg0,arg1,arg2);
			}
			public void onMode(IRCUser arg0, String arg1, String arg2) {
				handleOnMode(arg0,arg1,arg2);
			}
			public void onNick(IRCUser arg0, String arg1) {
				handleOnNick(arg0,arg1);
			}
			public void onNotice(String arg0, IRCUser arg1, String arg2) {
				handleOnNotice(arg0,arg1,arg2);
			}
			public void onPart(String arg0, IRCUser arg1, String arg2) {
				handleOnPart(arg0,arg1,arg2);
			}
			public void onPing(String arg0) {
				handleOnPing(arg0);
			}
			public void onPrivmsg(String arg0, IRCUser arg1, String arg2) {
				handleOnPrivmsg(arg0,arg1,arg2);
			}
			public void onQuit(IRCUser arg0, String arg1) {
				handleOnQuit(arg0,arg1);
			}
			public void onReply(int arg0, String arg1, String arg2) {
				handleOnReply(arg0,arg1,arg2);
			}
			public void onTopic(String arg0, IRCUser arg1, String arg2) {
				handleOnTopic(arg0,arg1,arg2);
			}
			public void unknown(String arg0, String arg1, String arg2, String arg3) {
				handleUnknown(arg0,arg1,arg2,arg3);
			}};
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainer#connect(org.eclipse.ecf.core.identity.ID, org.eclipse.ecf.core.security.IConnectContext)
	 */
	public synchronized void connect(ID targetID, IConnectContext connectContext)
			throws ContainerConnectException {
		
		if (connection != null) throw new ContainerConnectException("Already connected");
		if (targetID == null) throw new ContainerConnectException("targetID cannot be null");
		if (!(targetID instanceof IRCID)) throw new ContainerConnectException("targetID "+targetID+" not instance of IRCID");
		
		fireContainerEvent(new ContainerConnectingEvent(this
				.getID(), targetID, connectContext));
		// Get password via callback in connectContext
		String pw = null;
		try {
			Callback[] callbacks = new Callback[1];
			callbacks[0] = new ObjectCallback();
			if (connectContext != null) {
				CallbackHandler handler = connectContext.getCallbackHandler();
				if (handler != null) {
					handler.handle(callbacks);
				}
			}
			ObjectCallback cb = (ObjectCallback) callbacks[0];
			pw = (String) cb.getObject();
		} catch (Exception e) {
			throw new ContainerConnectException("Exception in CallbackHandler.handle(<callbacks>)",e);
		}

		IRCID tID = (IRCID) targetID;
		String host = tID.getHost();
		int port = tID.getPort();
		String pass = pw;
		String nick = tID.getUser();
		String user = nick;
		String name = null;
		boolean ssl = false;
		if (!ssl) {
			connection = new IRCConnection(host,new int[] {port},pass,nick,user,name);
		} else {
			connection = new SSLIRCConnection(host,new int[] {port},pass,nick,user,name);
		}
		// connection setup
		connection.addIRCEventListener(getIRCEventListener());
		connection.setPong(true);
		connection.setDaemon(false);
		connection.setColors(false);
		
		// If channel is specified set ourselves to join that channel once we are actually connected to server
		String channel = tID.getChannel();
		if (channel != null && !channel.equals("")) {
			startchannel = true;
			startchannelname = channel;
			addChannel(startchannelname,this);
		}
		trace("connecting to "+targetID);
		try {
			connection.connect();
		} catch (IOException e) {
			throw new ContainerConnectException("IRC connect exception",e);
		}
		this.targetID = tID;
		fireContainerEvent(new ContainerConnectedEvent(this
				.getID(), targetID));
	}
	protected void handleUnknown(String arg0, String arg1, String arg2, String arg3) {
		trace("handleUnknown("+arg0+","+arg1+","+arg2+","+arg3+")");
		showMessage(null,"UNKNOWN MESSAGE: "+arg0+","+arg1+","+arg2+","+arg3);
	}
	protected void handleOnTopic(String arg0, IRCUser arg1, String arg2) {
		trace("handleOnTopic("+arg0+","+arg1+","+arg2+")");
		showMessage(arg0, arg1.getNick() + " has changed the topic to: " + arg2);
	}
	protected String [] parseUsers(String usergroup) {
		if (usergroup == null) return null;
		StringTokenizer t = new StringTokenizer(usergroup,COMMAND_DELIM);
		int tok = t.countTokens();
		String [] res = new String[tok];
		for(int i=0; i < tok; i++) res[i] = t.nextToken();
		return res;
	}
	protected void handleOnReply(int arg0, String arg1, String arg2) {
		trace("handleOnReply("+arg0+"|"+arg1+"|"+arg2+")");
		replyHandler.handleReply(arg0,arg1,arg2);
	}
	
	protected String concat(String [] args, int start, String suffix) {
		StringBuffer result = new StringBuffer("");
		for(int i=start; i < args.length; i++) {
			result.append(args[i]).append(" ");
		}
		result.append(suffix);
		return result.toString();
	}
	protected class ReplyHandler {
		public void handleReply(int code, String arg1, String arg2) {
			String [] users = parseUsers(arg1);
			switch (code) {
			case 353:
				firePresenceListeners(true,parseUserNames(arg2));
				break;
			case 311:
				showMessage(null,"whois "+users[1]);
				showMessage(null,trimUsername(users[2])+"@"+users[3]);
				break;
			case 312:
				showMessage(null,"server: "+users[2]+" - "+arg2);
				break;
			case 317:
				showMessage(null,users[2]+" seconds idle");
				break;
			case 318:
				showMessage(null,"whois end");
				break;
			case 319:
				showMessage(null,"channels: "+arg2);
				break;
			case 320:
				break;
			default:
				// first user always expected to be us
				if (users.length < 2) showMessage(null,arg2);
				else {
					showMessage(users[1],concat(users,2,arg2));
				}
			}
		}
		private String trimUsername(String un) {
			int eq = un.indexOf('=');
			return un.substring(eq+1);
		}
	}
	private IPresence createPresence(final boolean available) {
		return new IPresence() {
			private static final long serialVersionUID = 1L;
			public Mode getMode() {
				return (available?IPresence.Mode.AVAILABLE:IPresence.Mode.AWAY);
			}
			public int getPriority() {
				return 0;
			}
			public Map getProperties() {
				return null;
			}
			public String getStatus() {
				return "";
			}
			public Type getType() {
				return (available?IPresence.Type.AVAILABLE:IPresence.Type.UNAVAILABLE);
			}
			public Object getAdapter(Class adapter) {
				return null;
			}
			public byte[] getPictureData() {
				return new byte[0];
			}
			
		};
	}
	
	private String [] removeOperators(String [] strings) {
		List results = new ArrayList();
		for (int i=0; i < strings.length; i++) {
			if (!strings[i].startsWith(OPERATOR_PREFIX)) results.add(strings[i]);
		}
		return (String []) results.toArray(new String [] {});
	}
	private void firePresenceListeners(boolean joined, String[] strings) {
		String [] users = removeOperators(strings);
		for(Iterator i=participantListeners.iterator(); i.hasNext(); ) {
			IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();
			for(int j=0; j < users.length; j++) {
				ID fromID = createIDFromString(users[j]);
				ID localID = (ircUser != null)?createIDFromString(ircUser.getNick()):null;
				if (joined) {
					if (!fromID.equals(localID)) {
						l.handlePresence(fromID,createPresence(joined));
						l.handleArrivedInChat(fromID);
					}
				} else {
					l.handlePresence(fromID,createPresence(joined));
					l.handleDepartedFromChat(fromID);
				}
			}
		}
	}
	private void joinLocalUser() {
		for(Iterator i=participantListeners.iterator(); i.hasNext(); ) {
			IChatRoomParticipantListener l = (IChatRoomParticipantListener) i.next();
			ID fromID = createIDFromString(ircUser.getNick());
			l.handlePresence(fromID,createPresence(true));
			l.handleArrivedInChat(fromID);
		}
	}
	private void firePresenceListeners(boolean joined, String name) {
		firePresenceListeners(joined,new String [] { name });
	}
	private String [] parseUserNames(String list) {
		StringTokenizer st = new StringTokenizer(list,COMMAND_DELIM);
		int tokens = st.countTokens();
		String [] res = new String[tokens];
		for(int i=0; i < tokens; i++) {
			res[i] = st.nextToken();
		}
		return res;
	}
	private void showMessage(String channel, String msg) {
		IRCContainer container = getChannel(channel);
		if (container == null) {
			// system message...present as such
			fireMessageListeners(getSystemID(),msg);
		} else if (container.equals(this)) {
			fireMessageListeners(createIDFromString(channel),msg);
		} else {
			trace("showMessage has no container for channel "+channel+": "+msg);
		}
	}
	private void showMessage(String channel, String user, String msg) {
		fireMessageListeners(createIDFromString(user),msg);
	}
	private ID getSystemID() {
		if (targetID == null) return unknownID;
		try {
			return IDFactory.getDefault().createStringID(targetID.getHost());
		} catch (IDCreateException e) {
			Activator.log("ID creation exception in IRCContainer.getSystemID()",e);
			return unknownID;
		}
	}
	private ID createIDFromString(String str) {
		try {
			return IDFactory.getDefault().createStringID(str);
		} catch (IDCreateException e) {
			Activator.log("ID creation exception in IRCContainer.getIDForString()",e);
			return unknownID;
		} 
	}
	private void fireMessageListeners(ID sender, String msg) {
		for(Iterator i=msgListeners.iterator(); i.hasNext(); ) {
			IMessageListener l = (IMessageListener) i.next();
			l.handleMessage(sender, null, IMessageListener.Type.GROUP_CHAT, "", msg);
		}
	}
	protected void handleOnQuit(IRCUser arg0, String arg1) {
		trace("handleOnQuit("+arg0+","+arg1+")");
		firePresenceListeners(false, getIRCUserName(arg0));
	}
	protected void handleOnPrivmsg(String arg0, IRCUser arg1, String arg2) {
		trace("handleOnPrivmsg("+arg0+","+arg1+","+arg2+")");
		showMessage(arg0,arg1.toString(),arg2);
	}
	protected void handleOnPing(String arg0) {
		trace("handleOnPing("+arg0+")");
		synchronized (this) {
			if (connection != null) {
				connection.doPong(arg0);
			}
		}
	}
	protected void handleOnPart(String arg0, IRCUser arg1, String arg2) {
		trace("handleOnPart("+arg0+","+arg1+","+arg2+")");
		firePresenceListeners(false, getIRCUserName(arg1));
	}
	protected void handleOnNotice(String arg0, IRCUser arg1, String arg2) {
		trace("handleOnNotice("+arg0+","+arg1+","+arg2+")");
		showMessage(arg0,arg2);
	}
	protected void handleOnNick(IRCUser arg0, String arg1) {
		trace("handleOnNick("+arg0+","+arg1+")");
	}
	protected void handleOnMode(IRCUser arg0, String arg1, String arg2) {
		trace("handleOnMode("+arg0+","+arg1+","+arg2+")");
	}
	protected void handleOnMode(String arg0, IRCUser arg1, IRCModeParser arg2) {
		trace("handleOnMode("+arg0+","+arg1+","+arg2+")");
	}
	protected void handleOnKick(String arg0, IRCUser arg1, String arg2, String arg3) {
		trace("handleOnKick("+arg0+","+arg1+","+arg2+","+arg3+")");
		firePresenceListeners(false, getIRCUserName(arg1));
	}
	protected String getIRCUserName(IRCUser user) {
		if (user == null) return null;
		else return user.toString();
	}
	protected void isJoined(String channel, IRCUser user) {
		if (joinedChannel == null) {
			joinedChannel = channel;
			ircUser = user;
			joinLocalUser();
		} else {
			firePresenceListeners(true, getIRCUserName(user) );
		}
	}
	protected void isLeft() {
		joinedChannel = null;
	    firePresenceListeners(false, getIRCUserName(ircUser));
	    ircUser = null;
	}
	protected void handleOnJoin(String arg0, IRCUser arg1) {
		trace("handleOnJoin("+arg0+","+arg1+")");
		isJoined(arg0,arg1);
	}
	protected void handleOnInvite(String arg0, IRCUser arg1, String arg2) {
		trace("handleOnInvite("+arg0+","+arg1+","+arg2+")");
	}
	protected void handleOnError(int arg0, String arg1) {
		trace("handleOnError("+arg0+","+arg1+")");
		showMessage(null,"ERROR: "+arg0+","+arg1);
		disconnect();
	}
	protected void handleOnError(String arg0) {
		trace("handleOnError("+arg0+")");
		showMessage(null,"ERROR: "+arg0);
		disconnect();
	}
	protected void handleOnDisconnected() {
		trace("handleOnDisconnected()");
		showMessage(null,"Disconnected");
		isLeft();
		disconnect();
	}
	protected void handleOnRegistered() {
		trace("handleOnRegistered()");
		if (startchannel) {
			IChatRoomContainer container = getChannel(startchannelname);
			if (container != null) {
				// we've got a container, now join it
				// since this is us we don't join it with a call to our connect method, but rather directly with the connetion
				synchronized (this) {
					if (connection != null) {
						trace("Joining channel "+startchannelname);
						connection.doJoin(startchannelname);
						startchannel = false;
					}
				}
			}
		}
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainer#getConnectedID()
	 */
	public ID getConnectedID() {
		return targetID;
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainer#getConnectNamespace()
	 */
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(Activator.NAMESPACE_IDENTIFIER);
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainer#disconnect()
	 */
	public void disconnect() {
		if (connection != null) {
			connection.close();
			connection = null;
		}
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainer#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class serviceType) {
		if (serviceType != null) {
			if (serviceType.equals(IChatRoomManager.class)) {
				return this;
			}
		}
		return null;
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IContainer#dispose()
	 */
	public void dispose() {
		fireContainerEvent(new ContainerDisposeEvent(getID()));
		disconnect();
	}
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.IIdentifiable#getID()
	 */
	public ID getID() {
		return localID;
	}
	// Impl of IChatRoomManager
	public IChatRoomManager getParent() {
		return null;
	}
	public IChatRoomManager[] getChildren() {
		return new IChatRoomManager[0];
	}
	protected ID getRoomIDFromName(String roomname) {
		try {
			return IDFactory.getDefault().createStringID(roomname);
		} catch (IDCreateException e) {
			return null;
		}
	}
	public IChatRoomInfo getChatRoomInfo(final String roomname) {
		return new IChatRoomInfo() {
			public String getDescription() {
				return "Channel "+joinedChannel;
			}
			public String getSubject() {
				return joinedChannel;
			}
			public ID getRoomID() {
				return getRoomIDFromName(roomname);
			}
			public int getParticipantsCount() {
				return 0;
			}
			public String getName() {
				return roomname;
			}
			public boolean isPersistent() {
				return false;
			}
			public boolean requiresPassword() {
				return false;
			}
			public boolean isModerated() {
				return false;
			}
			public ID getConnectedID() {
				return targetID;
			}
			public Object getAdapter(Class clazz) {
				return null;
			}
			public IChatRoomContainer createChatRoomContainer() throws ContainerCreateException {
				return IRCContainer.this;
			}
		};
	}
	public IChatRoomInfo[] getChatRoomsInfo() {
		return null;
	}
	// IChatRoomContainer
	public void addMessageListener(IMessageListener msgListener) {
		msgListeners.add(msgListener);
	}
	public IChatRoomMessageSender getChatMessageSender() {
		return new IChatRoomMessageSender() {
			public void sendMessage(String message) throws ECFException {
				parseMessageAndSend(message);
			}
		};
	}
	
	protected void parseMessageAndSend(String message) {
		if (isCommand(message)) {
			String [] tokens = parseCommandTokens(message);
			synchronized (this) {
				if (connection != null) {
					handleCommandMessage(tokens);
				} else {
					trace("parseMessageAndSend("+message+") Not connected for IRCContainer "+getID());
				}
			}
		} else {
			synchronized (this) {
				if (connection != null) {
					if (ircUser != null) {
						connection.doPrivmsg(joinedChannel, message);
						showMessage(null,ircUser.toString(),message);
					} else {
						trace("irc user is null.  Not connected to channel");
					}
				} else {
					trace("connection is null.  Cannot send message");
				}
			}
		}
	}
	private synchronized void handleCommandMessage(String[] tokens) {
		// Look at first one and switch
		String command = tokens[0];
		while (command.startsWith(COMMAND_PREFIX)) command = command.substring(1);
		String [] args = new String[tokens.length-1];
		System.arraycopy(tokens, 1, args, 0, tokens.length-1);
		if (command.equalsIgnoreCase(JOIN_COMMAND)) {
			if (args.length > 1) {
				connection.doJoin(args[0],args[1]);
			} else if (args.length > 0) {
				connection.doJoin(args[0]);
			}
		} else if (command.equalsIgnoreCase(LIST_COMMAND)) {
			if (args.length > 0) {
				connection.doList(args[0]);
			} else connection.doList();
		} else if (command.equalsIgnoreCase(PART_COMMAND)) {
			if (args.length > 1) {
				connection.doPart(args[0],args[1]);
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
				connection.doInvite(args[0],args[1]);
			}
		} else {
			trace("Unrecognized command '"+command+"' in IRCContainer "+getID());
		}
	}
	private String[] parseCommandTokens(String message) {
		StringTokenizer st = new StringTokenizer(message,COMMAND_DELIM);
		int countTokens = st.countTokens();
		String toks [] = new String[countTokens];
		for(int i=0; i < countTokens; i++) {
			toks[i] = st.nextToken();
		}
		return toks;
	}
	private boolean isCommand(String message) {
		return (message != null && message.startsWith(COMMAND_PREFIX));
	}
	public void addChatParticipantListener(IChatRoomParticipantListener participantListener) {
		participantListeners.add(participantListener);
	}
	public void removeChatParticipantListener(
			IChatRoomParticipantListener participantListener) {
		participantListeners.remove(participantListener);
		
	}
	public void removeMessageListener(IMessageListener msgListener) {
		// TODO Auto-generated method stub
		
	}
	public void addListener(IContainerListener l) {
		synchronized (listeners) {
			listeners.add(l);
		}
	}
	public void removeListener(IContainerListener l) {
		synchronized (listeners) {
			listeners.remove(l);
		}
	}
	public void addInvitationListener(IChatRoomInvitationListener listener) {
		// TODO Auto-generated method stub
	}
	public void removeInvitationListener(IChatRoomInvitationListener listener) {
		// TODO Auto-generated method stub
	}
}