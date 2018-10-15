Display.getDefault().asyncExec(new Runnable() {

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

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.presence.roster.IRosterManager;
import org.eclipse.ecf.presence.roster.IRosterUpdateListener;
import org.eclipse.swt.widgets.Display;

/**
 * A roster account appropriate for usage by a MultiRosterView. This class
 * provides a holder for an IContainer instance used by an
 * {@link IMultiRosterViewPart}. Subclasses may be created as desired.
 */
public class MultiRosterAccount {

	protected final MultiRosterView multiRosterView;

	protected IContainer container;

	protected IPresenceContainerAdapter adapter;

	IRosterUpdateListener updateListener = new IRosterUpdateListener() {
		public void handleRosterUpdate(final IRoster roster,
				final IRosterItem changedValue) {
			Display.getDefault().syncExec(new Runnable() {
				public void run() {
					MultiRosterAccount.this.multiRosterView.refreshTreeViewer(
							changedValue, true);
				}
			});
		}
	};

	public MultiRosterAccount(MultiRosterView multiRosterView,
			IContainer container, IPresenceContainerAdapter adapter) {
		this.multiRosterView = multiRosterView;
		Assert.isNotNull(container);
		Assert.isNotNull(adapter);
		this.container = container;
		this.adapter = adapter;
		getRosterManager().addRosterUpdateListener(updateListener);
	}

	public IContainer getContainer() {
		return container;
	}

	public IPresenceContainerAdapter getPresenceContainerAdapter() {
		return adapter;
	}

	public IRosterManager getRosterManager() {
		return getPresenceContainerAdapter().getRosterManager();
	}

	public IRoster getRoster() {
		return getRosterManager().getRoster();
	}

	public void dispose() {
		getRosterManager().removeRosterUpdateListener(updateListener);
		container = null;
		adapter = null;
	}
}
 No newline at end of file