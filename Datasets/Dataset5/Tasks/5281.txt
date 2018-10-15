return getImageDescriptor(SharedImages.IMG_IDENTITY);

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

import org.eclipse.core.runtime.IAdapterFactory;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.IRosterGroup;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.model.IWorkbenchAdapter;

/**
 * Adapter factory for adapter to IWorkbenchAdapter (labels and images).
 * Subclasses may override as desired and appropriate. The adapter factory is to
 * be used with the <code>org.eclipse.core.runtime.adapters</code> extension
 * point. Here is example markup for the
 * 
 * <pre>
 * &lt;extension point=&quot;org.eclipse.core.runtime.adapters&quot; &gt;
 *      &lt;factory adaptableType=&quot;org.eclipse.ecf.presence.roster.Roster&quot;
 *                class=&quot;org.eclipse.ecf.presence.ui.RosterWorkbenchAdapterFactory&quot;&gt;
 *           &lt;adapter type=&quot;org.eclipse.ui.model.IWorkbenchAdapter&quot;&gt;
 *           &lt;/adapter&gt;
 *      &lt;/factory&gt;
 * &lt;/extension&gt;
 * </pre>
 */
public class RosterWorkbenchAdapterFactory implements IAdapterFactory {

	protected ImageDescriptor getImageDescriptor(String iconFile) {
		return SharedImages.getImageDescriptor(iconFile);
	}

	protected String getRosterLabel(IRoster roster) {
		IUser user = roster.getUser();
		return user == null ? Messages.RosterWorkbenchAdapterFactory_Disconnected
				: user.getName();
	}

	protected ImageDescriptor getRosterImageDescriptor(IRoster roster) {
		IUser user = roster.getUser();
		if (user == null)
			return getImageDescriptor(SharedImages.IMG_USER_UNAVAILABLE);
		else
			return getImageDescriptor(SharedImages.IMG_USER_AVAILABLE);
	}

	private IWorkbenchAdapter rosterAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			IRoster roster = (IRoster) o;
			return roster.getItems().toArray();
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterImageDescriptor((IRoster) object);
		}

		public String getLabel(Object o) {
			return getRosterLabel((IRoster) o);
		}

		public Object getParent(Object o) {
			return null;
		}
	};

	protected int getEntriesAvailableCount(Collection entries) {
		int count = 0;
		synchronized (entries) {
			for (Iterator i = entries.iterator(); i.hasNext();) {
				Object o = i.next();
				if (o instanceof IRosterEntry) {
					IRosterEntry entry = (IRosterEntry) o;
					if (entry.getPresence().getType().equals(
							IPresence.Type.AVAILABLE))
						count++;
				}
			}
		}
		return count;
	}

	protected int getEntriesTotalCount(Collection entries) {
		int count = 0;
		synchronized (entries) {
			for (Iterator i = entries.iterator(); i.hasNext();) {
				Object o = i.next();
				if (o instanceof IRosterEntry)
					count++;
			}
		}
		return count;
	}

	protected String getRosterGroupLabel(IRosterGroup group) {
		Collection entries = group.getEntries();
		return NLS.bind(Messages.RosterWorkbenchAdapterFactory_GroupLabel,
				new Object[] { group.getName(),
						Integer.toString(getEntriesAvailableCount(entries)),
						Integer.toString(getEntriesTotalCount(entries)) });
	}

	protected ImageDescriptor getRosterGroupImageDescriptor(IRosterGroup group) {
		return getImageDescriptor(SharedImages.IMG_GROUP);
	}

	private IWorkbenchAdapter rosterGroupAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			return ((IRosterGroup) o).getEntries().toArray();
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterGroupImageDescriptor((IRosterGroup) object);
		}

		public String getLabel(Object o) {
			return getRosterGroupLabel((IRosterGroup) o);
		}

		public Object getParent(Object o) {
			return ((IRosterGroup) o).getParent();
		}

	};

	protected String getRosterItemLabel(IRosterItem item) {
		return item.getName();
	}

	protected ImageDescriptor getRosterItemImageDescriptor(IRosterItem item) {
		return null;
	}

	private IWorkbenchAdapter rosterItemAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			return new Object[0];
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterItemImageDescriptor((IRosterItem) object);
		}

		public String getLabel(Object o) {
			return getRosterItemLabel((IRosterItem) o);
		}

		public Object getParent(Object o) {
			return ((IRosterItem) o).getParent();
		}

	};

	protected String getRosterEntryLabel(IRosterEntry entry) {
		return entry.getName();
	}

	protected ImageDescriptor getRosterEntryImageDescriptor(IRosterEntry entry) {
		IPresence p = entry.getPresence();
		if (p != null) {
			IPresence.Type pType = p.getType();
			IPresence.Mode pMode = p.getMode();
			// If type is unavailable then we're unavailable
			if (pType.equals(IPresence.Type.AVAILABLE)) {
				// if type and mode are both 'available' then we're actually
				// available
				if (pMode.equals(IPresence.Mode.AVAILABLE))
					return getImageDescriptor(SharedImages.IMG_USER_AVAILABLE);
				// If mode is away then we're away
				else if (pMode.equals(IPresence.Mode.AWAY)
						|| pMode.equals(IPresence.Mode.EXTENDED_AWAY))
					return getImageDescriptor(SharedImages.IMG_USER_AWAY);
				else if (pMode.equals(IPresence.Mode.DND))
					return getImageDescriptor(SharedImages.IMG_USER_DND);
			}
		}
		return getImageDescriptor(SharedImages.IMG_USER_UNAVAILABLE);
	}

	private IWorkbenchAdapter rosterEntryAdapter = new IWorkbenchAdapter() {

		public Object[] getChildren(Object o) {
			return new Object[0];
		}

		public ImageDescriptor getImageDescriptor(Object object) {
			return getRosterEntryImageDescriptor((IRosterEntry) object);
		}

		public String getLabel(Object o) {
			return getRosterEntryLabel((IRosterEntry) o);
		}

		public Object getParent(Object o) {
			return ((IRosterEntry) o).getParent();
		}

	};

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.IAdapterFactory#getAdapter(java.lang.Object,
	 *      java.lang.Class)
	 */
	public Object getAdapter(Object adaptableObject, Class adapterType) {
		if (adapterType.equals(IWorkbenchAdapter.class)) {
			if (adaptableObject instanceof IRoster)
				return rosterAdapter;
			if (adaptableObject instanceof IRosterGroup)
				return rosterGroupAdapter;
			if (adaptableObject instanceof IRosterEntry)
				return rosterEntryAdapter;
			if (adaptableObject instanceof IRosterItem)
				return rosterItemAdapter;
		}
		return null;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.core.runtime.IAdapterFactory#getAdapterList()
	 */
	public Class[] getAdapterList() {
		return new Class[] { IWorkbenchAdapter.class };
	}

}