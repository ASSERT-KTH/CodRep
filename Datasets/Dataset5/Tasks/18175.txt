package org.eclipse.ecf.internal.ui.deprecated.views;

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
package org.eclipse.ecf.ui.views;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterGroup;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.jface.viewers.Viewer;

public class RosterViewContentProvider implements IStructuredContentProvider,
		ITreeContentProvider {
	/**
	 * 
	 */
	private final RosterView rosterView;

	/**
	 * @param rosterView
	 */
	RosterViewContentProvider(RosterView rosterView) {
		this.rosterView = rosterView;
	}

	private RosterParent invisibleRoot;

	private RosterParent root;

	public void inputChanged(Viewer v, Object oldInput, Object newInput) {
	}

	public void dispose() {
	}

	public RosterBuddy findBuddyWithUserID(ID userID) {
		return findBuddy(root, userID);
	}

	public Object[] getElements(Object parent) {
		if (parent.equals(this.rosterView.getViewSite())) {
			if (root == null) {
				root = new RosterParent("Buddy List");
				invisibleRoot = new RosterParent("");
				invisibleRoot.addChild(root);
			}
			return getChildren(root);
		}
		return getChildren(parent);
	}

	public Object getParent(Object child) {
		if (child instanceof RosterObject)
			return ((RosterObject) child).getParent();
		return null;
	}

	public Object[] getChildren(Object parent) {
		if (parent instanceof RosterParent)
			return ((RosterParent) parent).getChildren();
		return new Object[0];
	}

	public boolean hasChildren(Object parent) {
		if (parent instanceof RosterParent)
			return ((RosterParent) parent).hasChildren();
		return false;
	}

	public RosterBuddy fillPresence(RosterBuddy obj, IPresence presence) {
		obj.setPresence(presence);
		obj.removeChildren();
		obj.addChild(new RosterObject("User: " + obj.getID().getName()));
		obj
				.addChild(new RosterObject("Type: "
						+ presence.getType().toString()));
		String status = presence.getStatus();
		if (status != null && !status.equals(""))
			obj.addChild(new RosterObject("Status: " + status));
		Map props = presence.getProperties();
		for (Iterator i = props.keySet().iterator(); i.hasNext();) {
			String key = (String) i.next();
			String value = (String) props.get(key);
			if (key != null && value != null)
				obj.addChild(new RosterObject(key + ": " + value));
		}
		return obj;
	}

	public RosterBuddy createBuddy(ID svcID, RosterBuddy oldBuddy,
			IRosterEntry entry) {
		String name = entry.getName();
		if (name == null)
			name = this.rosterView.getUserNameFromID(entry.getUser().getID());
		name = name.replace('?','\'');
		IPresence presence = entry.getPresence();
		RosterBuddy newBuddy = null;
		if (oldBuddy == null)
			newBuddy = new RosterBuddy(svcID, name, entry.getUser().getID(),
					presence);
		else {
			newBuddy = oldBuddy;
			if (entry.getName() != null)
				newBuddy.setName(entry.getName());
		}
		if (presence != null)
			fillPresence(newBuddy, presence);
		return newBuddy;
	}

	public RosterGroup findGroup(RosterParent parent, String name) {
		if (parent == null)
			return null;
		RosterObject[] objs = parent.getChildren();
		if (objs != null) {
			for (int i = 0; i < objs.length; i++) {
				if (objs[i].getName().equals(name))
					return (RosterGroup) objs[i];
			}
		}
		return null;
	}

	public RosterGroup findGroup(RosterParent parent, ID id) {
		if (parent == null)
			return null;
		RosterObject[] objs = parent.getChildren();
		if (objs != null) {
			for (int i = 0; i < objs.length; i++) {
				ID idd = objs[i].getID();
				if (id.equals(idd))
					return (RosterGroup) objs[i];
			}
		}
		return null;
	}

	public String[] getAllGroupNamesForAccount(ID accountID) {
		RosterGroup accountRoot = findAccount(accountID);
		RosterObject[] objs = accountRoot.getChildren();
		if (objs != null) {
			List l = new ArrayList();
			for (int i = 0; i < objs.length; i++) {
				RosterObject o = objs[i];
				if (o instanceof RosterGroup) {
					l.add(((RosterGroup) o).getName());
				}
			}
			return (String[]) l.toArray(new String[] {});
		} else
			return new String[0];
	}

	public RosterBuddy findBuddy(RosterParent parent, IRosterEntry entry) {
		return findBuddy(parent, entry.getUser().getID());
	}

	public RosterBuddy findBuddy(RosterParent parent, ID entryID) {
		if (parent == null)
			return null;
		RosterObject[] objs = parent.getChildren();
		if (objs == null)
			return null;
		for (int i = 0; i < objs.length; i++) {
			if (objs[i] instanceof RosterBuddy) {
				RosterBuddy tb = (RosterBuddy) objs[i];
				ID tbid = tb.getID();
				if (tbid != null && tbid.equals(entryID)) {
					// Replace old ID with new ID
					RosterBuddy buddy = (RosterBuddy) objs[i];
					buddy.setID(entryID);
					return buddy;
				}
			} else if (objs[i] instanceof RosterGroup) {
				RosterBuddy found = findBuddy((RosterParent) objs[i], entryID);
				if (found != null)
					return found;
			}
		}
		return null;
	}

	public void replaceEntry(ID svcID, RosterParent parent, IRosterEntry entry) {
		RosterBuddy tb = findBuddy(parent, entry);
		RosterParent tp = null;
		// If entry already in tree, remove it from current position
		if (tb != null) {
			tp = tb.getParent();
			if (tp != null) {
				tp.removeChild(tb);
				if (tp.getName().equals(RosterView.UNFILED_GROUP_NAME)) {
					if (!tp.hasChildren()) {
						RosterParent tpp = tp.getParent();
						tpp.removeChild(tp);
					}
				}
			}
		}
		// Create new buddy
		RosterBuddy newBuddy = createBuddy(svcID, tb, entry);
		// If it's a replacement for an existing buddy with group (tg), then
		// simply add as child
		if (tp != null) {
			tp.addChild(newBuddy);
		} else {
			// The parent group is not there
			Iterator groups = entry.getGroups().iterator();
			// If the entry has any group, then take first one
			if (groups.hasNext()) {
				// There's a group associated with entry
				String groupName = ((IRosterGroup) groups.next()).getName();
				// Check to see if group already there
				RosterGroup oldgrp = findGroup(parent, groupName);
				// If so, simply add new buddy structure to existing group
				if (oldgrp != null)
					oldgrp.addChild(newBuddy);
				else {
					// There is a group name, but check to make sure it's
					// valid
					if (groupName.equals(""))
						groupName = RosterView.UNFILED_GROUP_NAME;
					addBuddyWithGroupName(parent, parent.getID(), groupName,
							newBuddy);
				}
			} else {
				// No group name, so we add under UNFILED_GROUP_NAME
				addBuddyWithGroupName(parent, parent.getID(),
						RosterView.UNFILED_GROUP_NAME, newBuddy);
			}
		}
	}

	protected void addBuddyWithGroupName(RosterParent parent, ID serviceID,
			String groupName, RosterBuddy newBuddy) {
		RosterGroup tg = findGroup(parent, groupName);
		if (tg == null) {
			tg = new RosterGroup(groupName, serviceID);
			tg.addChild(newBuddy);
			parent.addChild(tg);
		} else {
			tg.addChild(newBuddy);
		}
	}

	public void addAccount(ID accountID, String name) {
		RosterGroup oldgrp = findGroup(root, accountID);
		if (oldgrp != null)
			// If the name is already there, then skip
			return;
		// Group not there...add it
		root.addChild(new RosterAccount(name, accountID));
	}

	protected RosterGroup findAccount(String accountName) {
		return findGroup(root, accountName);
	}

	protected RosterGroup findAccount(ID acct) {
		return findGroup(root, acct);
	}

	public void addGroup(ID svcID, String name) {
		RosterGroup accountRoot = findAccount(svcID);
		if (accountRoot != null)
			addGroup(svcID, accountRoot, name);
	}

	public void addGroup(ID svcID, RosterParent parent, String name) {
		RosterGroup oldgrp = findGroup(parent, name);
		if (oldgrp != null)
			// If the name is already there, then skip
			return;
		// Group not there...add it
		RosterGroup newgrp = new RosterGroup(name, svcID);
		parent.addChild(newgrp);
	}

	public void removeGroup(RosterParent parent, String name) {
		RosterGroup oldgrp = findGroup(parent, name);
		if (oldgrp == null)
			// if not there, simply return
			return;
		// Else it is there...and we remove it
		parent.removeChild(oldgrp);
	}

	public void removeGroup(String name) {
		if (name == null)
			return;
		removeGroup(root, name);
	}

	public void handleRosterEntryUpdate(ID serviceID, IRosterEntry entry) {
		if (entry == null)
			return;
		RosterGroup tg = findAccount(serviceID.getName());
		replaceEntry(serviceID, tg, entry);		
	}
	
	public void handlePresence(ID groupID, ID userID, IPresence presence) {
		RosterBuddy buddy = findBuddy(findAccount(groupID.getName()), userID);
		if (buddy != null) fillPresence(buddy,presence);
	}
	
	public void handleRosterEntryAdd(ID serviceID, IRosterEntry entry) {
		handleRosterEntryUpdate(serviceID,entry);
	}

	public void handleRosterEntryRemove(ID entry) {
		if (entry == null)
			return;
		RosterUserAccount ua = this.rosterView.getAccountForUser(entry);
		if (ua == null)
			return;
		ID svcID = ua.getServiceID();
		RosterGroup tg = findAccount(svcID.getName());
		removeEntry(tg, entry);
	}

	public void removeEntry(RosterParent parent, ID entry) {
		RosterBuddy buddy = findBuddy(parent, entry);
		if (buddy == null)
			return;
		RosterParent p = buddy.getParent();
		if (p != null) {
			p.removeChild(buddy);
			this.rosterView.refreshView();
		}
	}

	protected void removeChildren(RosterParent parent, ID svcID) {
		RosterObject[] childs = parent.getChildren();
		for (int i = 0; i < childs.length; i++) {
			if (childs[i] instanceof RosterParent) {
				removeChildren((RosterParent) childs[i], svcID);
			}
			if (childs[i] instanceof RosterBuddy) {
				RosterBuddy tb = (RosterBuddy) childs[i];
				ID id = tb.getServiceID();
				if (id.equals(svcID)) {
					parent.removeChild(tb);
				}
			} else if (childs[i] instanceof RosterGroup) {
				RosterGroup tg = (RosterGroup) childs[i];
				ID id = tg.getID();
				if (id.equals(svcID)) {
					parent.removeChild(tg);
				}
			}
		}
	}

	public void removeAllEntriesForAccount(RosterUserAccount account) {
		if (account == null) {
			root = null;
		} else {
			removeChildren(root, account.getServiceID());
		}
	}
}
 No newline at end of file