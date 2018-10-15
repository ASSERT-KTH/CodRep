});

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
package org.eclipse.ecf.example.collab;

import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.IContainerConnectedEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.chat.IChatRoomContainer;
import org.eclipse.ecf.presence.chat.IChatRoomManager;
import org.eclipse.ecf.presence.chat.IRoomInfo;
import org.eclipse.ecf.ui.UiPlugin;
import org.eclipse.ecf.ui.views.ChatRoomManagerView;
import org.eclipse.ecf.ui.views.IChatRoomViewCloseListener;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;

public class IRCChatRoomManagerUI {
	private static final String CHAT_ROOM_MANAGER_VIEWID = "org.eclipse.ecf.ui.views.ChatRoomManagerView";

	IChatRoomManager manager;
	
	boolean viewAlreadyActive = false;
	
	public IRCChatRoomManagerUI(IChatRoomManager manager) {
		super();
		this.manager = manager;
	}
	
	protected String getViewIDFromTargetID(ID targetID) {
		URI uri;
		try {
			uri = targetID.toURI();
		} catch (URISyntaxException e) {
			return null;
		}
		// Get authority, host, and port to define view ID
		int port = uri.getPort();
		return uri.getAuthority() + ((port==-1)?"":":"+port);
	}
	protected ChatRoomManagerView getChatRoomManagerView(ID targetID) throws PartInitException {
		// Get view
		String secondaryViewID = getViewIDFromTargetID(targetID);
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
		.getActiveWorkbenchWindow();
		IWorkbenchPage wp = ww.getActivePage();
		ChatRoomManagerView view = null;
		if (secondaryViewID == null) view = (ChatRoomManagerView) wp.showView(CHAT_ROOM_MANAGER_VIEWID);
		else {
			IViewReference viewRef = wp.findViewReference(CHAT_ROOM_MANAGER_VIEWID, secondaryViewID);
			if (viewRef == null) view = (ChatRoomManagerView) wp.showView(CHAT_ROOM_MANAGER_VIEWID,secondaryViewID,IWorkbenchPage.VIEW_ACTIVATE);
			else {
				// Old view with same secondaryViewID found, so use/restore it rather than creating new view
				view = (ChatRoomManagerView) viewRef.getView(true);
				if (view.isEnabled()) viewAlreadyActive = true;
			}
		}
		return view;
	}
	
	private void setupNewView(final IContainer container, final ID targetID, final ChatRoomManagerView chatroomview) {
		IRoomInfo roomInfo = manager.getChatRoomInfo(null);
		if (roomInfo == null) throw new NullPointerException("Chat room manager does not expose chat room interface.  Cannot create UI");
		IChatRoomContainer chatRoom = null;
		try {
			chatRoom = roomInfo.createChatRoomContainer();
		} catch (ContainerCreateException e1) {
			// can't happen for 'root' roomInfo
		}
		// initialize the chatroomview with the necessary
		// information
		chatroomview.initialize(new IChatRoomViewCloseListener() {
			public void chatRoomViewClosing(String secondaryID) {
				container.dispose();
			}
		}, chatRoom, manager, targetID, chatRoom.getChatMessageSender());
		// Add listener for container, so that if the container is spontaneously disconnected,
		// then we will be able to have the UI respond by making itself inactive
		container.addListener(new IContainerListener() {
			public void handleEvent(IContainerEvent evt) {
				if (evt instanceof IContainerDisconnectedEvent) {
					IContainerDisconnectedEvent cd = (IContainerDisconnectedEvent) evt;
					final ID departedContainerID = cd.getTargetID();
					ID connectedID = targetID;
					if (connectedID == null
							|| connectedID.equals(departedContainerID)) {
						chatroomview.disconnected();
					}
				} else if (evt instanceof IContainerConnectedEvent) {
					chatroomview.joinRoom(getChannelFromID(targetID));
				}
			}
		},"");
		// Add listeners so that the new chat room gets
		// asynch notifications of various relevant chat room events
		chatRoom.addMessageListener(new IMessageListener() {
			public void handleMessage(ID fromID, ID toID, Type type,
					String subject, String messageBody) {
				chatroomview.handleMessage(fromID, toID, type, subject,
						messageBody);
			}
		});
	}

	public boolean setup(final IContainer container, final ID targetID,
			String username) {
		// If we don't already have a connection/view to this room then
		// now, create chat room instance
		// Get the chat message sender callback so that we can send
		// messages to chat room
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
				try {
					final ChatRoomManagerView chatroomview = getChatRoomManagerView(targetID);
					if (!viewAlreadyActive) setupNewView(container, targetID, chatroomview);
					else chatroomview.joinRoom(getChannelFromID(targetID));
				} catch (Exception e) {
					UiPlugin.log(
							"Exception in chat room view creation or initialization "
									+ targetID, e);
				}
            }

        });
		return viewAlreadyActive;
	}
	protected String getChannelFromID(ID targetID) {
		String initialRoom = null;
    	try {
    		URI targetURI = targetID.toURI();
    		initialRoom = targetURI.getRawFragment();
    	} catch (URISyntaxException e) {}
    	if (initialRoom == null || initialRoom.equals("")) return null;
    	while (initialRoom.charAt(0) == '/') initialRoom = initialRoom.substring(1);
    	if (initialRoom.charAt(0) != '#') initialRoom = "#"+initialRoom;
    	return initialRoom;
	}

}