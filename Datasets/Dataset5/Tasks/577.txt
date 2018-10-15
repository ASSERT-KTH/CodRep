container.disconnect();

/****************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *    Jacek Pospychala <jacek.pospychala@pl.ibm.com> - bug 197329
 *****************************************************************************/
package org.eclipse.ecf.presence.ui.chatroom;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.StringTokenizer;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.IContainerConnectedEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.IExceptionHandler;
import org.eclipse.ecf.internal.presence.ui.Activator;
import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageEvent;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;

/**
 * Chat room manager user interface.
 */
public class ChatRoomManagerUI implements IChatRoomCommandListener {

	public static final String ROOM_DELIMITER = ","; //$NON-NLS-1$

	protected IContainer container;

	protected IChatRoomManager manager;

	private boolean isContainerConnected = false;

	private boolean viewAlreadyActive = false;

	protected IExceptionHandler exceptionHandler = null;

	protected ChatRoomManagerView chatroomview = null;

	protected ID targetID = null;

	protected String[] channels = null;

	public ChatRoomManagerUI(IContainer container, IChatRoomManager manager) {
		this(container, manager, null);
	}

	public ChatRoomManagerUI(IContainer container, IChatRoomManager manager,
			IExceptionHandler exceptionHandler) {
		super();
		this.container = container;
		this.manager = manager;
		this.exceptionHandler = exceptionHandler;
	}

	public ID getTargetID() {
		return targetID;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.presence.ui.chatroom.IChatRoomCommandListener#handleCommand(org.eclipse.ecf.presence.chatroom.IChatRoomContainer,
	 *      java.lang.String)
	 */
	public String handleCommand(IChatRoomContainer chatRoomContainer,
			String inputLine) {
		return inputLine;
	}
	
	protected IChatRoomViewCloseListener createChatRoomViewCloseListener() {
		return new IChatRoomViewCloseListener() {
			public void chatRoomViewClosing() {
				container.dispose();
			}
		};
	}

	private void setupNewView() throws Exception {
		IChatRoomInfo roomInfo = manager.getChatRoomInfo(null);
		Assert.isNotNull(roomInfo,
				Messages.ChatRoomManagerUI_EXCEPTION_NO_ROOT_CHAT_ROOM_MANAGER);
		IChatRoomContainer managerChatRoom = roomInfo.createChatRoomContainer();
		chatroomview.initializeWithManager(ChatRoomManagerView.getUsernameFromID(targetID),
				ChatRoomManagerView.getHostnameFromID(targetID),
				managerChatRoom, this, createChatRoomViewCloseListener());
		chatroomview.setMessageRenderer(getDefaultMessageRenderer());
		// Add listener for container, so that if the container is spontaneously
		// disconnected,
		// then we will be able to have the UI respond by making itself inactive
		container.addListener(new IContainerListener() {
			public void handleEvent(final IContainerEvent evt) {
				Display.getDefault().syncExec(new Runnable() {
					public void run() {
						if (evt instanceof IContainerDisconnectedEvent) {
							IContainerDisconnectedEvent cd = (IContainerDisconnectedEvent) evt;
							final ID departedContainerID = cd.getTargetID();
							ID connectedID = targetID;
							if (connectedID == null
									|| connectedID.equals(departedContainerID)) {
								chatroomview.disconnected();
								isContainerConnected = false;
							}
						} else if (evt instanceof IContainerConnectedEvent) {
							isContainerConnected = true;
							chatroomview.setEnabled(true);
							String[] channels = getRoomsForTarget();
							for (int i = 0; i < channels.length; i++) {
								IChatRoomInfo info = manager
										.getChatRoomInfo(channels[i]);
								chatroomview.joinRoom(info,
										getPasswordForChatRoomConnect(info));
							}
						}
					}
				});
			}
		});
		// Add listeners so that the new chat room gets
		// asynch notifications of various relevant chat room events
		managerChatRoom.addMessageListener(new IIMMessageListener() {
			public void handleMessageEvent(IIMMessageEvent messageEvent) {
				if (messageEvent instanceof IChatRoomMessageEvent) {
					IChatRoomMessage m = ((IChatRoomMessageEvent) messageEvent)
							.getChatRoomMessage();
					chatroomview.handleMessage(m.getFromID(), m.getMessage());
				}
			}
		});
	}

