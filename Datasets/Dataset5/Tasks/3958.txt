chatRooms.remove(roomView.getID());

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

import java.net.URI;
import java.net.URISyntaxException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.core.runtime.Path;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerInstantiationException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.presence.IInvitationListener;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceContainer;
import org.eclipse.ecf.presence.IPresenceListener;
import org.eclipse.ecf.presence.IRosterEntry;
import org.eclipse.ecf.presence.IRosterGroup;
import org.eclipse.ecf.presence.chat.IChatMessageSender;
import org.eclipse.ecf.presence.chat.IChatParticipantListener;
import org.eclipse.ecf.presence.chat.IChatRoomContainer;
import org.eclipse.ecf.presence.chat.IChatRoomManager;
import org.eclipse.ecf.presence.chat.IRoomInfo;
import org.eclipse.ecf.presence.impl.RosterEntry;
import org.eclipse.ecf.ui.UiPlugin;
import org.eclipse.ecf.ui.UiPluginConstants;
import org.eclipse.ecf.ui.dialogs.AddBuddyDialog;
import org.eclipse.ecf.ui.dialogs.ChatRoomSelectionDialog;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.resource.ImageRegistry;
import org.eclipse.jface.viewers.DoubleClickEvent;
import org.eclipse.jface.viewers.IDoubleClickListener;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerSorter;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchActionConstants;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

