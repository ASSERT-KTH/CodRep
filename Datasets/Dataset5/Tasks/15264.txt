Trace.trace(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.DEBUG, msg + ";container=" + container.getID() + ";existingmembers=" + groupManager); //$NON-NLS-1$

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

package org.eclipse.ecf.provider.generic;

import java.util.HashSet;
import java.util.Iterator;
import java.util.Observable;
import java.util.Observer;
import java.util.TreeMap;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.provider.ECFProviderDebugOptions;
import org.eclipse.ecf.internal.provider.ProviderPlugin;
import org.eclipse.ecf.provider.generic.gmm.GMMImpl;
import org.eclipse.ecf.provider.generic.gmm.Member;
import org.eclipse.ecf.provider.generic.gmm.MemberChanged;

class SOContainerGMM implements Observer {
	SOContainer container;
	Member localMember;
	GMMImpl groupManager;
	// Maximum number of members. Default is -1 (no maximum).
	int maxMembers = -1;
	TreeMap loading, active;

	SOContainerGMM(SOContainer cont, Member local) {
		container = cont;
		groupManager = new GMMImpl();
		groupManager.addObserver(this);
		loading = new TreeMap();
		active = new TreeMap();
		localMember = local;
		addMember(local);
	}

	protected void debug(String msg) {
		if (Trace.shouldTrace(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.DEBUG)) {
			Trace.trace(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.DEBUG, msg + ";container=" + container.getID() + ";members=" + groupManager); //$NON-NLS-1$
		}
	}

	protected void traceStack(String msg, Throwable e) {
		Trace.catching(ProviderPlugin.PLUGIN_ID, ECFProviderDebugOptions.EXCEPTIONS_CATCHING, SOContainerGMM.class, container.getID() + ":" + msg, e); //$NON-NLS-1$
	}

	ID[] getSharedObjectIDs() {
		return getActiveKeys();
	}

