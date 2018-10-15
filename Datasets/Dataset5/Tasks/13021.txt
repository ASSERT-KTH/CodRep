l.handleRosterUpdate(roster, changedItem);

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
import java.util.Iterator;
import java.util.List;

public abstract class AbstractRosterManager implements IRosterManager {

	protected IRoster roster;
	
	protected List rosterSubscriptionListeners = new ArrayList();
	protected List rosterUpdateListeners = new ArrayList();
	
	public synchronized void addRosterSubscriptionListener(
			IRosterSubscriptionListener listener) {
		if (listener == null) return;
		rosterSubscriptionListeners.add(listener);
	}

	public synchronized void addRosterUpdateListener(IRosterUpdateListener listener) {
		if (listener == null) return;
		rosterUpdateListeners.add(listener);
	}

	protected void fireRosterUpdate(IRosterItem changedItem) {
		synchronized (this) {
			for(Iterator i=rosterUpdateListeners.iterator(); i.hasNext(); ) {
				IRosterUpdateListener l = (IRosterUpdateListener) i.next();
				l.handleRosterUpdate(changedItem);
			}
		}
	}
	
	public abstract IPresenceSender getPresenceSender();

	public IRoster getRoster() {
		return roster;
	}

	public abstract IRosterSubscriptionSender getRosterSubscriptionSender();

	public abstract IRosterUpdateSender getRosterUpdateSender();

	public synchronized void removeRosterSubscriptionListener(
			IRosterSubscriptionListener listener) {
		if (listener == null) return;
		rosterSubscriptionListeners.remove(listener);
	}

	public synchronized void removeRosterUpdateListener(IRosterUpdateListener listener) {
		if (listener == null) return;
		rosterSubscriptionListeners.remove(listener);
	}

	public Object getAdapter(Class adapter) {
		return null;
	}

}