new ChatRoomMessage(sender, targetID, msg)));

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

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.StringTokenizer;

import org.eclipse.ecf.core.AbstractContainer;
import org.eclipse.ecf.core.events.ContainerDisposeEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.provider.irc.Activator;
import org.eclipse.ecf.internal.provider.irc.IRCDebugOptions;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.chatroom.ChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.ChatRoomMessageEvent;
import org.eclipse.ecf.presence.chatroom.IChatRoomAdminListener;

public abstract class IRCAbstractContainer extends AbstractContainer {

	protected static final String ROOT_ROOMNAME = "/"; //$NON-NLS-1$
	protected static final String COMMAND_PREFIX = "/"; //$NON-NLS-1$
	protected static final String COMMAND_DELIM = " "; //$NON-NLS-1$
	protected static final String JOIN_COMMAND = "JOIN"; //$NON-NLS-1$
	protected static final String LIST_COMMAND = "LIST"; //$NON-NLS-1$
	protected static final String PART_COMMAND = "PART"; //$NON-NLS-1$
	protected static final String NICK_COMMAND = "NICK"; //$NON-NLS-1$
	protected static final String MSG_COMMAND = "MSG"; //$NON-NLS-1$
	protected static final String NOTICE_COMMAND = "NOTICE"; //$NON-NLS-1$
	protected static final String WHOIS_COMMAND = "WHOIS"; //$NON-NLS-1$
	protected static final String QUIT_COMMAND = "QUIT"; //$NON-NLS-1$
	protected static final String AWAY_COMMAND = "AWAY"; //$NON-NLS-1$
	protected static final String TOPIC_COMMAND = "TOPIC"; //$NON-NLS-1$
	protected static final String INVITE_COMMAND = "INVITE"; //$NON-NLS-1$
	protected static final String OPERATOR_PREFIX = "@"; //$NON-NLS-1$

	protected ID localID = null;
	protected ID targetID = null;
	protected List msgListeners = new ArrayList();
	protected ID unknownID = null;
	private ArrayList subjectListeners = new ArrayList();
	
	public IRCAbstractContainer() {
		super();
	}

	protected void trace(String msg) {
		Trace.trace(Activator.PLUGIN_ID, msg);
	}

	protected void traceStack(Throwable t, String msg) {
		Trace.catching(Activator.PLUGIN_ID, IRCDebugOptions.EXCEPTIONS_CATCHING, this.getClass(), msg, t);
	}

	public void fireMessageListeners(ID sender, String msg) {
		for (Iterator i = msgListeners.iterator(); i.hasNext();) {
			IIMMessageListener l = (IIMMessageListener) i.next();
			l.handleMessageEvent(new ChatRoomMessageEvent(sender,
					new ChatRoomMessage(sender, msg)));
		}
	}

	public ID getID() {
		return localID;
	}

	public ID getConnectedID() {
		return targetID;
	}

	protected String[] parseUsers(String usergroup) {
		if (usergroup == null)
			return null;
		StringTokenizer t = new StringTokenizer(usergroup, COMMAND_DELIM);
		int tok = t.countTokens();
		String[] res = new String[tok];
		for (int i = 0; i < tok; i++)
			res[i] = t.nextToken();
		return res;
	}

	protected String[] parseUserNames(String list) {
		StringTokenizer st = new StringTokenizer(list, COMMAND_DELIM);
		int tokens = st.countTokens();
		String[] res = new String[tokens];
		for (int i = 0; i < tokens; i++) {
			res[i] = st.nextToken();
		}
		return res;
	}

	protected String concat(String[] args, int start, String suffix) {
		StringBuffer result = new StringBuffer();
		for (int i = start; i < args.length; i++) {
			result.append(args[i]).append(' ');
		}
		result.append(suffix);
		return result.toString();
	}

	protected ID createIDFromString(String str) {
		if (str == null)
			return unknownID;
		try {
			return IDFactory.getDefault().createStringID(str);
		} catch (IDCreateException e) {
			Activator
					.log(
							"ID creation exception in IRCContainer.getIDForString()", //$NON-NLS-1$
							e);
			return unknownID;
		}
	}

	protected String trimOperator(String user) {
		if (user != null && user.startsWith(OPERATOR_PREFIX))
			return user.substring(OPERATOR_PREFIX.length());
		return user;
	}

	public abstract void disconnect();

	public void dispose() {
		fireContainerEvent(new ContainerDisposeEvent(getID()));
		disconnect();
	}

	protected String[] parseCommandTokens(String message) {
		StringTokenizer st = new StringTokenizer(message, COMMAND_DELIM);
		int countTokens = st.countTokens();
		String toks[] = new String[countTokens];
		for (int i = 0; i < countTokens; i++) {
			toks[i] = st.nextToken();
		}
		return toks;
	}

	protected boolean isCommand(String message) {
		return (message != null && message.startsWith(COMMAND_PREFIX));
	}

	public void addMessageListener(IIMMessageListener l) {
		msgListeners.add(l);
	}

	public void removeMessageListener(IIMMessageListener l) {
		msgListeners.remove(l);
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#addChatRoomSubjectListener(org.eclipse.ecf.presence.chatroom.IChatRoomAdminListener)
	 */
	public void addChatRoomAdminListener(
			IChatRoomAdminListener subjectListener) {
		subjectListeners.add(subjectListener);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.chatroom.IChatRoomContainer#removeChatRoomSubjectListener(org.eclipse.ecf.presence.chatroom.IChatRoomAdminListener)
	 */
	public void removeChatRoomAdminListener(
			IChatRoomAdminListener subjectListener) {
		subjectListeners.remove(subjectListener);
	}

	/**
	 * @param fromID
	 * @param arg2
	 */
	public void fireSubjectListeners(ID fromID, String newSubject) {
		for(Iterator i=subjectListeners.iterator(); i.hasNext(); ) {
			IChatRoomAdminListener l = (IChatRoomAdminListener) i.next();
			l.handleSubjectChange(fromID, newSubject);
		}
	}

}
 No newline at end of file