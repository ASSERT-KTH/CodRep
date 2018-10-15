private static final String COLLABORATION_PROJECTS_ARE_NOT_AVAILABLE_ = "No project collaboration sessions joined.\n\nTo join a project collaboration, select a project in either the Navigator or Package Explorer view,\nright-click to open context menu for project, choose ECF menu, and choose 'Connect Project...'.";

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

package org.eclipse.ecf.example.collab.ui;

import java.util.Enumeration;
import java.util.Hashtable;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.IMemento;
import org.eclipse.ui.IViewSite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.part.ViewPart;


public class LineChatView extends ViewPart {
	// The single view
	private static final String COLLABORATION_PROJECTS_ARE_NOT_AVAILABLE_ = "No project collaboration sessions joined.\n\nTo join a project collaboration session, select a project in either the Navigator or Package Explorer view,\nright-click to open context menu for project, choose ECF menu, and choose 'Join ECF Collaboration...'.";
	static protected LineChatView singleton = null;
	
	static protected Hashtable clientViews = new Hashtable();
	
	TabFolder tabFolder = null;	
	
	Composite parentComposite = null;
	
	Label inactiveLabel = null;
	
    /*
	protected static ID appShare = null;
	protected static EclipseAppShareServer appShareServer = null;
	
	protected static void setAppShareID(ID newID, EclipseAppShareServer server) {
		synchronized (clientViews) {
			appShare = newID;
			appShareServer = server;
			stopAppShareAction.setServer(appShareServer);
			if (newID == null) {
				removeActionFromToolbar(stopAppShareAction);
			} else {
				addActionToToolbar(stopAppShareAction);
			}
		}
	}
	protected static ID getAppShareID() {
		return appShare;
	}
	protected static boolean appShareActive() {
		return (appShare != null);
	}
	*/
	public static boolean isDisposed() {
		return (singleton == null);
	}
	public LineChatView() {
	}
	protected Object addClientView(LineChatClientView cv, TabItem ti) {
		synchronized (clientViews) {
			return clientViews.put(cv,ti);
		}
	}
	protected void removeClientView(LineChatClientView cv) {
		final TabItem ti = (TabItem) clientViews.remove(cv);
		

		// Clean up app share
        
/*		final ID appShareID = cv.getAppShareID();
		if (appShareID != null) {
			if (appShareID.equals(appShare)) {
				appShareServer.destroySelf();
			}
		}*/
        
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
                /*
				if (appShareID != null) {
					if (appShareID.equals(appShare)) {
						setAppShareID(null,null);
					}
				}
                */
				if (ti != null) ti.dispose();
				
				if (clientViews.isEmpty()) {
                    if (singleton != null) {
                        if (singleton.tabFolder != null) {
                            singleton.tabFolder.dispose();
                            singleton.tabFolder = null;
                        }
					
                        createInactiveComposite(singleton.parentComposite);
                        actionBars.getToolBarManager().removeAll();
                        actionBars.getMenuManager().removeAll();
                        actionBars.updateActionBars();
                        singleton.parentComposite.layout();
                    }
				}
			}
		});
		

		
		//if (clientViews.size()==0) {
		//	this.hideView();
		//} 
	}
	
	protected void hideView() {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					IWorkbenchPage wp = LineChatView.this.getSite().getPage();
					wp.hideView(LineChatView.this); 
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}
	
	public static LineChatClientView makeClientView(final LineChatHandler lch, final String name,final String initText,String downloaddir) 
		throws Exception {
		LineChatClientView newView = null;
		synchronized (clientViews) {
			if (singleton == null) throw new InstantiationException("View not initialized");
			
			if (singleton.inactiveLabel != null) {
				singleton.inactiveLabel.dispose();
			}
			
			if (singleton.tabFolder == null) {
				singleton.tabFolder = new TabFolder(singleton.parentComposite, SWT.NORMAL);
			}
			
			newView = new LineChatClientView(lch,singleton,name,initText,downloaddir);
			TabItem ti = new TabItem(singleton.tabFolder,SWT.NULL);
			ti.setControl(newView.getTeamChat());
			ti.setText(newView.name);
			singleton.addClientView(newView,ti);
			actionBars.updateActionBars();
			singleton.parentComposite.layout();
		}
		return newView;
	}
	
	public void setFocus() {
		synchronized (clientViews) {
			singleton.parentComposite.setFocus();
		}
	}
	
	static class StopAppShareAction extends Action {
		String id = null;
        /*
		EclipseAppShareServer server;
		*/
		public StopAppShareAction() {
			this("appshare.stop");
		}
		public StopAppShareAction(String id) {
			this.id = id;
			activateAction();
			super.setId(this.id);
		}
        /*
		protected void setServer(EclipseAppShareServer s) {
			server = s;
		}
        */
		protected void activateAction() {
            /*
			setText(ClientPlugin.getResourceString(id + ".text"));
			setDescription(ClientPlugin.getResourceString(id + ".tooltip"));
			setToolTipText(ClientPlugin.getResourceString(id + ".description"));
			setEnabled(true);
			try {
				final URL installUrl = ClientPlugin.getPluginTopLocation();
				final URL imageUrl = new URL(installUrl, ClientPlugin.getResourceString(id + ".image"));
				setImageDescriptor(ImageDescriptor.createFromURL(imageUrl));
			} catch (MalformedURLException e) {
				ClientPlugin.log("Exception loading image for action: "+id, e);	
			}
            */
		}
		
		public void run() {
			// Actually do something
            /*
			synchronized (clientViews) {
				if (server != null) {
					server.destroySelf();
					setAppShareID(null,null);
				}
			}
            */
		}
	}
	
	static IToolBarManager toolbarManager = null;
	static IActionBars actionBars = null;
	static StopAppShareAction stopAppShareAction = new StopAppShareAction();
	
	protected static void addActionToToolbar(Action action) {
		toolbarManager.add(action);
		actionBars.updateActionBars();
	}
	protected static void removeActionFromToolbar(Action action) {
		if (action == null) return;
		toolbarManager.remove(action.getId());
		actionBars.updateActionBars();
	}
	public void createPartControl(Composite parent) {
		singleton = this;
		IViewSite viewSite = this.getViewSite();
		actionBars = viewSite.getActionBars();
		toolbarManager = actionBars.getToolBarManager();
		parentComposite = parent;
		createInactiveComposite(parent);
	}
	
	private void createInactiveComposite(Composite parent) {
		inactiveLabel = new Label(parent, SWT.NONE);
		inactiveLabel.setText(COLLABORATION_PROJECTS_ARE_NOT_AVAILABLE_);
	}
	
	protected void disposeClient(LineChatClientView lccv) {
		if (singleton != null) singleton.removeClientView(lccv);		
	}
	public void dispose() {
		synchronized (clientViews) {
			closeAllClients();
		}
		singleton = null;
		super.dispose();
	}
	public void saveState(IMemento state) {
		// We can save state here, associated with all UI config for collab views
		// For now, we'll just use it to close the window
	}
	protected void closeAllClients() {
		for (Enumeration e=clientViews.keys();e.hasMoreElements();) {
			LineChatClientView vc = (LineChatClientView) e.nextElement();
			vc.closeClient();
		}
	}
	protected void setActiveTab(String name) {
		if (name == null) return;
		if (tabFolder != null) {
			TabItem [] items = tabFolder.getItems();
			if (items == null) return;
			for(int i=0; i < items.length; i++) {
				String itemName = items[i].getText();
				if (name.equals(itemName)) {
					tabFolder.setSelection(i);
				}
			}
		}
	}
}
 No newline at end of file