	protected IMessageRenderer getDefaultMessageRenderer() {
		return new MessageRenderer();
	}

	protected String getPasswordForChatRoomConnect(IChatRoomInfo info) {
		return null;
	}

	/**
	 * Show a chat room manager UI for given targetID. If a UI already exists
	 * that is connected to the given targetID, then it will be raised. and
	 * isContainerConnected connected to the given targetID then this will show
	 * the view associated with this targetID, and return <code>true</code>.
	 * The caller then <b>should not</b> connect the container, as there is
	 * already a container connected to the given target. If we are not already
	 * connected, then this method will return <code>false</code>, indicating
	 * that the caller should connect the new container to the given target ID.
	 * 
	 * @param targetID
	 */
	public void showForTarget(final ID targetID) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					ChatRoomManagerUI.this.targetID = targetID;
					chatroomview = getChatRoomManagerView();
					// If we're not already active, then setup new view
					if (!viewAlreadyActive) {
						setupNewView();
					} else if (isContainerConnected) {
						// If we are already active, and connected, then just
						// join room s
						channels = getRoomsForTarget();
						for (int i = 0; i < channels.length; i++) {
							IChatRoomInfo info = manager
									.getChatRoomInfo(channels[i]);
							chatroomview.joinRoom(info,
									getPasswordForChatRoomConnect(info));
						}
						// We're already connected, so all we do is return
						return;
					}
				} catch (Exception e) {
					if (exceptionHandler != null)
						exceptionHandler.handleException(e);
					else
						Activator
								.getDefault()
								.getLog()
								.log(
										new Status(
												IStatus.ERROR,
												Activator.PLUGIN_ID,
												IStatus.ERROR,
												Messages.ChatRoomManagerUI_EXCEPTION_CHAT_ROOM_VIEW_INITIALIZATION
														+ targetID, e));
				}
			}

		});
	}

	public boolean isContainerConnected() {
		return isContainerConnected;
	}

	protected String getSecondaryViewID(ID targetID) {
		URI uri;
		try {
			uri = new URI(targetID.getName());
		} catch (URISyntaxException e) {
			return null;
		}
		// Get authority, host, and port to define view ID
		int port = uri.getPort();
		return uri.getAuthority() + ((port == -1) ? "" : ":" + port); //$NON-NLS-1$ //$NON-NLS-2$
	}

	protected ChatRoomManagerView getChatRoomManagerView()
			throws PartInitException {
		// Get view
		String secondaryViewID = getSecondaryViewID(targetID);
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
				.getActiveWorkbenchWindow();
		IWorkbenchPage wp = ww.getActivePage();
		ChatRoomManagerView view = null;
		if (secondaryViewID == null)
			view = (ChatRoomManagerView) wp
					.showView(ChatRoomManagerView.VIEW_ID);
		else {
			IViewReference viewRef = wp.findViewReference(
					ChatRoomManagerView.VIEW_ID, secondaryViewID);
			if (viewRef == null)
				view = (ChatRoomManagerView) wp.showView(
						ChatRoomManagerView.VIEW_ID, secondaryViewID,
						IWorkbenchPage.VIEW_ACTIVATE);
			else {
				// Old view with same secondaryViewID found, so use/restore it
				// rather than creating new view
				view = (ChatRoomManagerView) viewRef.getView(true);
			}
		}
		viewAlreadyActive = view.isEnabled();
		return view;
	}

	protected String modifyRoomNameForTarget(String roomName) {
		return roomName;
	}

	protected String[] getRoomsForTarget() {
		String initialRooms = null;
		try {
			URI targetURI = new URI(targetID.getName());
			initialRooms = targetURI.getPath();
		} catch (URISyntaxException e) {
		}
		if (initialRooms == null || initialRooms.equals("")) //$NON-NLS-1$
			return new String[0];
		while (initialRooms.charAt(0) == '/')
			initialRooms = initialRooms.substring(1);

		StringTokenizer st = new StringTokenizer(initialRooms, ROOM_DELIMITER);
		int tokenCount = st.countTokens();
		String[] roomsResult = new String[tokenCount];
		for (int i = 0; i < tokenCount; i++)
			roomsResult[i] = modifyRoomNameForTarget(st.nextToken());
		return roomsResult;
	}

}