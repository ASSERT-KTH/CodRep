// ignored since this is not possible

/****************************************************************************
 * Copyright (c) 2006, 2007 Remy Suen, Composent Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.internal.provider.msn;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.protocol.msn.Contact;
import org.eclipse.ecf.protocol.msn.Status;

final class MSNRosterEntry implements IPresence, IRosterEntry, IUser {

	private static final long serialVersionUID = 5358415024505371809L;

	private Collection groups;

	private IRosterItem parent;

	private final Contact contact;

	private MSNID id;

	private IRoster roster;

	private Map properties;

	MSNRosterEntry(IRoster roster, Contact contact, Namespace namespace) {
		this.roster = roster;
		this.contact = contact;
		groups = Collections.EMPTY_LIST;
		properties = new HashMap(1);
		try {
			id = (MSNID) namespace.createInstance(new Object[] { contact
					.getEmail() });
		} catch (IDCreateException e) {
			e.printStackTrace();
		}
	}

	void updatePersonalMessage() {
		String message = contact.getPersonalMessage();
		if (message.equals("")) { //$NON-NLS-1$
			properties.remove(Messages.MSNRosterEntry_Message);
		} else {
			properties.put(Messages.MSNRosterEntry_Message, message);
		}
	}

	Contact getContact() {
		return contact;
	}

	public String getName() {
		return contact.getDisplayName();
	}

	public Mode getMode() {
		Status status = contact.getStatus();
		if (status == Status.ONLINE) {
			return Mode.AVAILABLE;
		} else if (status == Status.BUSY) {
			return Mode.DND;
		} else if (status == Status.APPEAR_OFFLINE) {
			return Mode.INVISIBLE;
		} else {
			return Mode.AWAY;
		}
	}

	public Map getProperties() {
		return properties;
	}

	public String getStatus() {
		return contact.getPersonalMessage();
	}

	public Type getType() {
		return contact.getStatus() == Status.OFFLINE ? Type.UNAVAILABLE
				: Type.AVAILABLE;
	}

	public Object getAdapter(Class adapter) {
		if (adapter != null && adapter.isInstance(this)) {
			return this;
		} else {
			return null;
		}
	}

	public Collection getGroups() {
		return groups;
	}

	public IPresence getPresence() {
		return this;
	}

	public IUser getUser() {
		return this;
	}

	void setParent(IRosterItem parent) {
		this.parent = parent;
		if (parent instanceof IRoster) {
			groups = Collections.EMPTY_LIST;
		} else {
			ArrayList list = new ArrayList(1);
			list.add(parent);
			groups = Collections.unmodifiableCollection(list);
		}
	}

	public IRosterItem getParent() {
		return parent;
	}

	public byte[] getPictureData() {
		// TODO: update this when avatars have been implemented
		return null;
	}

	public ID getID() {
		return id;
	}

	public String getNickname() {
		return contact.getDisplayName();
	}

	public IRoster getRoster() {
		return roster;
	}

}