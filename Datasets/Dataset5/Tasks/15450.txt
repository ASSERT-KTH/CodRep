view.setSubscription(subscription);

/**
 * Copyright (c) 2006 Ecliptical Software Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Ecliptical Software Inc. - initial API and implementation
 */
package org.eclipse.ecf.example.pubsub;

import java.io.IOException;
import java.util.Vector;

import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.SharedObjectCreateException;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.example.collab.CollabClient;
import org.eclipse.ecf.pubsub.IPublishedServiceDirectory;
import org.eclipse.ecf.pubsub.IPublishedServiceDirectoryListener;
import org.eclipse.ecf.pubsub.IPublishedServiceRequestor;
import org.eclipse.ecf.pubsub.ISubscription;
import org.eclipse.ecf.pubsub.ISubscriptionCallback;
import org.eclipse.ecf.pubsub.PublishedServiceDescriptor;
import org.eclipse.ecf.pubsub.PublishedServiceDirectoryChangeEvent;
import org.eclipse.ecf.pubsub.model.IMasterModel;
import org.eclipse.ecf.pubsub.model.SharedModelFactory;
import org.eclipse.ecf.pubsub.model.impl.LocalAgent;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerSorter;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.BaseSelectionListenerAction;
import org.eclipse.ui.part.ViewPart;

public class PubSubView extends ViewPart {
	
	protected TableViewer viewer;
	
	protected MenuManager menuManager;

	protected ISharedObjectContainer container;
	
	private BaseSelectionListenerAction subscribeAction;
	
	protected TableViewer sharedListViewer;
	
	protected MenuManager sharedListMenuManager;
	
	private BaseSelectionListenerAction appendAction;
	
	protected final Vector sharedLists = new Vector();
	
