package org.eclipse.ecf.internal.provider.xmpp.identity;

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
package org.eclipse.ecf.provider.xmpp.identity;

import java.net.URI;
import java.net.URISyntaxException;
import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.presence.im.IChatID;
import org.jivesoftware.smack.XMPPConnection;

public class XMPPRoomID extends BaseID implements IChatID {
	
	private static final long serialVersionUID = -4843967090539640622L;
	public static final String DOMAIN_DEFAULT = "conference";
	public static final String NICKNAME = "nickname";
	
	URI uri = null;
	String longName = null;
	
	protected String fixHostname(String host, String domain) {
		if (domain == null) domain = DOMAIN_DEFAULT;
		return domain+"."+host;
	}
	
	protected String fixUsername(String connUsername) {
		int atIndex = connUsername.indexOf('@');
		if (atIndex == -1) return connUsername;
		else return connUsername.substring(0,atIndex);
	}
	protected String[] getRoomAndHost(String roomatconfhost) {
		int atIndex = roomatconfhost.indexOf('@');
		if (atIndex == -1) return new String[] { "", ""};
		String room = roomatconfhost.substring(0,atIndex);
		String fullHost = roomatconfhost.substring(atIndex+1);
		int dotIndex = fullHost.indexOf('.');
		String domain = fullHost.substring(0,dotIndex);
		String host = fullHost.substring(dotIndex+1);
		return new String [] { room, host, domain };
	}
	public XMPPRoomID(Namespace namespace, String username, String host, String domain, String groupname, String nickname) throws URISyntaxException {
		super(namespace);
		String hostname = fixHostname(host,domain);
		String query = NICKNAME+"="+((nickname==null)?username:nickname);
		uri = new URI(namespace.getScheme(),username,hostname,-1,"/"+groupname,query,null);
	}
	public XMPPRoomID(Namespace namespace, XMPPID userid, String domain, String groupname, String nickname) throws URISyntaxException {
		this(namespace,userid.getUsername(),userid.getHostname(),domain,groupname,nickname);
	}
	public XMPPRoomID(Namespace namespace, XMPPConnection conn, String roomid, String longName) throws URISyntaxException {
		super(namespace);
		String username = fixUsername(conn.getUser());
		String [] roomandhost = getRoomAndHost(roomid);
		String room = roomandhost[0];
		String hostname = fixHostname(roomandhost[1],roomandhost[2]);
		String query = NICKNAME+"="+username;
		this.uri = new URI(namespace.getScheme(),username,hostname,-1,"/"+room,query,null);
		this.longName = longName;
	}
	public XMPPRoomID(Namespace namespace, XMPPConnection conn, String roomid) throws URISyntaxException {
		this(namespace,conn,roomid,null);
	}
	protected int namespaceCompareTo(BaseID o) {
        return getName().compareTo(o.getName());
	}
	protected boolean namespaceEquals(BaseID o) {
		if (!(o instanceof XMPPRoomID)) {
			return false;
		}
		XMPPRoomID other = (XMPPRoomID) o;
		return uri.equals(other.uri);
	}
	protected String fixPath(String path) {
		while (path.startsWith("/")) {
			path = path.substring(1);
		}
		return path;
	}
	protected String namespaceGetName() {
		String path = uri.getPath();
		return fixPath(path);
	}
	protected int namespaceHashCode() {
		return uri.hashCode();
	}
	public String getMucString() {
		String host = uri.getHost();
		String group = fixPath(uri.getPath());
		String res = group + "@" + host;
		return res;
	}
	public String getNickname() {
		String query = uri.getQuery();
		if (query == null) {
			return uri.getUserInfo();
		} else {
			return query.substring(query.indexOf('=')+1);
		}
	}
	public String getLongName() {
		return longName;
	}
	public String toString() {
		StringBuffer sb = new StringBuffer("XMPPRoomID[");
		sb.append(uri).append("]");
		return sb.toString();
	}
	public Object getAdapter(Class clazz) {
	    if (clazz.isInstance(this)) {
	    	return this;
	    } else return super.getAdapter(clazz);
	}

	public String getUsername() {
		return getNickname();
	}
}