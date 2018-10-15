package org.eclipse.ecf.provider.xmpp.identity;

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
package org.eclipse.ecf.internal.provider.xmpp.identity;

import java.net.URISyntaxException;

import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.presence.im.IChatID;
import org.jivesoftware.smack.XMPPConnection;

public class XMPPRoomID extends BaseID implements IChatID {

	private static final long serialVersionUID = -4843967090539640622L;
	public static final String DOMAIN_DEFAULT = "conference";
	public static final String NICKNAME = "nickname";
	public static final String AT_SIGN = "@";
	public static final String DOT = ".";
	public static final String SLASH = "/";
	public static final char DOT_CHAR = DOT.charAt(0);
	
	String domain;
	String host;
	String username;
	String roomname;
	String nickname = "";
	String longName;

	public static String fixConferenceDomain(String domain, String host) {
		if (domain == null)
			domain = DOMAIN_DEFAULT;
		return domain + DOT + host;
	}

	public XMPPRoomID(Namespace namespace, String username, String host,
			String domain, String roomname, String nickname)
			throws URISyntaxException {
		super(namespace);
		this.domain = domain;
		this.host = host;
		this.username = username;
		this.roomname = roomname;
		this.nickname = ((nickname == null) ? username : nickname);
	}

	public XMPPRoomID(Namespace namespace, XMPPID userid, String domain,
			String groupname, String nickname) throws URISyntaxException {
		this(namespace, userid.getUsername(), userid.getHostname(), domain,
				groupname, nickname);
	}

	public XMPPRoomID(Namespace namespace, XMPPConnection conn, String roomid,
			String longName) throws URISyntaxException {
		super(namespace);
		String connUsername = conn.getUser();
		int atIndex = connUsername.indexOf(AT_SIGN);
		this.username = (atIndex == -1)?connUsername:connUsername.substring(0, atIndex);
		atIndex = roomid.indexOf(AT_SIGN);
		if (atIndex == -1) {
			this.roomname = roomid;
			this.host = conn.getHost();
			this.domain = DOMAIN_DEFAULT;
		} else {
			this.roomname = roomid.substring(0, atIndex);
			String fullHost = roomid.substring(atIndex + 1);
			int dotIndex = fullHost.indexOf(DOT_CHAR);
			this.domain = fullHost.substring(0, dotIndex);
			this.host = fullHost.substring(dotIndex + 1);
		}
		this.nickname = this.username;
		this.longName = (longName==null)?this.roomname+AT_SIGN+this.domain+DOT+this.host:longName;
	}

	public XMPPRoomID(Namespace namespace, XMPPConnection conn, String roomid)
			throws URISyntaxException {
		this(namespace, conn, roomid, null);
	}

	protected int namespaceCompareTo(BaseID o) {
		return getName().compareTo(o.getName());
	}

	protected boolean fieldEquals(XMPPRoomID o) {
		return (this.domain.equals(o.domain) && (this.host.equals(o.host))
				&& (this.nickname.equals(o.nickname))
				&& (this.roomname.equals(o.roomname)) && (this.username
				.equals(o.username)));
	}

	protected boolean namespaceEquals(BaseID o) {
		if (!(o instanceof XMPPRoomID)) {
			return false;
		}
		XMPPRoomID other = (XMPPRoomID) o;
		return fieldEquals(other);
	}

	protected String fixPath(String path) {
		while (path.startsWith(SLASH)) {
			path = path.substring(1);
		}
		return path;
	}

	protected String namespaceGetName() {
		return this.roomname;
	}

	protected int namespaceHashCode() {
		return this.domain.hashCode() ^ this.host.hashCode()
				^ this.nickname.hashCode() ^ this.roomname.hashCode()
				^ this.username.hashCode();
	}

	public String getMucString() {
		return this.roomname + AT_SIGN + this.domain + DOT + this.host;
	}

	public String getNickname() {
		return nickname;
	}

	public String getLongName() {
		return longName;
	}
	
	public String toString() {
		StringBuffer sb = new StringBuffer("XMPPRoomID[");
		sb.append(
				getNamespace().getScheme() + "://" + getUsername() + AT_SIGN
						+ this.domain + DOT + this.host + SLASH + this.roomname)
				.append("]");
		return sb.toString();
	}

	public Object getAdapter(Class clazz) {
		if (clazz.isInstance(this)) {
			return this;
		} else
			return super.getAdapter(clazz);
	}

	public String getUsername() {
		return getNickname();
	}
	
	public String getHostname() {
		return this.host;
	}
}