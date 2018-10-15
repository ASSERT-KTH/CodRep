public static String unfixEscapeInNode(String node) {

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
import java.util.Hashtable;
import java.util.Iterator;

import org.eclipse.ecf.core.identity.BaseID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.internal.provider.xmpp.Messages;
import org.eclipse.ecf.presence.IFQID;
import org.eclipse.ecf.presence.im.IChatID;

public class XMPPID extends BaseID implements IChatID, IFQID {

	private static final long serialVersionUID = 3257289140701049140L;
	public static final char USER_HOST_DELIMITER = '@';
	public static final char PORT_DELIMITER = ':';
	public static final String PATH_DELIMITER = "/";

	static class XMPPEscape {
		StringBuffer buf = new StringBuffer();

		public XMPPEscape(char[] chars) {
			if (chars != null) {
				for (int i = 0; i < chars.length; i++) {
					buf.append(chars[i]);
				}
			}
		}

		public CharSequence getAsCharSequence() {
			return buf;
		}

	}

	protected static Hashtable escapeTable;

	static {
		escapeTable = new Hashtable(10);
		escapeTable.put("@", new XMPPEscape(new char[] {'\\', '4', '0'}));
		escapeTable.put("\"", new XMPPEscape(new char[] {'\\', '2', '2'}));
		escapeTable.put("&", new XMPPEscape(new char[] {'\\', '2', '6'}));
		escapeTable.put("'", new XMPPEscape(new char[] {'\\', '2', '7'}));
		escapeTable.put("/", new XMPPEscape(new char[] {'\\', '2', 'f'}));
		escapeTable.put(":", new XMPPEscape(new char[] {'\\', '3', 'a'}));
		escapeTable.put("<", new XMPPEscape(new char[] {'\\', '3', 'c'}));
		escapeTable.put(">", new XMPPEscape(new char[] {'\\', '3', 'e'}));
		escapeTable.put("\\", new XMPPEscape(new char[] {'\\', '5', 'c'}));
	}

	// implements JEP-0106 JID escaping: http://www.xmpp.org/extensions/xep-0106.html
	static String fixEscapeInNode(String node) {
		if (node == null)
			return null;
		for (final Iterator i = escapeTable.keySet().iterator(); i.hasNext();) {
			final String key = (String) i.next();
			final XMPPEscape escape = (XMPPEscape) escapeTable.get(key);
			node = node.replace(new StringBuffer(key), escape.getAsCharSequence());
		}
		return node;
	}

	static String fixPercentEscape(String src) {
		if (src == null)
			return null;
		return src.replaceAll("%", "%25");
	}

	static String unfixEscapeInNode(String node) {
		if (node == null)
			return null;
		for (final Iterator i = escapeTable.keySet().iterator(); i.hasNext();) {
			final String key = (String) i.next();
			final XMPPEscape escape = (XMPPEscape) escapeTable.get(key);
			node = node.replace(escape.getAsCharSequence(), new StringBuffer(key));
		}
		return node;
	}

	URI uri;
	String username;
	String hostname;
	String resourcename;
	int port = -1;

	public XMPPID(Namespace namespace, String unamehost) throws URISyntaxException {
		super(namespace);
		unamehost = fixPercentEscape(unamehost);
		if (unamehost == null)
			throw new URISyntaxException(unamehost, Messages.XMPPID_EXCEPTION_XMPPID_USERNAME_NOT_NULL);
		// Handle parsing of user@host/resource string
		int atIndex = unamehost.lastIndexOf(USER_HOST_DELIMITER);
		if (atIndex == -1)
			throw new URISyntaxException(unamehost, Messages.XMPPID_EXCEPTION_HOST_PORT_NOT_VALID);
		username = fixEscapeInNode(unamehost.substring(0, atIndex));
		final String remainder = unamehost.substring(atIndex + 1);
		// Handle parsing of host:port
		atIndex = remainder.lastIndexOf(PORT_DELIMITER);
		if (atIndex != -1) {
			try {
				final int slashLoc = remainder.indexOf(PATH_DELIMITER);
				if (slashLoc != -1)
					port = Integer.parseInt(remainder.substring(atIndex + 1, slashLoc));
				else
					port = Integer.parseInt(remainder.substring(atIndex + 1));
			} catch (final NumberFormatException e) {
				throw new URISyntaxException(unamehost, Messages.XMPPID_EXCEPTION_INVALID_PORT);
			}
			hostname = remainder.substring(0, atIndex);
		}
		atIndex = remainder.indexOf(PATH_DELIMITER);
		if (atIndex != -1) {
			if (hostname == null)
				hostname = remainder.substring(0, atIndex);
			resourcename = PATH_DELIMITER + remainder.substring(atIndex + 1);
		} else {
			resourcename = PATH_DELIMITER + "";
		}
		if (hostname == null)
			hostname = remainder;
		uri = new URI(namespace.getScheme(), username, hostname, port, resourcename, null, null);
	}

	protected int namespaceCompareTo(BaseID o) {
		return getName().compareTo(o.getName());
	}

	protected boolean namespaceEquals(BaseID o) {
		if (!(o instanceof XMPPID)) {
			return false;
		}
		final XMPPID other = (XMPPID) o;
		return getUsernameAtHost().equals(other.getUsernameAtHost());
	}

	protected String namespaceGetName() {
		return getUsernameAtHost();
	}

	protected int namespaceHashCode() {
		return getUsernameAtHost().hashCode();
	}

	public String getNodename() {
		return username;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.core.identity.BaseID#namespaceToExternalForm()
	 */
	protected String namespaceToExternalForm() {
		return uri.toASCIIString();
	}

	public String getUsername() {
		return unfixEscapeInNode(username);
	}

	public String getHostname() {
		return hostname;
	}

	public String getResourceName() {
		return resourcename;
	}

	public void setResourceName(String resourceName) {
		this.resourcename = resourceName;
	}

	public int getPort() {
		return port;
	}

	public String getUsernameAtHost() {
		return getUsername() + USER_HOST_DELIMITER + getHostname() + ((getPort() == -1) ? "" : ":" + getPort());
	}

	public String getFQName() {
		return getUsernameAtHost() + getResourceName();
	}

	public String toString() {
		final StringBuffer sb = new StringBuffer("XMPPID["); //$NON-NLS-1$
		sb.append(uri.toString()).append("]");
		return sb.toString();
	}

	public Object getAdapter(Class clazz) {
		if (clazz.isInstance(this)) {
			return this;
		} else
			return super.getAdapter(clazz);
	}
}