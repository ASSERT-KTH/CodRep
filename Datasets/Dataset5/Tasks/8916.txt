Display.getDefault().syncExec(new Runnable() {

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

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.ecf.presence.roster.IRosterItem;
import org.eclipse.ecf.presence.roster.IRosterManager;
import org.eclipse.ecf.presence.roster.IRosterUpdateListener;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.part.ViewPart;

/**
 * View class for displaying multiple rosters in a tree viewer
 *
 */
public class MultiRosterView extends ViewPart implements IMultiRosterViewPart {

	protected TreeViewer treeViewer;

	protected MultiRosterLabelProvider rosterLabelProvider;

	protected MultiRosterContentProvider rosterContentProvider;

	protected List rosterAccounts = new ArrayList();

	/* (non-Javadoc)
	 * @see org.eclipse.ui.part.WorkbenchPart#createPartControl(org.eclipse.swt.widgets.Composite)
	 */
	public void createPartControl(Composite parent) {
		treeViewer = new TreeViewer(parent, SWT.BORDER | SWT.MULTI
				| SWT.V_SCROLL);
		getSite().setSelectionProvider(treeViewer);
		rosterContentProvider = new MultiRosterContentProvider();
		rosterLabelProvider = new MultiRosterLabelProvider();
		treeViewer.setLabelProvider(rosterLabelProvider);
		treeViewer.setContentProvider(rosterContentProvider);
		treeViewer.setInput(new Object());
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ui.part.WorkbenchPart#dispose()
	 */
	public void dispose() {
		super.dispose();
		treeViewer = null;
		rosterLabelProvider = null;
		rosterContentProvider = null;
		rosterAccounts.clear();
	}

	protected void addRosterAccountsToProviders() {
		for (Iterator i = rosterAccounts.iterator(); i.hasNext();) {
			RosterAccount account = (RosterAccount) i.next();
			rosterContentProvider.add(account.getRoster());
		}
	}

	protected boolean addRosterAccount(RosterAccount account) {
		if (account == null)
			return false;
		if (rosterAccounts.add(account)) {
			if (rosterContentProvider != null) {
				rosterContentProvider.add(account.getRoster());
			}
			return true;
		} else
			return false;
	}

	protected boolean removeRosterAccount(RosterAccount account) {
		if (account == null)
			return false;
		if (rosterAccounts.remove(account)) {
			if (rosterContentProvider != null) {
				rosterContentProvider.remove(account.getRoster());
			}
			account.dispose();
			return true;
		} else
			return false;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.part.WorkbenchPart#setFocus()
	 */
	public void setFocus() {
		treeViewer.getControl().setFocus();
	}

	class RosterAccount {
		IContainer container;

		IPresenceContainerAdapter adapter;

		IRosterUpdateListener updateListener = new IRosterUpdateListener() {
			public void handleRosterUpdate(final IRoster roster,
					final IRosterItem changedValue) {
				Display.getDefault().asyncExec(new Runnable() {
					public void run() {
						refreshTreeViewer(changedValue,true);
					}
				});
			}
		};

		public RosterAccount(IContainer container,
				IPresenceContainerAdapter adapter) {
			Assert.isNotNull(container);
			Assert.isNotNull(adapter);
			this.container = container;
			this.adapter = adapter;
			getRosterManager().addRosterUpdateListener(updateListener);
		}

		public IContainer getContainer() {
			return container;
		}

		public IPresenceContainerAdapter getPresenceAdapter() {
			return adapter;
		}

		public IRosterManager getRosterManager() {
			return getPresenceAdapter().getRosterManager();
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

	protected void refreshTreeViewer(Object val, boolean labels) {
		if (treeViewer != null) {
			if (val != null) treeViewer.refresh(val,labels);
			else treeViewer.refresh(labels);
		}
	}
	
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.ui.IMultiRosterViewPart#addContainer(org.eclipse.ecf.core.IContainer)
	 */
	public boolean addContainer(IContainer container) {
		if (container == null)
			return false;
		IPresenceContainerAdapter containerAdapter = (IPresenceContainerAdapter) container
				.getAdapter(IPresenceContainerAdapter.class);
		if (containerAdapter == null)
			return false;
		if (addRosterAccount(new RosterAccount(container, containerAdapter))) {
			refreshTreeViewer(null,true);
			return true;
		} else
			return false;
	}
}