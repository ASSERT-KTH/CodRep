import org.eclipse.ecf.presence.IPresence;

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
import org.eclipse.ecf.internal.presence.ui.Activator;
import org.eclipse.ecf.internal.presence.ui.IImageFiles;
import org.eclipse.ecf.presence.roster.IPresence;
import org.eclipse.ecf.presence.roster.Roster;
import org.eclipse.ecf.presence.roster.RosterEntry;
import org.eclipse.ecf.presence.roster.RosterGroup;
import org.eclipse.ecf.presence.roster.RosterItem;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.ui.model.IWorkbenchAdapter;
import org.eclipse.ui.plugin.AbstractUIPlugin;

/**
 * Adapter factory for adapter to IWorkbenchAdapter (labels and images).
 * Subclasses may override as desired and appropriate. The adapter factory is to
 * be used with the <code>org.eclipse.core.runtime.adapters</code> extension
 * point. Here is example markup for the
 * 
 * <pre>
 *   &lt;extension point=&quot;org.eclipse.core.runtime.adapters&quot; &gt;
 *        &lt;factory
 *             adaptableType=&quot;org.eclipse.ecf.presence.roster.Roster&quot;
 *             class=&quot;org.eclipse.ecf.presence.ui.RosterWorkbenchAdapterFactory&quot;&gt;
 *          &lt;adapter
 *                type=&quot;org.eclipse.ui.model.IWorkbenchAdapter&quot;&gt;
 *          &lt;/adapter&gt;
 *       &lt;/factory&gt;
 *   &lt;/extension&gt;
 * </pre>
 */
public class RosterWorkbenchAdapterFactory implements IAdapterFactory {

	private static final String MODE_PREFIX = "Mode: ";
	private static final String TYPE_PREFIX = "Type: ";
	private static final String ACCOUNT_PREFIX = "Account: ";
	private static final String LEFT_PAREN = "(";
	private static final String RIGHT_PAREN = ")";
	private static final String SLASH = "/";
	private static final String ROSTER_DISCONNECTED_NAME = "connecting...";

	protected ImageDescriptor getImageDescriptor(String iconFile) {
		return AbstractUIPlugin.imageDescriptorFromPlugin(Activator.PLUGIN_ID,
				iconFile);
	}

	protected String getRosterLabel(Roster roster) {
		IUser user = roster.getUser();
		if (user == null)
			return ROSTER_DISCONNECTED_NAME;
		else
			return user.getName();
	}

	protected ImageDescriptor getRosterImageDescriptor(Roster roster) {
		IUser user = roster.getUser();
		if (user == null)
			return getImageDescriptor(IImageFiles.USER_UNAVAILABLE_ICON);
		else
			return getImageDescriptor(IImageFiles.USER_AVAILABLE_ICON);
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
		buf.append(LEFT_PAREN).append(getEntriesAvailableCount(entries))
				.append(SLASH);
		buf.append(getEntriesTotalCount(entries)).append(RIGHT_PAREN);
		return buf.toString();
	}

	protected ImageDescriptor getRosterGroupImageDescriptor(RosterGroup group) {
		return getImageDescriptor(IImageFiles.GROUP_ICON);
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
		int fixedEntries = 3;
		Object[] children = new Object[fixedEntries + properties.size()];
		children[0] = new RosterItem(entry, ACCOUNT_PREFIX
				+ entry.getUser().getID().getName());
		children[1] = new RosterItem(entry, TYPE_PREFIX
				+ presence.getType().toString());
		children[2] = new RosterItem(entry, MODE_PREFIX
				+ presence.getMode().toString());
		for (Iterator i = properties.keySet().iterator(); i.hasNext(); fixedEntries++) {
			children[fixedEntries] = properties.get(i.next());
		}
		return children;
	}

	protected String getRosterEntryLabel(RosterEntry entry) {
		return entry.getName();
	}

	protected ImageDescriptor getRosterEntryImageDescriptor(RosterEntry entry) {
		IPresence p = entry.getPresence();
		if (p != null) {
			IPresence.Type pType = p.getType();
			IPresence.Mode pMode = p.getMode();
			// If type is unavailable then we're unavailable
			if (pType.equals(IPresence.Type.AVAILABLE)) {
				// if type and mode are both 'available' then we're actually
				// available
				if (pMode.equals(IPresence.Mode.AVAILABLE))
					return getImageDescriptor(IImageFiles.USER_AVAILABLE_ICON);
				// If mode is away then we're away
				else if (pMode.equals(IPresence.Mode.AWAY)
						|| pMode.equals(IPresence.Mode.EXTENDED_AWAY))
					return getImageDescriptor(IImageFiles.USER_AWAY_ICON);
				else if (pMode.equals(IPresence.Mode.DND))
					return getImageDescriptor(IImageFiles.USER_DND_ICON);
			}
		}
		return getImageDescriptor(IImageFiles.USER_UNAVAILABLE_ICON);
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