	synchronized boolean addMember(Member m) {
		debug("addMember(" + m.getID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		if (maxMembers > 0 && getSize() > maxMembers) {
			return false;
		} else {
			return groupManager.addMember(m);
		}
	}

	synchronized int setMaxMembers(int max) {
		debug("setMaxMembers(" + max + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		final int old = maxMembers;
		maxMembers = max;
		return old;
	}

	synchronized int getMaxMembers() {
		return maxMembers;
	}

	synchronized boolean removeMember(Member m) {
		final boolean res = groupManager.removeMember(m);
		if (res) {
			removeSharedObjects(m);
		}
		return res;
	}

	synchronized boolean removeMember(ID id) {
		debug("removeMember(" + id + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		final Member m = getMemberForID(id);
		if (m == null)
			return false;
		return removeMember(m);
	}

	void removeAllMembers() {
		removeAllMembers(null);
	}

	void removeNonLocalMembers() {
		removeAllMembers(localMember);
	}

	synchronized void removeAllMembers(Member exception) {
		if (exception == null) {
			debug("removeAllMembers()"); //$NON-NLS-1$
		} else {
			debug("removeAllMembers(" + exception.getID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		}
		final Object m[] = getMembers();
		for (int i = 0; i < m.length; i++) {
			final Member mem = (Member) m[i];
			if (exception == null || !exception.equals(mem))
				removeMember(mem);
		}
	}

	synchronized Object[] getMembers() {
		return groupManager.getMembers();
	}

	synchronized ID[] getOtherMemberIDs() {
		return groupManager.getMemberIDs(localMember.getID());
	}

	synchronized ID[] getMemberIDs() {
		return groupManager.getMemberIDs(null);
	}

	synchronized Member getMemberForID(ID id) {
		final Member newMem = new Member(id);
		for (final Iterator i = iterator(); i.hasNext();) {
			final Member oldMem = (Member) i.next();
			if (newMem.equals(oldMem))
				return oldMem;
		}
		return null;
	}

	synchronized int getSize() {
		return groupManager.getSize();
	}

	synchronized boolean containsMember(Member m) {
		if (m != null) {
			debug("containsMember(" + m.getID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		}
		return groupManager.containsMember(m);
	}

	synchronized Iterator iterator() {
		return groupManager.iterator();
	}

	// End group membership change methods
	synchronized boolean addSharedObject(SOWrapper ro) {
		if (ro != null)
			debug("addSharedObject(" + ro.getObjID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		if (getFromAny(ro.getObjID()) != null)
			return false;
		addSharedObjectToActive(ro);
		return true;
	}

	synchronized boolean addLoadingSharedObject(SOContainer.LoadingSharedObject lso) {
		if (lso != null)
			debug("addLoadingSharedObject(" + lso.getID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		if (getFromAny(lso.getID()) != null)
			return false;
		loading.put(lso.getID(), new SOWrapper(lso, container));
		// And start the thing
		lso.start();
		return true;
	}

	synchronized void moveSharedObjectFromLoadingToActive(SOWrapper ro) {
		if (ro != null)
			debug("moveSharedObjectFromLoadingToActive(" + ro.getObjID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		if (removeSharedObjectFromLoading(ro.getObjID()))
			addSharedObjectToActive(ro);
	}

	boolean removeSharedObjectFromLoading(ID id) {
		debug("removeSharedObjectFromLoading(" + id + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		if (loading.remove(id) != null) {
			return true;
		} else
			return false;
	}

	synchronized ID[] getActiveKeys() {
		return (ID[]) active.keySet().toArray(new ID[0]);
	}

	void addSharedObjectToActive(SOWrapper so) {
		if (so != null)
			debug("addSharedObjectToActive(" + so.getObjID() + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		active.put(so.getObjID(), so);
		so.activated();
	}

	synchronized void notifyOthersActivated(ID id) {
		debug("notifyOthersActivated(" + id + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		notifyOtherChanged(id, active, true);
	}

	synchronized void notifyOthersDeactivated(ID id) {
		debug("notifyOthersDeactivated(" + id + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		notifyOtherChanged(id, active, false);
	}

	void notifyOtherChanged(ID id, TreeMap aMap, boolean activated) {
		for (final Iterator i = aMap.values().iterator(); i.hasNext();) {
			final SOWrapper other = (SOWrapper) i.next();
			if (!id.equals(other.getObjID())) {
				other.otherChanged(id, activated);
			}
		}
	}

	synchronized boolean removeSharedObject(ID id) {
		debug("removeSharedObject(" + id + ")"); //$NON-NLS-1$ //$NON-NLS-2$
		final SOWrapper ro = removeFromMap(id, active);
		if (ro == null)
			return false;
		ro.deactivated();
		return true;
	}

	synchronized SOWrapper getFromMap(ID objID, TreeMap aMap) {
		return (SOWrapper) aMap.get(objID);
	}

	synchronized SOWrapper removeFromMap(ID objID, TreeMap aMap) {
		return (SOWrapper) aMap.remove(objID);
	}

	SOWrapper getFromLoading(ID objID) {
		return getFromMap(objID, loading);
	}

	SOWrapper getFromActive(ID objID) {
		return getFromMap(objID, active);
	}

	synchronized SOWrapper getFromAny(ID objID) {
		SOWrapper ro = getFromMap(objID, active);
		if (ro != null)
			return ro;
		ro = getFromMap(objID, loading);
		return ro;
	}

	// Notification methods
	void notifyAllOfMemberChange(Member m, TreeMap map, boolean add) {
		for (final Iterator i = map.values().iterator(); i.hasNext();) {
			final SOWrapper ro = (SOWrapper) i.next();
			ro.memberChanged(m, add);
		}
	}

	public void update(Observable o, Object arg) {
		final MemberChanged mc = (MemberChanged) arg;
		notifyAllOfMemberChange(mc.getMember(), active, mc.getAdded());
	}

	synchronized void removeSharedObjects(Member m) {
		removeSharedObjects(m, true);
	}

	synchronized void clear() {
		debug("clear()"); //$NON-NLS-1$
		removeSharedObjects(null, true);
	}

	void removeSharedObjects(Member m, boolean match) {
		final HashSet set = getRemoveIDs(m.getID(), match);
		final Iterator i = set.iterator();
		while (i.hasNext()) {
			final ID removeID = (ID) i.next();
			if (isLoading(removeID)) {
				removeSharedObjectFromLoading(removeID);
			} else {
				container.destroySharedObject(removeID);
			}
		}
	}

	HashSet getRemoveIDs(ID homeID, boolean match) {
		final HashSet aSet = new HashSet();
		for (final Iterator i = new DestroyIterator(loading, homeID, match); i.hasNext();) {
			aSet.add(i.next());
		}
		for (final Iterator i = new DestroyIterator(active, homeID, match); i.hasNext();) {
			aSet.add(i.next());
		}
		return aSet;
	}

	synchronized boolean isActive(ID id) {
		return active.containsKey(id);
	}

	synchronized boolean isLoading(ID id) {
		return loading.containsKey(id);
	}

	public String toString() {
		final StringBuffer sb = new StringBuffer();
		sb.append("SOContainerGMM["); //$NON-NLS-1$
		sb.append(groupManager);
		sb.append(";load:").append(loading); //$NON-NLS-1$
		sb.append(";active:").append(active).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
		return sb.toString();
	}
}

class DestroyIterator implements Iterator {
	ID next;
	ID homeID;
	Iterator i;
	boolean match;

	public DestroyIterator(TreeMap map, ID hID, boolean m) {
		i = map.values().iterator();
		homeID = hID;
		next = null;
		match = m;
	}

	public boolean hasNext() {
		if (next == null)
			next = getNext();
		return (next != null);
	}

	public Object next() {
		if (hasNext()) {
			final ID value = next;
			next = null;
			return value;
		} else {
			throw new java.util.NoSuchElementException();
		}
	}

	ID getNext() {
		while (i.hasNext()) {
			final SOWrapper ro = (SOWrapper) i.next();
			if (homeID == null || (match ^ !ro.getHomeID().equals(homeID))) {
				return ro.getObjID();
			}
		}
		return null;
	}

	public void remove() {
		throw new UnsupportedOperationException();
	}
}
 No newline at end of file