public class RosterView extends ViewPart implements IChatRoomViewCloseListener {
	private static final String CHAT_ROOM_VIEW_CLASS = "org.eclipse.ecf.ui.views.ChatRoomView";
	public static final String DISCONNECT_ICON_DISABLED = "icons/disabled/terminate_co.gif";
	public static final String DISCONNECT_ICON_ENABLED = "icons/enabled/terminate_co.gif";
	public static final String INSTANT_MESSAGE_ICON = "icons/enabled/message.gif";
	public static final String ADDGROUP_ICON = "icons/enabled/addgroup.gif";
	public static final String ADDBUDDY_ICON = "icons/enabled/addbuddy.gif";
	public static final String ADDCHAT_ICON = "icons/enabled/addchat.gif";
	public static final String UNFILED_GROUP_NAME = "Buddies";
	protected static final int TREE_EXPANSION_LEVELS = 2;
	private TreeViewer viewer;
	// private Action chatAction;
	private Action selectedChatAction;
	private Action selectedDoubleClickAction;
	private Action disconnectAction;
	private Action openChatRoomAction;
	// private Action addGroupAction;
	// private Action addBuddyAction;
	protected Hashtable chatThreads = new Hashtable();
	protected Hashtable accounts = new Hashtable();
	protected Hashtable chatRooms = new Hashtable();
	protected void addAccount(UserAccount account) {
		if (account == null)
			return;
		accounts.put(account.getServiceID(), account);
	}
	protected UserAccount getAccount(ID serviceID) {
		return (UserAccount) accounts.get(serviceID);
	}
	protected void removeAccount(ID serviceID) {
		accounts.remove(serviceID);
	}
	class UserAccount {
		ID serviceID;
		IUser user;
		ILocalInputHandler inputHandler;
		IPresenceContainer container;
		public UserAccount(ID serviceID, IUser user,
				ILocalInputHandler handler, IPresenceContainer container) {
			this.serviceID = serviceID;
			this.user = user;
			this.inputHandler = handler;
			this.container = container;
		}
		public ID getServiceID() {
			return serviceID;
		}
		public IUser getUser() {
			return user;
		}
		public ILocalInputHandler getInputHandler() {
			return inputHandler;
		}
		public IPresenceContainer getContainer() {
			return container;
		}
	}
	protected String getUserNameFromID(ID userID) {
		if (userID == null)
			return "";
		String uname = userID.getName();
		int index = uname.indexOf("@");
		String username = uname;
		if (index >= 0) {
			username = uname.substring(0, index);
		}
		if (username.equals("")) {
			return uname;
		} else
			return username;
	}
	public void dispose() {
		for (Iterator i = accounts.keySet().iterator(); i.hasNext();) {
			ID serviceID = (ID) i.next();
			UserAccount account = getAccount(serviceID);
			if (account != null) {
				ILocalInputHandler handler = account.getInputHandler();
				if (handler != null) {
					handler.disconnect();
				}
			}
		}
		accounts.clear();
		super.dispose();
	}
	class TreeObject implements IAdaptable {
		private String name;
		private TreeParent parent;
		private ID userID;
		public TreeObject(String name, ID userID) {
			this.name = name;
			this.userID = userID;
		}
		public TreeObject(String name) {
			this(name, null);
		}
		public String getName() {
			return name;
		}
		public void setName(String name) {
			this.name = name;
		}
		public ID getUserID() {
			return userID;
		}
		public void setParent(TreeParent parent) {
			this.parent = parent;
		}
		public TreeParent getParent() {
			return parent;
		}
		public String toString() {
			return getName();
		}
		public Object getAdapter(Class key) {
			return null;
		}
	}
	class TreeParent extends TreeObject {
		private ArrayList children;
		public TreeParent(String name) {
			super(name);
			children = new ArrayList();
		}
		public TreeParent(String name, ID userID) {
			super(name, userID);
			children = new ArrayList();
		}
		public void addChild(TreeObject child) {
			children.add(child);
			child.setParent(this);
		}
		public void removeChild(TreeObject child) {
			children.remove(child);
			child.setParent(null);
		}
		public void removeChildren() {
			for (Iterator i = children.iterator(); i.hasNext();) {
				TreeObject obj = (TreeObject) i.next();
				obj.setParent(null);
			}
			children.clear();
		}
		public TreeObject[] getChildren() {
			return (TreeObject[]) children.toArray(new TreeObject[children
					.size()]);
		}
		public boolean hasChildren() {
			return children.size() > 0;
		}
	}
	class TreeGroup extends TreeParent {
		ID svcID;
		public TreeGroup(ID svcID, String name) {
			super(name);
			this.svcID = svcID;
		}
		public int getActiveCount() {
			TreeObject[] childs = getChildren();
			int totCount = 0;
			for (int i = 0; i < childs.length; i++) {
				if (childs[i] instanceof TreeBuddy) {
					TreeBuddy tb = (TreeBuddy) childs[i];
					if (tb.isActive()) {
						totCount++;
					}
				}
			}
			return totCount;
		}
		public int getTotalCount() {
			return getChildren().length;
		}
		public ID getServiceID() {
			return svcID;
		}
	}
	class TreeBuddy extends TreeParent {
		IPresence presence = null;
		ID svcID = null;
		public TreeBuddy(ID svcID, String name, ID id, IPresence p) {
			super(name, id);
			this.svcID = svcID;
			this.presence = p;
		}
		public IPresence getPresence() {
			return presence;
		}
		public void setPresence(IPresence p) {
			this.presence = p;
		}
		public ID getServiceID() {
			return svcID;
		}
		public boolean isActive() {
			IPresence p = getPresence();
			if (p == null)
				return false;
			return presence.getType().equals(IPresence.Type.AVAILABLE);
		}
	}
	class ViewContentProvider implements IStructuredContentProvider,
			ITreeContentProvider {
		private TreeParent invisibleRoot;
		private TreeParent root;
		public void inputChanged(Viewer v, Object oldInput, Object newInput) {
		}
		public void dispose() {
		}
		public TreeBuddy findBuddyWithUserID(ID userID) {
			return findBuddy(root, userID);
		}
		public Object[] getElements(Object parent) {
			if (parent.equals(getViewSite())) {
				if (root == null)
					initialize();
				return getChildren(root);
			}
			return getChildren(parent);
		}
		public Object getParent(Object child) {
			if (child instanceof TreeObject) {
				return ((TreeObject) child).getParent();
			}
			return null;
		}
		public Object[] getChildren(Object parent) {
			if (parent instanceof TreeParent) {
				return ((TreeParent) parent).getChildren();
			}
			return new Object[0];
		}
		public boolean hasChildren(Object parent) {
			if (parent instanceof TreeParent)
				return ((TreeParent) parent).hasChildren();
			return false;
		}
		public TreeBuddy fillPresence(TreeBuddy obj, IPresence presence) {
			obj.setPresence(presence);
			obj.removeChildren();
			obj.addChild(new TreeObject("Account: "
					+ obj.getServiceID().getName()));
			TreeObject type = new TreeObject("Status: "
					+ presence.getType().toString());
			obj.addChild(type);
			String status = presence.getStatus();
			if (status != null && !status.equals("")) {
				TreeObject stat = new TreeObject("Details: " + status);
				obj.addChild(stat);
			}
			Map props = presence.getProperties();
			for (Iterator i = props.keySet().iterator(); i.hasNext();) {
				String key = (String) i.next();
				String value = (String) props.get(key);
				if (key != null && value != null) {
					TreeObject prop = new TreeObject(key + ": " + value);
					obj.addChild(prop);
				}
			}
			return obj;
		}
		public TreeBuddy createBuddy(TreeBuddy oldBuddy, IRosterEntry entry) {
			String name = entry.getName();
			if (name == null)
				name = getUserNameFromID(entry.getUserID());
			IPresence presence = entry.getPresenceState();
			TreeBuddy newBuddy = null;
			if (oldBuddy == null)
				newBuddy = new TreeBuddy(entry.getServiceID(), name, entry
						.getUserID(), presence);
			else {
				newBuddy = oldBuddy;
				if (entry.getName() != null)
					newBuddy.setName(entry.getName());
			}
			if (presence != null)
				fillPresence(newBuddy, presence);
			else if (oldBuddy == null)
				newBuddy.addChild(new TreeObject("Account: "
						+ newBuddy.getServiceID().getName()));
			return newBuddy;
		}
		public TreeGroup findGroup(TreeParent parent, String name) {
			TreeObject[] objs = parent.getChildren();
			if (objs != null) {
				for (int i = 0; i < objs.length; i++) {
					if (objs[i].getName().equals(name)) {
						return (TreeGroup) objs[i];
					}
				}
			}
			return null;
		}
		public String[] getAllGroupNames() {
			TreeObject[] objs = root.getChildren();
			if (objs != null) {
				List l = new ArrayList();
				for (int i = 0; i < objs.length; i++) {
					TreeObject o = objs[i];
					if (o instanceof TreeGroup) {
						l.add(((TreeGroup) o).getName());
					}
				}
				return (String[]) l.toArray(new String[] {});
			} else
				return new String[0];
		}
		public TreeBuddy findBuddy(TreeParent parent, IRosterEntry entry) {
			return findBuddy(parent, entry.getUserID());
		}
		public TreeBuddy findBuddy(TreeParent parent, ID entryID) {
			TreeObject[] objs = parent.getChildren();
			if (objs == null)
				return null;
			for (int i = 0; i < objs.length; i++) {
				if (objs[i] instanceof TreeBuddy) {
					TreeBuddy tb = (TreeBuddy) objs[i];
					ID tbid = tb.getUserID();
					if (tbid != null && tbid.equals(entryID)) {
						return (TreeBuddy) objs[i];
					}
				} else if (objs[i] instanceof TreeGroup) {
					TreeBuddy found = findBuddy((TreeParent) objs[i], entryID);
					if (found != null)
						return found;
				}
			}
			return null;
		}
		public void addEntry(TreeParent parent, IRosterEntry entry) {
			TreeBuddy tb = findBuddy(parent, entry);
			TreeBuddy newBuddy = createBuddy(tb, entry);
			// If buddy found already, then remove old and add new
			if (tb != null) {
				TreeParent tbparent = tb.getParent();
				tbparent.removeChild(tb);
				tbparent.addChild(newBuddy);
			}
			TreeParent buddyParent = newBuddy.getParent();
			if (buddyParent == null) {
				// Existing group not found, so see if entry has a group
				// associated with it
				Iterator groups = entry.getGroups();
				if (groups.hasNext()) {
					// There's a group associated with entry...so add with group
					// name
					String groupName = ((IRosterGroup) groups.next()).getName();
					TreeGroup oldgrp = findGroup(parent, groupName);
					if (oldgrp != null) {
						oldgrp.addChild(newBuddy);
					} else {
						TreeGroup newgrp = new TreeGroup(entry.getServiceID(),
								groupName);
						newgrp.addChild(newBuddy);
						parent.addChild(newgrp);
					}
				} else {
					TreeGroup tg = findGroup(parent, UNFILED_GROUP_NAME);
					if (tg == null) {
						tg = new TreeGroup(entry.getServiceID(),
								UNFILED_GROUP_NAME);
						tg.addChild(newBuddy);
						parent.addChild(tg);
					} else {
						tg.addChild(newBuddy);
					}
				}
			}
		}
		public void replaceEntry(TreeParent parent, IRosterEntry entry) {
			TreeBuddy tb = findBuddy(parent, entry);
			// If entry already in tree, remove it from current position
			if (tb != null) {
				TreeParent tp = (TreeParent) tb.getParent();
				if (tp != null) {
					tp.removeChild(tb);
					if (tp.getName().equals(UNFILED_GROUP_NAME)) {
						if (!tp.hasChildren()) {
							TreeParent tpp = tp.getParent();
							tpp.removeChild(tp);
						}
					}
				}
			}
			// Create new buddy
			TreeBuddy newBuddy = createBuddy(tb, entry);
			Iterator groups = entry.getGroups();
			if (groups.hasNext()) {
				// There's a group associated with entry...so add with group
				// name
				String groupName = ((IRosterGroup) groups.next()).getName();
				TreeGroup oldgrp = findGroup(parent, groupName);
				if (oldgrp != null) {
					oldgrp.addChild(newBuddy);
				} else {
					TreeGroup newgrp = new TreeGroup(entry.getServiceID(),
							groupName);
					newgrp.addChild(newBuddy);
					parent.addChild(newgrp);
				}
			} else {
				TreeGroup tg = findGroup(parent, UNFILED_GROUP_NAME);
				if (tg == null) {
					tg = new TreeGroup(entry.getServiceID(), UNFILED_GROUP_NAME);
					tg.addChild(newBuddy);
					parent.addChild(tg);
				} else {
					tg.addChild(newBuddy);
				}
			}
		}
		public void addGroup(ID svcID, String name) {
			if (name == null)
				return;
			addGroup(svcID, root, name);
		}
		public void addGroup(ID svcID, TreeParent parent, String name) {
			TreeGroup oldgrp = findGroup(parent, name);
			if (oldgrp != null) {
				// If the name is already there, then skip
				return;
			}
			// Group not there...add it
			TreeGroup newgrp = new TreeGroup(svcID, name);
			parent.addChild(newgrp);
		}
		public void removeGroup(TreeParent parent, String name) {
			TreeGroup oldgrp = findGroup(parent, name);
			if (oldgrp == null) {
				// if not there, simply return
				return;
			}
			// Else it is there...and we remove it
			parent.removeChild(oldgrp);
		}
		public void removeGroup(String name) {
			if (name == null)
				return;
			removeGroup(root, name);
		}
		public void addEntry(IRosterEntry entry) {
			addEntry(root, entry);
		}
		public void replaceEntry(IRosterEntry entry) {
			replaceEntry(root, entry);
		}
		public void removeRosterEntry(ID entry) {
			removeEntry(root, entry);
		}
		public void removeEntry(TreeParent parent, ID entry) {
			TreeBuddy buddy = findBuddy(parent, entry);
			if (buddy == null)
				return;
			TreeParent p = buddy.getParent();
			if (p != null) {
				p.removeChild(buddy);
				refreshView();
			}
		}
		protected void removeChildren(TreeParent parent, ID svcID) {
			TreeObject[] childs = parent.getChildren();
			for (int i = 0; i < childs.length; i++) {
				if (childs[i] instanceof TreeParent) {
					removeChildren((TreeParent) childs[i], svcID);
				}
				if (childs[i] instanceof TreeBuddy) {
					TreeBuddy tb = (TreeBuddy) childs[i];
					ID id = tb.getServiceID();
					if (id.equals(svcID)) {
						parent.removeChild(tb);
					}
				} else if (childs[i] instanceof TreeGroup) {
					TreeGroup tg = (TreeGroup) childs[i];
					ID id = tg.getServiceID();
					if (id.equals(svcID)) {
						parent.removeChild(tg);
					}
				}
			}
		}
		public void removeAllEntriesForAccount(UserAccount account) {
			if (account == null) {
				root = null;
			} else {
				removeChildren(root, account.getServiceID());
			}
		}
		private void initialize() {
			root = new TreeParent("Buddy List");
			invisibleRoot = new TreeParent("");
			invisibleRoot.addChild(root);
		}
	}
	class ViewLabelProvider extends LabelProvider {
		public String getText(Object obj) {
			String label = null;
			if (obj instanceof TreeGroup) {
				TreeGroup tg = (TreeGroup) obj;
				label = tg.getName() + " (" + tg.getActiveCount() + "/"
						+ tg.getTotalCount() + ")";
				return label;
			} else
				return obj.toString();
		}
		public Image getImage(Object obj) {
			Image image = null; // By default, no image exists for obj, but if
			// found to be a specific instance, load from
			// plugin repository.
			if (obj instanceof TreeBuddy) {
				ImageRegistry registry = UiPlugin.getDefault()
						.getImageRegistry();
				TreeBuddy o = (TreeBuddy) obj;
				if (o.getUserID() != null) {
					if (o.isActive()) {
						image = registry.get(UiPluginConstants.DECORATION_USER);
					} else {
						image = registry
								.get(UiPluginConstants.DECORATION_USER_INACTIVE);
					}
				}
			} else if (obj instanceof TreeGroup) {
				image = PlatformUI.getWorkbench().getSharedImages().getImage(
						ISharedImages.IMG_OBJ_ELEMENT);
			}
			return image;
		}
	}
	class NameSorter extends ViewerSorter {
	}
	public RosterView() {
	}
	protected void refreshView() {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					viewer.refresh();
					expandAll();
				} catch (Exception e) {
				}
			}
		});
	}
	protected void expandAll() {
		viewer.expandToLevel(TREE_EXPANSION_LEVELS);
	}
	public void createPartControl(Composite parent) {
		viewer = new TreeViewer(parent, SWT.MULTI | SWT.H_SCROLL | SWT.V_SCROLL);
		viewer.setContentProvider(new ViewContentProvider());
		viewer.setLabelProvider(new ViewLabelProvider());
		viewer.setSorter(new NameSorter());
		viewer.setInput(getViewSite());
		viewer.setAutoExpandLevel(3);
		makeActions();
		hookContextMenu();
		hookDoubleClickAction();
		contributeToActionBars();
	}
	private void hookContextMenu() {
		MenuManager menuMgr = new MenuManager("#PopupMenu");
		menuMgr.setRemoveAllWhenShown(true);
		menuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {
				RosterView.this.fillContextMenu(manager);
			}
		});
		Menu menu = menuMgr.createContextMenu(viewer.getControl());
		viewer.getControl().setMenu(menu);
		getSite().registerContextMenu(menuMgr, viewer);
	}
	private void contributeToActionBars() {
		IActionBars bars = getViewSite().getActionBars();
		fillLocalPullDown(bars.getMenuManager());
		fillLocalToolBar(bars.getToolBarManager());
	}
	private void fillLocalPullDown(IMenuManager manager) {
		manager.add(disconnectAction);
		manager.add(openChatRoomAction);
	}
	private void fillContextMenu(IMenuManager manager) {
		final TreeObject treeObject = getSelectedTreeObject();
		final ID targetID = treeObject.getUserID();
		if (treeObject != null) {
			if (treeObject instanceof TreeBuddy) {
				final TreeBuddy tb = (TreeBuddy) treeObject;
				selectedChatAction = new Action() {
					public void run() {
						openChatWindowForTarget(targetID);
					}
				};
				selectedChatAction.setText("Send IM to "
						+ treeObject.getUserID().getName());
				selectedChatAction.setImageDescriptor(ImageDescriptor
						.createFromURL(UiPlugin.getDefault().find(
								new Path(INSTANT_MESSAGE_ICON))));
				manager.add(selectedChatAction);
				TreeObject parent = treeObject.getParent();
				TreeGroup tg = null;
				if (parent != null && parent instanceof TreeGroup) {
					tg = (TreeGroup) parent;
				}
				final TreeGroup treeGroup = tg;
				Action removeUserAction = new Action() {
					public void run() {
						removeUserFromGroup(tb, treeGroup);
					}
				};
				if (treeGroup != null) {
					removeUserAction.setText("Remove " + treeObject.getName()
							+ " from " + treeGroup.getName() + " group");
				} else {
					removeUserAction.setText("Remove " + treeObject.getName());
				}
				removeUserAction.setImageDescriptor(PlatformUI.getWorkbench()
						.getSharedImages().getImageDescriptor(
								ISharedImages.IMG_TOOL_DELETE));
				manager.add(removeUserAction);
			} else if (treeObject instanceof TreeGroup) {
				final TreeGroup treeGroup = (TreeGroup) treeObject;
				final String groupName = treeGroup.getName();
				Action removeGroupAction = new Action() {
					public void run() {
						removeGroup(groupName);
					}
				};
				String accountName = treeGroup.getServiceID().getName();
				removeGroupAction.setText("Remove " + treeObject.getName()
						+ " for account " + accountName);
				removeGroupAction.setEnabled(treeGroup.getTotalCount() == 0);
				removeGroupAction.setImageDescriptor(PlatformUI.getWorkbench()
						.getSharedImages().getImageDescriptor(
								ISharedImages.IMG_TOOL_DELETE));
				if (removeGroupAction.isEnabled())
					manager.add(removeGroupAction);
			}
		}
		manager.add(new Separator());
		// Other plug-ins can contribute there actions here
		manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));
	}
	protected void openDialogAndSendRequest(ID svcID, String name,
			String groupName) {
		String[] groupNames = this.getGroupNames();
		List g = Arrays.asList(groupNames);
		int selected = (groupName == null) ? -1 : g.indexOf(groupName);
		AddBuddyDialog sg = new AddBuddyDialog(viewer.getControl().getShell(),
				name, groupNames, selected);
		sg.open();
		if (sg.getResult() == Window.OK) {
			String group = sg.getGroup();
			String user = sg.getUser();
			String nickname = sg.getNickname();
			sg.close();
			if (!Arrays.asList(groupNames).contains(group)) {
				// create group with name
				this.addGroup(svcID, group);
			}
			String[] sendGroups = new String[] { group };
			// Finally, send the information and request subscription
			UserAccount account = getAccount(svcID);
			ILocalInputHandler inputHandler = account.getInputHandler();
			inputHandler.sendRosterAdd(user, nickname, sendGroups);
		}
	}
	protected void requestAuthFrom(TreeBuddy buddy, TreeGroup tg) {
		if (buddy == null)
			return;
		ID buddyID = buddy.getUserID();
		String name = buddyID.getName();
		String groupName = (tg == null) ? null : tg.getName();
		openDialogAndSendRequest(buddy.getServiceID(), name, groupName);
	}
	protected void addUserToGroup(ID serviceID, String groupName) {
		openDialogAndSendRequest(serviceID, null, groupName);
	}
	protected void removeUserFromGroup(TreeBuddy buddy, TreeGroup group) {
		UserAccount account = getAccount(buddy.getServiceID());
		if (account != null) {
			ILocalInputHandler handler = account.getInputHandler();
			handler.sendRosterRemove(buddy.getUserID());
		}
	}
	protected TreeObject getSelectedTreeObject() {
		ISelection selection = viewer.getSelection();
		Object obj = ((IStructuredSelection) selection).getFirstElement();
		TreeObject treeObject = (TreeObject) obj;
		return treeObject;
	}
	private void fillLocalToolBar(IToolBarManager manager) {
		manager.add(disconnectAction);
		manager.add(new Separator());
		manager.add(openChatRoomAction);
	}
	protected ID inputIMTarget() {
		InputDialog dlg = new InputDialog(getSite().getShell(), "Send IM",
				"Please enter the XMPP ID of the person you would like to IM",
				"", null);
		dlg.setBlockOnOpen(true);
		int res = dlg.open();
		if (res == InputDialog.OK) {
			String strres = dlg.getValue();
			if (strres != null && !strres.equals("")) {
				ID target = null;
				try {
					target = IDFactory.getDefault().makeStringID(strres);
				} catch (Exception e) {
					MessageDialog.openError(getSite().getShell(), "Error",
							"Error in IM target");
					return null;
				}
				return target;
			}
		}
		return null;
	}
	class RoomWithAView {
		IChatRoomContainer container;
		ChatRoomView view;
		String secondaryID;
		IChatRoomManager manager;
		RoomWithAView(IChatRoomManager manager, IChatRoomContainer container,
				ChatRoomView view, String secondaryID) {
			this.manager = manager;
			this.container = container;
			this.view = view;
			this.secondaryID = secondaryID;
		}
		public IChatRoomManager getManager() {
			return manager;
		}
		public IChatRoomContainer getContainer() {
			return container;
		}
		public ChatRoomView getView() {
			return view;
		}
		public String getID() {
			return secondaryID;
		}
	}
	private String getChatRoomSecondaryID(ID roomID) {
		try {
			URI aURI = roomID.toURI();
			String auth = aURI.getAuthority();
			String path = aURI.getPath();
			return auth + path;
		} catch (URISyntaxException e) {
			return null;
		}
	}
	private void makeActions() {
		selectedDoubleClickAction = new Action() {
			public void run() {
				TreeObject treeObject = getSelectedTreeObject();
				final ID targetID = treeObject.getUserID();
				if (targetID != null)
					openChatWindowForTarget(targetID);
			}
		};
		disconnectAction = new Action() {
			public void run() {
				// Disconnect all accounts
				for (Iterator i = accounts.entrySet().iterator(); i.hasNext();) {
					Map.Entry entry = (Map.Entry) i.next();
					UserAccount account = (UserAccount) entry.getValue();
					account.getInputHandler().disconnect();
				}
				setToolbarEnabled(false);
				this.setEnabled(false);
			}
		};
		disconnectAction.setText("Disconnect");
		disconnectAction.setToolTipText("Disconnect from servers.");
		disconnectAction.setEnabled(false);
		disconnectAction.setImageDescriptor(ImageDescriptor
				.createFromURL(UiPlugin.getDefault().find(
						new Path(DISCONNECT_ICON_ENABLED))));
		disconnectAction.setDisabledImageDescriptor(ImageDescriptor
				.createFromURL(UiPlugin.getDefault().find(
						new Path(DISCONNECT_ICON_DISABLED))));
		openChatRoomAction = new Action() {
			public void run() {
				// Get managers for all accounts currently connected to
				IChatRoomManager managers[] = new IChatRoomManager[accounts
						.size()];
				int j = 0;
				for (Iterator i = accounts.values().iterator(); i.hasNext();) {
					UserAccount ua = (UserAccount) i.next();
					managers[j++] = ua.getContainer().getChatRoomManager();
				}
				// Create chat room selection dialog with managers, open
				ChatRoomSelectionDialog dialog = new ChatRoomSelectionDialog(
						RosterView.this.getViewSite().getShell(), managers);
				dialog.setBlockOnOpen(true);
				dialog.open();
				// If selection cancelled then simply return
				if (dialog.getReturnCode() != Window.OK) {
					return;
				}
				// Get selected room, selected manager, and selected IRoomInfo
				ChatRoomSelectionDialog.Room room = dialog.getSelectedRoom();
				IChatRoomManager selectedManager = room.getManager();
				IRoomInfo selectedInfo = room.getRoomInfo();
				// If they are null then we can't proceed
				if (room == null || selectedManager == null
						|| selectedInfo == null) {
					MessageDialog.openInformation(RosterView.this.getViewSite()
							.getShell(), "No room selected",
							"Cannot connect to null room");
					return;
				}
				// Now get the secondary ID from the selected room id
				String secondaryID = getChatRoomSecondaryID(selectedInfo
						.getRoomID());
				if (secondaryID == null) {
					MessageDialog.openError(RosterView.this.getViewSite()
							.getShell(), "Could not get identifier for room",
							"Could not get proper identifier for chat room "
									+ selectedInfo.getRoomID());
					return;
				}
				// Check to make sure that we are not already connected to the
				// selected room.
				// If we are simply activate the existing view for the room and
				// done
				IWorkbenchWindow ww = PlatformUI.getWorkbench()
						.getActiveWorkbenchWindow();
				IWorkbenchPage wp = ww.getActivePage();
				RoomWithAView roomView = getRoomView(secondaryID);
				if (roomView != null) {
					// We've already connected to this room
					// So just show it.
					ChatRoomView view = roomView.getView();
					wp.activate(view);
					return;
				}
				// If we don't already have a connection/view to this room then
				// now, create chat room instance
				IChatRoomContainer chatRoom = null;
				try {
					chatRoom = selectedManager.makeChatRoomContainer();
				} catch (ContainerInstantiationException e1) {
					MessageDialog.openError(RosterView.this.getViewSite()
							.getShell(), "Could not create chat room",
							"Could not create chat room for account");
				}
				// Get the chat message sender callback so that we can send
				// messages to chat room
				IChatMessageSender sender = chatRoom.getChatMessageSender();
				IViewPart view = null;
				try {
					IViewReference ref = wp.findViewReference(
							CHAT_ROOM_VIEW_CLASS, secondaryID);
					if (ref == null) {
						view = wp.showView(CHAT_ROOM_VIEW_CLASS, secondaryID,
								IWorkbenchPage.VIEW_ACTIVATE);
					} else {
						view = ref.getView(true);
					}
					final ChatRoomView chatroomview = (ChatRoomView) view;
					// initialize the chatroomview with the necessary
					// information
					chatroomview.initialize(RosterView.this, secondaryID,
							chatRoom, selectedInfo, sender);
					// Add listeners so that the new chat room gets
					// asynch notifications of various relevant chat room events
					chatRoom.addMessageListener(new IMessageListener() {
						public void handleMessage(ID fromID, ID toID,
								Type type, String subject, String messageBody) {
							chatroomview.handleMessage(fromID, toID, type,
									subject, messageBody);
						}
					});
					chatRoom
							.addChatParticipantListener(new IChatParticipantListener() {
								public void handlePresence(ID fromID,
										IPresence presence) {
									chatroomview.handlePresence(fromID,
											presence);
								}
								public void joined(ID user) {
									chatroomview.handleJoin(user);
								}
								public void left(ID user) {
									chatroomview.handleLeave(user);
								}
							});
					chatRoom.addInvitationListener(new IInvitationListener() {
						public void handleInvitationReceived(ID roomID,
								ID from, ID toID, String subject, String body) {
							chatroomview.handleInvitationReceived(roomID, from,
									toID, subject, body);
						}
					});
				} catch (PartInitException e) {
					UiPlugin.log(
							"Exception in chat room view initialization for chat room "
									+ selectedInfo.getRoomID(), e);
					MessageDialog.openError(getViewSite().getShell(),
							"Can't initialize chat room view",
							"Unexpected error initializing for chat room: "
									+ selectedInfo.getName()
									+ ".  Please see Error Log for details");
					return;
				}
				// Now actually connect to chatroom
				try {
					chatRoom.connect(selectedInfo.getRoomID(), null);
				} catch (ContainerConnectException e1) {
					UiPlugin.log("Exception connecting to chat room "
							+ selectedInfo.getRoomID(), e1);
					MessageDialog.openError(RosterView.this.getViewSite()
							.getShell(), "Could not connect",
							"Cannot connect to chat room "
									+ selectedInfo.getName() + ", message: "
									+ e1.getMessage());
					return;
				}
				// If connect successful...we create a room with a view and add
				// it to our known set
				addRoomView(new RoomWithAView(selectedManager, chatRoom,
						(ChatRoomView) view, secondaryID));
			}
		};
		openChatRoomAction.setText("Enter Chatroom");
		openChatRoomAction.setToolTipText("Enter a chatroom");
		openChatRoomAction.setImageDescriptor(ImageDescriptor
				.createFromURL(UiPlugin.getDefault().find(
						new Path(ADDCHAT_ICON))));
		openChatRoomAction.setEnabled(false);
	}
	protected void addRoomView(RoomWithAView roomView) {
		chatRooms.put(roomView.getID(), roomView);
	}
	protected void removeRoomView(RoomWithAView roomView) {
		chatRooms.remove(roomView);
	}
	protected RoomWithAView getRoomView(String id) {
		return (RoomWithAView) chatRooms.get(id);
	}
	protected ChatWindow openChatWindowForTarget(ID targetID) {
		if (targetID == null)
			return null;
		ChatWindow window = null;
		synchronized (chatThreads) {
			window = (ChatWindow) chatThreads.get(targetID);
			if (window == null) {
				window = makeChatWindowForTarget(targetID);
				if (window != null)
					window.open();
			} else {
				if (!window.hasFocus()) {
					window.openAndFlash();
				}
			}
			if (window != null)
				window.setStatus("chat with " + targetID.getName());
		}
		return window;
	}
	protected ChatWindow makeChatWindowForTarget(ID targetID) {
		UserAccount account = getAccountForUser(targetID);
		if (account == null)
			return null;
		ChatWindow window = new ChatWindow(RosterView.this, targetID.getName(),
				getWindowInitText(targetID), account.getUser(), new User(
						targetID));
		window.create();
		chatThreads.put(targetID, window);
		return window;
	}
	private void hookDoubleClickAction() {
		viewer.addDoubleClickListener(new IDoubleClickListener() {
			public void doubleClick(DoubleClickEvent event) {
				selectedDoubleClickAction.run();
			}
		});
	}
	/**
	 * Passing the focus request to the viewer's control.
	 */
	public void setFocus() {
		viewer.getControl().setFocus();
	}
	public void handleRosterEntry(ID groupID, IRosterEntry entry) {
		if (entry == null)
			return;
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			if (entry.getInterestType() == IRosterEntry.InterestType.REMOVE
					|| entry.getInterestType() == IRosterEntry.InterestType.NONE) {
				vcp.removeRosterEntry(entry.getUserID());
			} else
				vcp.addEntry(entry);
			refreshView();
		}
	}
	public void handlePresence(ID groupID, ID userID, IPresence presence) {
		IRosterEntry entry = new RosterEntry(groupID, userID, null, presence);
		handleRosterEntry(groupID, entry);
	}
	protected UserAccount getAccountForUser(ID userID) {
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp == null)
			return null;
		TreeBuddy buddy = vcp.findBuddyWithUserID(userID);
		if (buddy == null)
			return null;
		UserAccount account = getAccount(buddy.getServiceID());
		return account;
	}
	protected ILocalInputHandler getHandlerForUser(ID userID) {
		UserAccount account = getAccountForUser(userID);
		if (account == null)
			return null;
		else
			return account.getInputHandler();
	}
	public Object getAdapter(Class clazz) {
		if (clazz != null && clazz.equals(ILocalInputHandler.class)) {
			return new ILocalInputHandler() {
				public void inputText(ID userID, String text) {
					ILocalInputHandler inputHandler = getHandlerForUser(userID);
					if (inputHandler != null) {
						inputHandler.inputText(userID, text);
					} else
						System.err.println("handleTextLine(" + text + ")");
				}
				public void startTyping(ID userID) {
					ILocalInputHandler inputHandler = getHandlerForUser(userID);
					if (inputHandler != null) {
						inputHandler.startTyping(userID);
					} else
						System.err.println("handleStartTyping()");
				}
				public void disconnect() {
					disconnect();
				}
				public void updatePresence(ID userID, IPresence presence) {
					ILocalInputHandler inputHandler = getHandlerForUser(userID);
					if (inputHandler != null) {
						inputHandler.updatePresence(userID, presence);
					} else
						System.err.println("updatePresence(" + userID + ","
								+ presence + ")");
				}
				public void sendRosterAdd(String user, String name,
						String[] groups) {
				}
				public void sendRosterRemove(ID userID) {
					ILocalInputHandler inputHandler = getHandlerForUser(userID);
					if (inputHandler != null) {
						inputHandler.sendRosterRemove(userID);
					} else
						System.err.println("sendRosterRemove()");
				}
			};
		} else if (clazz.equals(IPresenceListener.class)) {
			return this;
		} else if (clazz.equals(IMessageListener.class)) {
			return this;
		} else
			return null;
	}
	protected String getWindowInitText(ID targetID) {
		String result = "chat with " + targetID.getName() + " started "
				+ getDateAndTime() + "\n\n";
		return result;
	}
	protected String getDateAndTime() {
		SimpleDateFormat sdf = new SimpleDateFormat("MM:dd hh:mm:ss");
		return sdf.format(new Date());
	}
	public void handleMessage(ID groupID, ID fromID, ID toID,
			IMessageListener.Type type, String subject, String message) {
		ChatWindow window = openChatWindowForTarget(fromID);
		// finally, show message
		if (window != null) {
			window.handleMessage(fromID, toID, type, subject, message);
			window.setStatus("last message received at "
					+ (new SimpleDateFormat("hh:mm:ss").format(new Date())));
		}
	}
	public void addAccount(ID account, IUser user, ILocalInputHandler handler,
			IPresenceContainer container) {
		if (account != null) {
			addAccount(new UserAccount(account, user, handler, container));
			setToolbarEnabled(true);
		}
	}
	protected void setToolbarEnabled(boolean enabled) {
		disconnectAction.setEnabled(enabled);
		openChatRoomAction.setEnabled(enabled);
	}
	public void accountDeparted(ID serviceID) {
		UserAccount account = getAccount(serviceID);
		if (account != null) {
			handleAccountDeparted(account);
		}
	}
	protected void disposeAllChatWindowsForAccount(UserAccount account,
			String status) {
		synchronized (chatThreads) {
			for (Iterator i = chatThreads.values().iterator(); i.hasNext();) {
				ChatWindow window = (ChatWindow) i.next();
				ID userID = window.getLocalUser().getID();
				UserAccount userAccount = getAccountForUser(userID);
				if (userAccount != null) {
					if (userAccount.getServiceID().equals(
							account.getServiceID())) {
						window.setDisposed(status);
						i.remove();
					}
				}
			}
		}
	}
	protected void removeAllRosterEntriesForAccount(UserAccount account) {
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.removeAllEntriesForAccount(account);
			refreshView();
		}
	}
	public String[] getGroupNames() {
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			return vcp.getAllGroupNames();
		} else
			return new String[0];
	}
	public String getSelectedGroupName() {
		TreeObject to = getSelectedTreeObject();
		if (to == null)
			return null;
		if (to instanceof TreeGroup) {
			TreeGroup tg = (TreeGroup) to;
			return tg.getName();
		}
		return null;
	}
	public void addGroup(ID svcID, String name) {
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.addGroup(svcID, name);
			refreshView();
		}
	}
	public void removeGroup(String name) {
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.removeGroup(name);
			refreshView();
		}
	}
	public void removeRosterEntry(ID id) {
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.removeRosterEntry(id);
			refreshView();
		}
	}
	protected void handleAccountDeparted(UserAccount account) {
		removeAllRosterEntriesForAccount(account);
		disposeAllChatWindowsForAccount(account,
				"Disconnected from server.  Chat is inactive");
		accounts.remove(account.getServiceID());
		if (accounts.size() == 0)
			setToolbarEnabled(false);
	}
	public void handleSetRosterEntry(ID groupID, IRosterEntry entry) {
		if (entry == null)
			return;
		ViewContentProvider vcp = (ViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			if (entry.getInterestType() == IRosterEntry.InterestType.REMOVE
					|| entry.getInterestType() == IRosterEntry.InterestType.NONE) {
				vcp.removeRosterEntry(entry.getUserID());
			} else
				vcp.replaceEntry(entry);
			refreshView();
		}
	}
	public void chatRoomViewClosing(String secondaryID) {
		RoomWithAView roomView = (RoomWithAView) chatRooms.get(secondaryID);
		if (roomView != null) {
			IChatRoomContainer container = roomView.getContainer();
			container.dispose();
			removeRoomView(roomView);
		}
	}
}
 No newline at end of file