public void accountDisconnected(ID serviceID) {

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

import java.io.IOException;
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

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.security.Callback;
import org.eclipse.ecf.core.security.CallbackHandler;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.security.NameCallback;
import org.eclipse.ecf.core.security.UnsupportedCallbackException;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.user.User;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.ui.Activator;
import org.eclipse.ecf.internal.ui.Constants;
import org.eclipse.ecf.presence.IAccountManager;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.IPresenceListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageEvent;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;
import org.eclipse.ecf.presence.im.IChatID;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.roster.RosterEntry;
import org.eclipse.ecf.ui.dialogs.AddBuddyDialog;
import org.eclipse.ecf.ui.dialogs.ChangePasswordDialog;
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
import org.eclipse.jface.viewers.DoubleClickEvent;
import org.eclipse.jface.viewers.IDoubleClickListener;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.ViewerSorter;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
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

public class RosterView extends ViewPart implements IIMMessageListener, IChatRoomViewCloseListener {
	private static final String CHAT_ROOM_VIEW_CLASS = "org.eclipse.ecf.ui.views.ChatRoomView";

	public static final String UNFILED_GROUP_NAME = "Buddies";

	protected static final int TREE_EXPANSION_LEVELS = 3;

	private TreeViewer viewer;

	private Action selectedChatAction;

	private Action selectedDoubleClickAction;

	private Action disconnectAction;

	private Action disconnectAccountAction;

	private Action openChatRoomAction;

	private Action openChatRoomAccountAction;

	protected Hashtable chatThreads = new Hashtable();

	protected Hashtable accounts = new Hashtable();

	protected Hashtable chatRooms = new Hashtable();

	/**
	 * Called when an account is added to a RosterView. By default, this method
	 * simply returns null, meaning that no shared object is to be associated
	 * with the given account. Subclasses may override if they wish to create
	 * and set up a shared object for the given account.
	 * 
	 * @param account
	 *            the RosterUserAccount to add the shared object to
	 */
	protected ISharedObject createAndAddSharedObjectForAccount(
			RosterUserAccount account) {
		return null;
	}

	protected void addAccount(RosterUserAccount account) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			ID accountID = account.getServiceID();
			if (accountID != null) {
				vcp.addAccount(accountID, accountID.getName());
				refreshView();
			}
		}
		accounts.put(account.getServiceID(), account);
	}

	protected RosterUserAccount getAccount(ID serviceID) {
		return (RosterUserAccount) accounts.get(serviceID);
	}

	protected void removeAccount(ID serviceID) {
		accounts.remove(serviceID);
	}

	protected String getUserNameFromID(ID userID) {
		if (userID == null)
			return "";
		String uname = userID.getName();
		int index = uname.lastIndexOf("@");
		String username = uname;
		if (index >= 0) {
			username = uname.substring(0, index);
		}
		if (username.equals(""))
			return uname;
		else
			return username;
	}

	public void dispose() {
		synchronized (accounts) {
			for (Iterator i = accounts.keySet().iterator(); i.hasNext();) {
				ID serviceID = (ID) i.next();
				RosterUserAccount account = getAccount(serviceID);
				if (account != null) {
					ILocalInputHandler handler = account.getInputHandler();
					if (handler != null) {
						handler.disconnect();
					}
				}
			}
			accounts.clear();
		}
		super.dispose();
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
		viewer.setContentProvider(new RosterViewContentProvider(this));
		viewer.setLabelProvider(new RosterViewLabelProvider(this));
		viewer.setSorter(new ViewerSorter());
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

	protected void disconnectAccount(RosterUserAccount acct) {
		acct.getInputHandler().disconnect();
	}

	/**
	 * Called when time to fill the context menu. First allows super class to
	 * fill menu, then adds on test action that simply sends shared object
	 * message to given buddy. Subclasses may override as appropriate to fill in
	 * context menu. Note that super.fillContextMenu(manager) should always be
	 * called first to allow the superclass to fill in the context menu.
	 * 
	 * @param manager
	 *            the IMenuManager
	 */
	protected void fillContextMenu(IMenuManager manager) {
		final RosterObject rosterObject = getSelectedTreeObject();
		final ID targetID = rosterObject.getID();
		if (rosterObject != null) {
			if (rosterObject instanceof RosterBuddy) {
				final RosterBuddy tb = (RosterBuddy) rosterObject;
				selectedChatAction = new Action() {
					public void run() {
						openChatWindowForTarget(targetID);
					}
				};
				selectedChatAction.setText("Send IM to "
						+ rosterObject.getID().getName());
				selectedChatAction.setImageDescriptor(ImageDescriptor
						.createFromImage(Activator.getDefault()
								.getImageRegistry().get(
										Constants.DECORATION_MESSAGE)));
				manager.add(selectedChatAction);
				RosterObject parent = rosterObject.getParent();
				RosterGroup tg = null;
				if (parent != null && parent instanceof RosterGroup) {
					tg = (RosterGroup) parent;
				}
				final RosterGroup rosterGroup = tg;
				Action removeUserAction = new Action() {
					public void run() {
						removeUserFromGroup(tb, rosterGroup);
					}
				};
				if (rosterGroup != null) {
					removeUserAction.setText("Remove " + rosterObject.getName()
							+ " from " + rosterGroup.getName() + " group");
				} else {
					removeUserAction.setText("Remove " + rosterObject.getName());
				}
				removeUserAction.setImageDescriptor(PlatformUI.getWorkbench()
						.getSharedImages().getImageDescriptor(
								ISharedImages.IMG_TOOL_DELETE));
				manager.add(removeUserAction);

			} else if (rosterObject instanceof RosterAccount) {
				final RosterAccount rosterAccount = (RosterAccount) rosterObject;
				final ID accountID = rosterAccount.getID();
				final RosterUserAccount ua = getAccount(accountID);
				if (ua != null) {
					Action addBuddyToGroupAction = new Action() {
						public void run() {
							sendRosterAdd(accountID, null);
						}
					};
					addBuddyToGroupAction.setImageDescriptor(ImageDescriptor
							.createFromImage(Activator.getDefault()
									.getImageRegistry().get(
											Constants.DECORATION_ADD_BUDDY)));
					addBuddyToGroupAction.setText("Add Buddy");
					addBuddyToGroupAction.setEnabled(true);

					manager.add(addBuddyToGroupAction);
					openChatRoomAccountAction = new Action() {
						public void run() {
							showChatRoomsForAccount(ua);
						}
					};
					openChatRoomAccountAction
							.setText("Show chat rooms for account");
					openChatRoomAccountAction.setEnabled(true);
					openChatRoomAccountAction
							.setImageDescriptor(ImageDescriptor
									.createFromImage(Activator.getDefault()
											.getImageRegistry()
											.get(Constants.DECORATION_ADD_CHAT)));

					manager.add(openChatRoomAccountAction);

					Action changePasswordAction = new Action() {
						public void run() {
							changePasswordForAccount(accountID);
						}
					};
					changePasswordAction.setText("Change Password");
					changePasswordAction
							.setToolTipText("Change password for account");
					changePasswordAction.setEnabled(true);
					manager.add(changePasswordAction);

					disconnectAccountAction = new Action() {
						public void run() {
							if (MessageDialog.openConfirm(RosterView.this
									.getViewSite().getShell(), "Disconnect",
									"Disconnect from account?")) {
								disconnectAccount(ua);
							}
						}
					};
					disconnectAccountAction.setText("Disconnect from account");
					disconnectAccountAction.setEnabled(true);
					disconnectAccountAction
							.setImageDescriptor(ImageDescriptor
									.createFromImage(Activator
											.getDefault()
											.getImageRegistry()
											.get(
													Constants.DECORATION_DISCONNECT_ENABLED)));
					manager.add(disconnectAccountAction);

				}

			} else if (rosterObject instanceof RosterGroup) {
				final RosterGroup rosterGroup = (RosterGroup) rosterObject;
				final String groupName = rosterGroup.getName();
				Action removeGroupAction = new Action() {
					public void run() {
						removeGroup(groupName);
					}
				};
				String accountName = rosterGroup.getID().getName();
				removeGroupAction.setText("Remove " + rosterObject.getName()
						+ " for account " + accountName);
				removeGroupAction.setEnabled(rosterGroup.getTotalCount() == 0);
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

	protected void changePasswordForAccount(ID accountID) {
		RosterUserAccount account = getAccount(accountID);
		if (account != null) {
			IPresenceContainerAdapter pc = account.getPresenceContainer();
			IAccountManager am = pc.getAccountManager();
			ChangePasswordDialog cpd = new ChangePasswordDialog(viewer
					.getControl().getShell());
			cpd.open();
			if (cpd.getResult() == Window.OK) {
				try {
					am.changePassword(cpd.getNewPassword());
				} catch (ECFException e) {
					MessageDialog.openError(viewer.getControl().getShell(),
							"Password not changed", "Error changing password");
				}
			}
		}
	}

	public void sendRosterAdd(ID svcID, String groupName) {
		sendRosterAdd(svcID, null, groupName);
	}

	public void sendRosterAdd(ID svcID, String username, String groupName) {
		String[] groupNames = this.getAllGroupNamesForAccount(svcID);
		List g = Arrays.asList(groupNames);
		int selected = (groupName == null) ? -1 : g.indexOf(groupName);
		AddBuddyDialog sg = new AddBuddyDialog(viewer.getControl().getShell(),
				username, groupNames, selected);
		sg.open();
		if (sg.getResult() == Window.OK) {
			String group = sg.getGroup();
			String user = sg.getUser();
			String nickname = sg.getNickname();
			sg.close();
			String[] sendGroups = null;
			if (group != null) {
				sendGroups = (group == null) ? null : new String[] { group };
			}
			// Finally, send the information and request subscription
			getAccount(svcID).getInputHandler().sendRosterAdd(user, nickname,
					sendGroups);
		}
	}

	protected void removeUserFromGroup(RosterBuddy buddy, RosterGroup group) {
		RosterUserAccount account = getAccount(buddy.getServiceID());
		if (account != null) {
			ILocalInputHandler handler = account.getInputHandler();
			handler.sendRosterRemove(buddy.getID());
		}
	}

	protected RosterObject getSelectedTreeObject() {
		ISelection selection = viewer.getSelection();
		Object obj = ((IStructuredSelection) selection).getFirstElement();
		RosterObject rosterObject = (RosterObject) obj;
		return rosterObject;
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
		if (res == Window.OK) {
			String strres = dlg.getValue();
			if (strres != null && !strres.equals("")) {
				ID target = null;
				try {
					target = IDFactory.getDefault().createStringID(strres);
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

		RoomWithAView(IChatRoomContainer container, ChatRoomView view,
				String secondaryID) {
			this.container = container;
			this.view = view;
			this.secondaryID = secondaryID;
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
			URI aURI = new URI(roomID.getName());
			String auth = aURI.getAuthority();
			String path = aURI.getPath();
			return auth + path;
		} catch (URISyntaxException e) {
			return null;
		}
	}

	protected IConnectContext getChatJoinContext(final String windowText) {
		return new IConnectContext() {
			public CallbackHandler getCallbackHandler() {
				return new CallbackHandler() {
					public void handle(Callback[] callbacks)
							throws IOException, UnsupportedCallbackException {
						if (callbacks == null)
							return;
						for (int i = 0; i < callbacks.length; i++) {
							if (callbacks[i] instanceof NameCallback) {
								NameCallback ncb = (NameCallback) callbacks[i];
								InputDialog id = new InputDialog(
										RosterView.this.getViewSite()
												.getShell(), windowText, ncb
												.getPrompt(), ncb
												.getDefaultName(), null);
								id.setBlockOnOpen(true);
								id.open();
								if (id.getReturnCode() != Window.OK)
									// If user cancels, stop here
									throw new IOException("User cancelled");
								ncb.setName(id.getValue());
							}
						}
					}
				};
			}
		};
	}

	protected void showChatRoomsForAccount(RosterUserAccount ua) {
		IChatRoomManager manager = ua.getPresenceContainer()
				.getChatRoomManager();
		if (manager != null)
			showChatRooms(new IChatRoomManager[] { manager });
		else
			showChatRooms(new IChatRoomManager[] {});
	}

	protected void showChatRooms(IChatRoomManager[] managers) {
		// Create chat room selection dialog with managers, open
		ChatRoomSelectionDialog dialog = new ChatRoomSelectionDialog(
				RosterView.this.getViewSite().getShell(), managers);
		dialog.setBlockOnOpen(true);
		dialog.open();
		// If selection cancelled then simply return
		if (dialog.getReturnCode() != Window.OK)
			return;
		// Get selected room, selected manager, and selected IChatRoomInfo
		ChatRoomSelectionDialog.Room room = dialog.getSelectedRoom();
		IChatRoomInfo selectedInfo = room.getRoomInfo();
		// If they are null then we can't proceed
		if (room == null || selectedInfo == null) {
			MessageDialog.openInformation(RosterView.this.getViewSite()
					.getShell(), "No room selected",
					"Cannot connect to null room");
			return;
		}
		// Now get the secondary ID from the selected room id
		String secondaryID = getChatRoomSecondaryID(selectedInfo.getRoomID());
		if (secondaryID == null) {
			MessageDialog.openError(RosterView.this.getViewSite().getShell(),
					"Could not get identifier for room",
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
			chatRoom = selectedInfo.createChatRoomContainer();
		} catch (ContainerCreateException e1) {
			MessageDialog.openError(RosterView.this.getViewSite().getShell(),
					"Could not create chat room",
					"Could not create chat room for account");
		}
		// Get the chat message sender callback so that we can send
		// messages to chat room
		IChatRoomMessageSender sender = chatRoom.getChatRoomMessageSender();
		IViewPart view = null;
		try {
			IViewReference ref = wp.findViewReference(CHAT_ROOM_VIEW_CLASS,
					secondaryID);
			if (ref == null) {
				view = wp.showView(CHAT_ROOM_VIEW_CLASS, secondaryID,
						IWorkbenchPage.VIEW_ACTIVATE);
			} else {
				view = ref.getView(true);
			}
			final ChatRoomView chatroomview = (ChatRoomView) view;
			// initialize the chatroomview with the necessary
			// information
			chatroomview.initialize(RosterView.this, secondaryID, chatRoom,
					selectedInfo, sender);
			// Add listeners so that the new chat room gets
			// asynch notifications of various relevant chat room events
			chatRoom.addMessageListener(new IIMMessageListener() {
				
				public void handleMessageEvent(IIMMessageEvent messageEvent) {
					if (messageEvent instanceof IChatRoomMessageEvent) {
						IChatRoomMessage m = ((IChatRoomMessageEvent) messageEvent).getChatRoomMessage();
						chatroomview.handleMessage(m.getFromID(), m.getMessage());
					}
					
				}
			});
			chatRoom.addChatRoomParticipantListener(new IChatRoomParticipantListener() {
				public void handlePresence(ID fromID, IPresence presence) {
					chatroomview.handlePresence(fromID, presence);
				}

				public void handleArrivedInChat(ID participant) {
					chatroomview.handleJoin(participant);
				}

				public void handleDepartedFromChat(ID participant) {
					chatroomview.handleLeave(participant);
				}
			});
		} catch (PartInitException e) {
			Activator.log(
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
			chatRoom
					.connect(selectedInfo.getRoomID(),
							getChatJoinContext("Nickname for "
									+ selectedInfo.getName()));
		} catch (ContainerConnectException e1) {
			Activator.log("Exception connecting to chat room "
					+ selectedInfo.getRoomID(), e1);
			MessageDialog.openError(RosterView.this.getViewSite().getShell(),
					"Could not connect", "Cannot connect to chat room "
							+ selectedInfo.getName() + ", message: "
							+ e1.getMessage());
			return;
		}
		// If connect successful...we create a room with a view and add
		// it to our known set
		addRoomView(new RoomWithAView(chatRoom, (ChatRoomView) view,
				secondaryID));

	}

	private void makeActions() {
		selectedDoubleClickAction = new Action() {
			public void run() {
				RosterObject rosterObject = getSelectedTreeObject();
				final ID targetID = rosterObject.getID();
				if (targetID != null)
					openChatWindowForTarget(targetID);
			}
		};
		disconnectAction = new Action() {
			public void run() {
				if (MessageDialog.openConfirm(RosterView.this.getViewSite()
						.getShell(), "Disconnect", "Disconnect all accounts?")) {
					// Disconnect all accounts
					for (Iterator i = accounts.entrySet().iterator(); i
							.hasNext();) {
						Map.Entry entry = (Map.Entry) i.next();
						RosterUserAccount account = (RosterUserAccount) entry.getValue();
						disconnectAccount(account);
					}
					setToolbarEnabled(false);
					this.setEnabled(false);
				}
			}
		};
		disconnectAction.setText("Disconnect");
		disconnectAction.setToolTipText("Disconnect from all accounts");
		disconnectAction.setEnabled(false);
		disconnectAction.setImageDescriptor(ImageDescriptor
				.createFromImage(Activator.getDefault().getImageRegistry().get(
						Constants.DECORATION_DISCONNECT_ENABLED)));
		disconnectAction.setDisabledImageDescriptor(ImageDescriptor
				.createFromImage(Activator.getDefault().getImageRegistry().get(
						Constants.DECORATION_DISCONNECT_DISABLED)));
		openChatRoomAction = new Action() {
			public void run() {
				// Get managers for all accounts currently connected to
				List list = new ArrayList();
				for (Iterator i = accounts.values().iterator(); i.hasNext();) {
					RosterUserAccount ua = (RosterUserAccount) i.next();
					IChatRoomManager man = ua.getPresenceContainer()
							.getChatRoomManager();
					if (man != null)
						list.add(man);
				}
				// get chat rooms, allow user to choose desired one and open it
				showChatRooms((IChatRoomManager[]) list
						.toArray(new IChatRoomManager[] {}));
			}
		};
		openChatRoomAction.setText("Enter Chatroom");
		openChatRoomAction.setToolTipText("Show chat rooms for all accounts");
		openChatRoomAction.setImageDescriptor(ImageDescriptor
				.createFromImage(Activator.getDefault().getImageRegistry().get(
						Constants.DECORATION_ADD_CHAT)));
		openChatRoomAction.setEnabled(false);

	}

	protected void addRoomView(RoomWithAView roomView) {
		chatRooms.put(roomView.getID(), roomView);
	}

	protected void removeRoomView(RoomWithAView roomView) {
		chatRooms.remove(roomView.getID());
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
				window = createChatWindowForTarget(targetID);
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

	protected ChatWindow createChatWindowForTarget(ID targetID) {
		RosterUserAccount account = getAccountForUser(targetID);
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

	public void handleRosterEntryAdd(ID groupID, IRosterEntry entry) {
		if (entry == null)
			return;
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.replaceEntry(groupID, entry);
			refreshView();
		}
	}

	public void handlePresence(ID groupID, ID userID, IPresence presence) {
		IChatID chatID = (IChatID) userID.getAdapter(IChatID.class);
		String name = null;
		if (chatID != null) name = chatID.getUsername();
		else name = userID.toString();
		handleRosterEntryAdd(groupID, new RosterEntry(new Object(), new User(userID, name), presence));
	}

	protected RosterUserAccount getAccountForUser(ID userID) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp == null)
			return null;
		RosterBuddy buddy = vcp.findBuddyWithUserID(userID);
		if (buddy == null)
			return null;
		RosterUserAccount account = getAccount(buddy.getServiceID());
		return account;
	}

	protected ILocalInputHandler getHandlerForUser(ID userID) {
		RosterUserAccount account = getAccountForUser(userID);
		if (account == null)
			return null;
		else
			return account.getInputHandler();
	}

	public Object getAdapter(Class clazz) {
		if (clazz != null && clazz.equals(ILocalInputHandler.class))
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
		else if (clazz.equals(IPresenceListener.class))
			return this;
		else if (clazz.equals(IIMMessageListener.class))
			return this;
		else
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

	/*
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
*/
	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.IIMMessageListener#handleMessageEvent(org.eclipse.ecf.presence.IIMMessageEvent)
	 */
	public void handleMessageEvent(IIMMessageEvent messageEvent) {
		ChatWindow window = openChatWindowForTarget(messageEvent.getFromID());
		// finally, show message
		if (window != null) {
			window.handleMessageEvent(messageEvent);
			window.setStatus("last message received at "
					+ (new SimpleDateFormat("hh:mm:ss").format(new Date())));
		}
	}

	public void addAccount(ID account, IUser user, ILocalInputHandler handler,
			IPresenceContainerAdapter container,
			ISharedObjectContainer soContainer) {
		addAccount(new RosterUserAccount(this, account, user, handler, container,
				soContainer));
		setToolbarEnabled(true);
	}

	protected void setToolbarEnabled(boolean enabled) {
		disconnectAction.setEnabled(enabled);
		openChatRoomAction.setEnabled(enabled);
	}

	public void accountDeparted(ID serviceID) {
		RosterUserAccount account = getAccount(serviceID);
		if (account != null) {
			handleAccountDisconnected(account);
		}
	}

	protected void disposeAllChatWindowsForAccount(RosterUserAccount account,
			String status) {
		synchronized (chatThreads) {
			for (Iterator i = chatThreads.values().iterator(); i.hasNext();) {
				ChatWindow window = (ChatWindow) i.next();
				ID userID = window.getLocalUser().getID();
				RosterUserAccount rosterUserAccount = getAccountForUser(userID);
				if (rosterUserAccount != null) {
					if (rosterUserAccount.getServiceID().equals(
							account.getServiceID())) {
						window.setDisposed(status);
						i.remove();
					}
				}
			}
		}
	}

	protected void removeAllRosterEntriesForAccount(RosterUserAccount account) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.removeAllEntriesForAccount(account);
			refreshView();
		}
	}

	public String[] getAllGroupNamesForAccount(ID accountID) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null)
			return vcp.getAllGroupNamesForAccount(accountID);
		else
			return new String[0];
	}

	public String getSelectedGroupName() {
		RosterObject to = getSelectedTreeObject();
		if (to == null)
			return null;
		if (to instanceof RosterGroup) {
			RosterGroup tg = (RosterGroup) to;
			return tg.getName();
		}
		return null;
	}

	public void addGroup(ID svcID, String name) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.addGroup(svcID, name);
			refreshView();
		}
	}

	public void removeGroup(String name) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.removeGroup(name);
			refreshView();
		}
	}

	public void removeRosterEntry(ID id) {
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.removeRosterEntry(id);
			refreshView();
		}
	}

	protected void handleAccountDisconnected(RosterUserAccount account) {
		removeAllRosterEntriesForAccount(account);
		disposeAllChatWindowsForAccount(account,
				"Disconnected from server.  Chat is inactive");
		accounts.remove(account.getServiceID());
		if (accounts.size() == 0)
			setToolbarEnabled(false);
	}

	public void handleRosterEntryUpdate(ID groupID, IRosterEntry entry) {
		if (groupID == null || entry == null)
			return;
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null) {
			vcp.replaceEntry(groupID, entry);
			refreshView();
		}
	}

	public void handleRosterEntryRemove(ID groupID, IRosterEntry entry) {
		if (groupID == null || entry == null)
			return;
		RosterViewContentProvider vcp = (RosterViewContentProvider) viewer
				.getContentProvider();
		if (vcp != null)
			vcp.removeRosterEntry(entry.getUser().getID());
		refreshView();
	}

	public void chatRoomViewClosing(String secondaryID) {
		RoomWithAView roomView = (RoomWithAView) chatRooms.get(secondaryID);
		if (roomView != null) {
			IChatRoomContainer container = roomView.getContainer();
			container.dispose();
			removeRoomView(roomView);
		}
	}

	public void handleTyping(ID fromID) {
		ChatWindow window = null;
		synchronized (chatThreads) {
			window = (ChatWindow) chatThreads.get(fromID);
		}
		if (window != null) {
			IChatID chatID = (IChatID) fromID.getAdapter(IChatID.class);
			String name = fromID.getName();
			if (chatID != null) name = chatID.getUsername();
			window.setStatus(name+" is typing");
		}
	}

}
 No newline at end of file