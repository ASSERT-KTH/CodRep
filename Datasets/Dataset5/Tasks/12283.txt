public RosterEntry(Object parent, IUser user,

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

package org.eclipse.ecf.presence.roster;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.user.IUser;

/**
 * Roster entry base class implementing {@link IRosterEntry}. Subclasses may be
 * created as appropriate
 * 
 */
public class RosterEntry extends RosterItem implements IRosterEntry {

	protected IUser user;
	
	protected IPresence presence;

	protected List groups;

	public RosterEntry(IRosterItem parent, IUser user,
			IPresence presenceState) {
		Assert.isNotNull(parent);
		Assert.isNotNull(user);
		this.parent = parent;
		this.name = user.getName();
		this.user = user;
		this.presence = presenceState;
		this.groups = Collections.synchronizedList(new ArrayList());
		if (parent instanceof RosterGroup) {
			groups.add(parent);
			((RosterGroup) parent).add(this);
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.roster.IRosterEntry#add(org.eclipse.ecf.presence.roster.IRosterGroup)
	 */
	public boolean add(IRosterGroup group) {
		if (group == null) return false;
		return groups.add(group);
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.roster.IRosterEntry#remove(org.eclipse.ecf.presence.roster.IRosterGroup)
	 */
	public boolean remove(IRosterGroup group) {
		if (group == null) return false;
		return groups.remove(group);
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.roster.IRosterEntry#getUser()
	 */
	public IUser getUser() {
		return user;
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.ui.presence.IRosterEntry#getGroups()
	 */
	public Collection getGroups() {
		return groups;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.ui.presence.IRosterEntry#getPresenceState()
	 */
	public IPresence getPresence() {
		return presence;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	public String toString() {
		StringBuffer sb = new StringBuffer("RosterEntry["); //$NON-NLS-1$
		synchronized (sb) {
			sb.append("name=").append(name).append(';'); //$NON-NLS-1$
			sb.append("presence=").append(presence).append(';'); //$NON-NLS-1$
			sb.append("groups="); //$NON-NLS-1$
			if (!groups.isEmpty()) {
				for (int i = 0; i < groups.size(); i++) {
					sb.append(((IRosterGroup) groups.get(i)).getName());
					if (i < (groups.size()-1)) sb.append(',');
				}
			}
			sb.append(']');
		}
		return sb.toString();
	}

}