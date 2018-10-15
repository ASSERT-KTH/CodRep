public class RosterWorkbenchAdapterFactory implements IAdapterFactory {

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
package org.eclipse.ecf.presence.ui;

import java.util.Collection;
import java.util.Iterator;
import java.util.Map;

import org.eclipse.core.runtime.IAdapterFactory;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.presence.roster.IPresence;
import org.eclipse.ecf.presence.roster.Roster;
import org.eclipse.ecf.presence.roster.RosterEntry;
import org.eclipse.ecf.presence.roster.RosterGroup;
import org.eclipse.ecf.presence.roster.RosterItem;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.ui.model.IWorkbenchAdapter;

public class RosterAdapterFactory implements IAdapterFactory {

	private static final String LEFT_PAREN = "(";
	private static final String RIGHT_PAREN = ")";
	private static final String SLASH = "/";
	private static final String ROSTER_DISCONNECTED_NAME = LEFT_PAREN
			+ "disconnected" + RIGHT_PAREN;

	protected String getRosterLabel(Roster roster) {
		IUser user = roster.getUser();
		if (user == null)
			return ROSTER_DISCONNECTED_NAME;
		else
			return user.getName();
	}

	protected ImageDescriptor getRosterImageDescriptor(Roster roster) {
		return null;
	}

	private IWorkbenchAdapter rosterAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			Roster roster = (Roster) o;
			return roster.getItems().toArray();
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterImageDescriptor((Roster) object);
		}

		public String getLabel(Object o) {
			return getRosterLabel((Roster) o);
		}

		public Object getParent(Object o) {
			return null;
		}
	};

	protected int getEntriesAvailableCount(Collection entries) {
		int count = 0;
		for (Iterator i = entries.iterator(); i.hasNext();) {
			Object o = i.next();
			if (o instanceof RosterEntry) {
				RosterEntry entry = (RosterEntry) o;
				if (entry.getPresence().getMode().equals(
						IPresence.Mode.AVAILABLE))
					count++;
			}
		}
		return count;
	}

	protected int getEntriesTotalCount(Collection entries) {
		int count = 0;
		for (Iterator i = entries.iterator(); i.hasNext();) {
			Object o = i.next();
			if (o instanceof RosterEntry)
				count++;
		}
		return count;
	}

	protected String getRosterGroupLabel(RosterGroup group) {
		Collection entries = group.getEntries();
		StringBuffer buf = new StringBuffer(group.getName()).append(" ");
		buf.append(LEFT_PAREN).append(getEntriesAvailableCount(entries)).append(SLASH);
		buf.append(getEntriesTotalCount(entries)).append(RIGHT_PAREN);
		return buf.toString();
	}

	protected ImageDescriptor getRosterGroupImageDescriptor(RosterGroup group) {
		return null;
	}
	
	private IWorkbenchAdapter rosterGroupAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			return ((RosterGroup) o).getEntries().toArray();
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterGroupImageDescriptor((RosterGroup) object);
		}

		public String getLabel(Object o) {
			return getRosterGroupLabel((RosterGroup) o);
		}

		public Object getParent(Object o) {
			return ((RosterGroup) o).getParent();
		}

	};

	protected String getRosterItemLabel(RosterItem item) {
		return item.getName();
	}

	protected ImageDescriptor getRosterItemImageDescriptor(RosterItem item) {
		return null;
	}
	

	private IWorkbenchAdapter rosterItemAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			return new Object[0];
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterItemImageDescriptor((RosterItem) object);
		}

		public String getLabel(Object o) {
			return getRosterItemLabel((RosterItem) o);
		}

		public Object getParent(Object o) {
			return ((RosterItem) o).getParent();
		}

	};

	protected Object[] getRosterEntryChildrenFromPresence(RosterEntry entry) {
		IPresence presence = entry.getPresence();
		Map properties = presence.getProperties();
		int fixedEntries = 2;
		Object[] children = new Object[fixedEntries + properties.size()];
		children[0] = new RosterItem(entry, "User: "
				+ entry.getUser().getName());
		children[1] = new RosterItem(entry, "Status: " + presence.getStatus());
		for (Iterator i = properties.keySet().iterator(); i.hasNext(); fixedEntries++) {
			children[fixedEntries] = properties.get(i.next());
		}
		return children;
	}

	protected String getRosterEntryLabel(RosterEntry entry) {
		return entry.getName();
	}

	protected ImageDescriptor getRosterEntryImageDescriptor(RosterEntry entry) {
		return null;
	}
	

	private IWorkbenchAdapter rosterEntryAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			return getRosterEntryChildrenFromPresence((RosterEntry) o);
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterEntryImageDescriptor((RosterEntry) object);
		}

		public String getLabel(Object o) {
			return getRosterEntryLabel((RosterEntry) o);
		}

		public Object getParent(Object o) {
			return ((RosterEntry) o).getParent();
		}

	};

	public Object getAdapter(Object adaptableObject, Class adapterType) {
		if (adapterType.equals(IWorkbenchAdapter.class)) {
			if (adaptableObject instanceof Roster)
				return rosterAdapter;
			if (adaptableObject instanceof RosterGroup)
				return rosterGroupAdapter;
			if (adaptableObject instanceof RosterEntry)
				return rosterEntryAdapter;
			if (adaptableObject instanceof RosterItem)
				return rosterItemAdapter;
		}
		return null;
	}

	public Class[] getAdapterList() {
		return new Class[] { IWorkbenchAdapter.class };
	}

}