	public void init(IViewSite site) throws PartInitException {
		super.init(site);
		
		final Action shareSomethingAction = new Action("Share something") {
			public void run() {
				try {
					IMasterModel sds = SharedModelFactory.getInstance().createSharedDataSource(container, IDFactory.getDefault().createGUID(), new AppendableList(), ListAppender.ID);
					if (sds == null)
						MessageDialog.openError(getSite().getShell(), "Error", "Could not share anything.");
					else {
						sharedLists.add(sds);
						sharedListViewer.add(sds);
					}
				} catch (SharedObjectCreateException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IDInstantiationException e) {
					throw new RuntimeException(e);
				}
			}
		};
		
		shareSomethingAction.setEnabled(false);
		
		IMenuManager mgr = site.getActionBars().getMenuManager();
		mgr.add(new Action("Start") {
			public void run() {
				container = CollabClient.getContainer(ResourcesPlugin.getWorkspace().getRoot());
				if (container == null) {
					MessageDialog.openError(getSite().getShell(), "Error", "Collaboration environment not found.");
					return;
				}
				
				IPublishedServiceDirectory directory = (IPublishedServiceDirectory) container.getAdapter(IPublishedServiceDirectory.class);
				viewer.setInput(directory);
				setEnabled(false);
				shareSomethingAction.setEnabled(true);
			}
		});
		
		mgr.add(shareSomethingAction);
		
		menuManager = new MenuManager();
		subscribeAction = new BaseSelectionListenerAction("Subscribe") {
					
			public void run() {
				PublishedServiceDescriptor desc = (PublishedServiceDescriptor) getStructuredSelection().getFirstElement();
				IPublishedServiceRequestor requestor = (IPublishedServiceRequestor) container.getAdapter(IPublishedServiceRequestor.class);
				requestor.subscribe(desc.getContainerID(), desc.getSharedObjectID(), new SubscriptionViewOpener());
			}
			
			protected boolean updateSelection(IStructuredSelection selection) {
				return !selection.isEmpty();
			}
		};
				
		subscribeAction.setEnabled(false);
		menuManager.add(subscribeAction);
		
		sharedListMenuManager = new MenuManager();
		appendAction = new BaseSelectionListenerAction("Append...") {
			
			public void run() {
				InputDialog dlg = new InputDialog(getSite().getShell(), "Append to Shared List", "Enter element to append:", null, null);
				dlg.open();
				String value = dlg.getValue();
				if (value != null) {
					LocalAgent model = (LocalAgent) getStructuredSelection().getFirstElement();
					AppendableList list = (AppendableList) model.getData();
					if (list.add(value)) {
						try {
							model.update(value);
						} catch (IOException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
					}
				}
			}
			
			protected boolean updateSelection(IStructuredSelection selection) {
				return !selection.isEmpty();
			}
		};
		
		appendAction.setEnabled(false);
		sharedListMenuManager.add(appendAction);
	}

	public void createPartControl(Composite parent) {
		Composite composite = new Composite(parent, SWT.NONE);
		composite.setLayout(new GridLayout(2, true));
		
		Label label = new Label(composite, SWT.NONE);
		label.setText("Remote Shared Services");

		label = new Label(composite, SWT.NONE);
		label.setText("Local Shared Sample Lists");
		
		viewer = new TableViewer(composite);
		viewer.getTable().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		viewer.setUseHashlookup(true);
		viewer.setLabelProvider(new LabelProvider());
		viewer.setContentProvider(new ContentProvider());
		viewer.setSorter(new ViewerSorter());
		viewer.addSelectionChangedListener(subscribeAction);
		viewer.getControl().setMenu(menuManager.createContextMenu(viewer.getControl()));
		
		sharedListViewer = new TableViewer(composite);
		sharedListViewer.getTable().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		sharedListViewer.setUseHashlookup(true);
		sharedListViewer.setLabelProvider(new LabelProvider());
		sharedListViewer.setContentProvider(new ArrayContentProvider());
		sharedListViewer.addSelectionChangedListener(appendAction);
		sharedListViewer.getControl().setMenu(sharedListMenuManager.createContextMenu(sharedListViewer.getControl()));
	}

	public void setFocus() {
		viewer.getControl().setFocus();
	}
	
	public void dispose() {
		menuManager.dispose();
		
		if (container != null)
			container.disconnect();
		
		super.dispose();
	}
	
	protected class ContentProvider implements IStructuredContentProvider, IPublishedServiceDirectoryListener {
		
		private Viewer viewer;

		public Object[] getElements(Object inputElement) {
			return new Object[0];
		}

		public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
			this.viewer = viewer;
			
			if (oldInput instanceof IPublishedServiceDirectory)
				((IPublishedServiceDirectory) oldInput).removeReplicatedServiceListener(this);
			
			if (newInput instanceof IPublishedServiceDirectory)
				((IPublishedServiceDirectory) newInput).addReplicatedServiceListener(this);
		}

		public void dispose() {
			viewer = null;
		}

		public void publishedServiceDirectoryChanged(final PublishedServiceDirectoryChangeEvent event) {
			if (viewer instanceof TableViewer) {
				Control ctrl = viewer == null ? null : viewer.getControl();
				if (ctrl != null && !ctrl.isDisposed())
					ctrl.getDisplay().asyncExec(new Runnable() {
						public void run() {
							TableViewer tableViewer = (TableViewer) viewer;
							if (event.getKind() == PublishedServiceDirectoryChangeEvent.ADDED)
								tableViewer.add(event.getReplicatedServices());
							else
								tableViewer.remove(event.getReplicatedServices());
						}
					});
			}
		}
	}
	
	protected class SubscriptionViewOpener implements ISubscriptionCallback {
		
		public void subscribed(final ISubscription subscription) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					SubscriptionView view;
					try {
						view = (SubscriptionView) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(SubscriptionView.VIEW_ID, subscription.getID().getName(), IWorkbenchPage.VIEW_ACTIVATE);
					} catch (PartInitException e) {
						ErrorDialog.openError(getSite().getShell(), "Subscription Error", "Could not create subscription view.", e.getStatus());
						return;
					}
		
					view.setSubscription(container, subscription);
				}
			});
		}

		public void requestFailed(final Throwable t) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					MessageDialog.openError(getSite().getShell(), "Subscription Error", t.getLocalizedMessage());
				}
			});
		}
	}
}