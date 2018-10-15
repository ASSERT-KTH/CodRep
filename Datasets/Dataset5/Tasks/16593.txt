return IDFactory.getDefault().createID(namespace.getName(), new Object[] { connection

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.xmpp.smack;

import java.io.IOException;
import java.util.Map;
import org.eclipse.ecf.core.comm.DisconnectConnectionEvent;
import org.eclipse.ecf.core.comm.IAsynchConnectionEventHandler;
import org.eclipse.ecf.core.comm.IConnectionEventHandler;
import org.eclipse.ecf.core.comm.ISynchAsynchConnection;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.provider.xmpp.Trace;
import org.eclipse.ecf.provider.xmpp.container.IIMMessageSender;
import org.eclipse.ecf.provider.xmpp.identity.XMPPID;
import org.eclipse.ecf.provider.xmpp.identity.XMPPRoomID;
import org.jivesoftware.smack.Chat;
import org.jivesoftware.smack.ConnectionListener;
import org.jivesoftware.smack.GoogleTalkConnection;
import org.jivesoftware.smack.PacketListener;
import org.jivesoftware.smack.Roster;
import org.jivesoftware.smack.RosterEntry;
import org.jivesoftware.smack.SSLXMPPConnection;
import org.jivesoftware.smack.SmackConfiguration;
import org.jivesoftware.smack.XMPPConnection;
import org.jivesoftware.smack.XMPPException;
import org.jivesoftware.smack.packet.Message;
import org.jivesoftware.smack.packet.Packet;
import org.jivesoftware.smack.packet.Presence;

public class ECFConnection implements ISynchAsynchConnection, IIMMessageSender {

	public static final String CLIENT_TYPE = "ECF_XMPP";
	public static final Trace trace = Trace.create("smackconnection");
	public static final Trace smack = Trace.create("smackdebug");
	protected static final String STRING_ENCODING = "UTF-8";
	public static final String OBJECT_PROPERTY_NAME = ECFConnection.class
			.getName()
			+ ".object";
	protected static final int XMPP_NORMAL_PORT = 5222;
	protected XMPPConnection connection = null;
	protected IAsynchConnectionEventHandler handler = null;
	protected ID localID = null;
	protected boolean isStarted = false;
	protected String serverName;
	protected int serverPort = -1;
	protected Map properties = null;
	protected boolean isConnected = false;
	protected Namespace namespace = null;
	
	protected boolean google = false;
	
	protected boolean secure = false;
	
	protected void debug(String msg) {
		if (Trace.ON && trace != null) {
			trace.msg(msg);
		}
	}

	protected void dumpStack(String msg, Throwable t) {
		if (Trace.ON && trace != null) {
			trace.dumpStack(t, msg);
		}
	}

	protected void logException(String msg, Throwable t) {
		dumpStack(msg, t);
	}

	public Map getProperties() {
		return properties;
	}

	public Object getAdapter(Class clazz) {
		if (clazz.equals(IIMMessageSender.class)) {
			return this;
		}
		return null;
	}

	public XMPPConnection getXMPPConnection() {
		return connection;
	}
	public ECFConnection(boolean google, Namespace ns, IAsynchConnectionEventHandler h, boolean secure) {
		this.handler = h;
		this.namespace = ns;
		this.google = google;
		this.secure = secure;
		if (smack != null) {
			XMPPConnection.DEBUG_ENABLED = true;
		}
	}
	public ECFConnection(boolean google, Namespace ns, IAsynchConnectionEventHandler h) {
		this(google,ns,h,false);
	}
	protected String getPasswordForObject(Object data) {
		String password = null;
		try {
			password = (String) data;
		} catch (ClassCastException e) {
			return null;
		}
		return password;
	}
	
	protected XMPPID getXMPPID(ID remote) throws IOException {
		XMPPID jabberID = null;
		try {
			jabberID = (XMPPID) remote;
		} catch (ClassCastException e) {
			IOException throwMe = new IOException(e.getMessage());
			throwMe.setStackTrace(e.getStackTrace());
			throw throwMe;
		}
		return jabberID;
	}
	public synchronized Object connect(ID remote, Object data, int timeout)
			throws IOException {
		if (connection != null)
			throw new IOException("already connected");
		if (timeout > 0)
			SmackConfiguration.setPacketReplyTimeout(timeout);
		Roster.setDefaultSubscriptionMode(Roster.SUBSCRIPTION_MANUAL);
		
		XMPPID jabberURI = getXMPPID(remote);
		String username = jabberURI.getUsername();
		serverName = jabberURI.getHostname();
		try {
			if (google) {
				connection = new GoogleTalkConnection();
			} else if (serverPort == -1) {
				if (secure) {
					connection = new SSLXMPPConnection(serverName);
				} else {
					connection = new XMPPConnection(serverName);
				}
			} else {
				if (secure) {
					connection = new SSLXMPPConnection(serverName, serverPort);
				} else {
					connection = new XMPPConnection(serverName, serverPort);
				}
			}
			connection.addPacketListener(new PacketListener() {
				public void processPacket(Packet arg0) {
					handlePacket(arg0);
				}
			}, null);
			connection.addConnectionListener(new ConnectionListener() {
				public void connectionClosed() {
					handleConnectionClosed(null);
				}

				public void connectionClosedOnError(Exception e) {
					handleConnectionClosed(e);
				}
			});
			// Login
			connection.login(username, (String) data, CLIENT_TYPE);
			isConnected = true;
			debug("User: " + username + " logged into " + serverName);
		} catch (XMPPException e) {
			if (connection != null) {
				connection.close();
			}
			IOException result = new IOException(e.getMessage());
			result.setStackTrace(e.getStackTrace());
			throw result;
		}
		return null;
	}

	public synchronized void disconnect() throws IOException {
		debug("disconnect()");
		if (isStarted()) {
			stop();
		}
		if (connection != null) {
			connection.close();
			isConnected = false;
			connection = null;
		}
	}

	public synchronized boolean isConnected() {
		return (isConnected);
	}

	public synchronized ID getLocalID() {
		if (!isConnected())
			return null;
		try {
			return IDFactory.getDefault().makeID(namespace.getName(), new Object[] { connection
					.getConnectionID() });
		} catch (Exception e) {
			logException("Exception in getLocalID", e);
			return null;
		}
	}

	public synchronized void start() {
		if (isStarted())
			return;
		isStarted = true;
	}

	public boolean isStarted() {
		return isStarted;
	}

	public synchronized void stop() {
		isStarted = false;
	}

	protected void handleConnectionClosed(Exception e) {
		handler.handleDisconnectEvent(new DisconnectConnectionEvent(this, e,
				null));
	}

	protected void handlePacket(Packet arg0) {
		debug("handlePacket(" + arg0 + ")");
		try {
			Object val = arg0.getProperty(OBJECT_PROPERTY_NAME);
			if (val != null) {
				handler.handleAsynchEvent(new ECFConnectionObjectPacketEvent(
						this, arg0, val));
			} else {
				handler.handleAsynchEvent(new ECFConnectionPacketEvent(this,
						arg0));
			}
		} catch (IOException e) {
			logException("Exception in handleAsynchEvent", e);
			try {
				disconnect();
			} catch (Exception e1) {
				logException("Exception in disconnect()", e1);
			}
		}
	}

	public synchronized void sendAsynch(ID receiver, byte[] data)
			throws IOException {
		if (data == null)
			throw new IOException("no data");
		debug("sendAsynch(" + receiver + "," + data + ")");
		Message aMsg = new Message();
		aMsg.setProperty(OBJECT_PROPERTY_NAME, data);
		sendMessage(receiver,aMsg);
	}
	
	protected void sendMessage(ID receiver, Message aMsg) throws IOException {
		synchronized (this) {
			if (!isConnected())
				throw new IOException("not connected");
			try {
				if (receiver == null) throw new IOException(
							"receiver cannot be null for xmpp instant messaging");
				else if (receiver instanceof XMPPID) {
						XMPPID rcvr = (XMPPID) receiver;
						aMsg.setType(Message.Type.CHAT);
						String userAtHost = rcvr.getUsernameAtHost();
						Chat localChat = connection.createChat(userAtHost);
						localChat.sendMessage(aMsg);
					} else if (receiver instanceof XMPPRoomID) {
						XMPPRoomID roomID = (XMPPRoomID) receiver;
						aMsg.setType(Message.Type.GROUP_CHAT);
						String to = roomID.getMucString();
						aMsg.setTo(to);
						connection.sendPacket(aMsg);
					} else throw new IOException("receiver must be of type XMPPID or XMPPRoomID");
			} catch (XMPPException e) {
				IOException result = new IOException(
						"XMPPException in sendMessage: " + e.getMessage());
				result.setStackTrace(e.getStackTrace());
				throw result;
			}
		}
	}
	public synchronized Object sendSynch(ID receiver, byte[] data)
			throws IOException {
		if (data == null)
			throw new IOException("data cannot be null");
		// This is assumed to be disconnect...so we'll just disconnect
		// disconnect();
		return null;
	}

	public void addCommEventListener(IConnectionEventHandler listener) {
		// XXX Not yet implemented
	}

	public void removeCommEventListener(IConnectionEventHandler listener) {
		// XXX Not yet implemented
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.xmpp.IIMMessageSender#sendMessage(org.eclipse.ecf.core.identity.ID,
	 *      java.lang.String)
	 */
	public void sendMessage(ID target, String message) throws IOException {
		if (target == null)
			throw new IOException("target cannot be null");
		if (message == null)
			throw new IOException("message cannot be null");
		debug("sendMessage(" + target + "," + message + ")");
		Message aMsg = new Message();
		aMsg.setBody(message);
		sendMessage(target, aMsg);
	}

	public void sendPresenceUpdate(ID target, Presence presence) throws IOException {
		if (target == null)
			throw new IOException("target cannot be null");
		if (presence == null)
			throw new IOException("presence cannot be null");
		debug("sendPresenceUpdate(" + target + "," + presence + ")");
		presence.setFrom(connection.getUser());
		presence.setTo(target.getName());
		synchronized (this) {
			if (!isConnected())
				throw new IOException("not connected");
				connection.sendPacket(presence);
		}
	}
	
	public void sendRosterAdd(String user, String name, String [] groups) throws IOException {
		Roster r = getRoster();
		try {
			r.createEntry(user,name,groups);
		} catch (XMPPException e) {
			e.printStackTrace();
		}
	}
	public void sendRosterRemove(String user) throws IOException {
		Roster r = getRoster();
		RosterEntry re = r.getEntry(user);
		try {
			r.removeEntry(re);
		} catch (XMPPException e) {
			e.printStackTrace();
		}
	}
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.provider.xmpp.IIMMessageSender#getRoster()
	 */
	public Roster getRoster() throws IOException {
		if (connection == null)
			return null;
		if (!connection.isConnected())
			return null;
		Roster roster = connection.getRoster();
		return roster;
	}

}