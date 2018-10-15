IRoomInfo roomInfo = manager.getChatRoomInfo(targetID.getName());

package org.eclipse.ecf.example.collab;

import org.eclipse.ecf.core.ContainerInstantiationException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.presence.IInvitationListener;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chat.IChatMessageSender;
import org.eclipse.ecf.presence.chat.IChatParticipantListener;
import org.eclipse.ecf.presence.chat.IChatRoomContainer;
import org.eclipse.ecf.presence.chat.IChatRoomManager;
import org.eclipse.ecf.presence.chat.IRoomInfo;
import org.eclipse.ecf.ui.UiPlugin;
import org.eclipse.ecf.ui.views.ChatRoomView;
import org.eclipse.ecf.ui.views.IChatRoomViewCloseListener;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;

public class ChatRoomManagerUI {
	IChatRoomManager manager;
	
	public ChatRoomManagerUI(IChatRoomManager manager) {
		super();
		this.manager = manager;
	}

	public ChatRoomManagerUI setup(final IContainer newClient, final ID targetID,
			String username) {
		// If we don't already have a connection/view to this room then
		// now, create chat room instance
		// Get the chat message sender callback so that we can send
		// messages to chat room
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
				try {
					IRoomInfo roomInfo = manager.getChatRoomInfo(targetID);
					IChatRoomContainer chatRoom = null;
					try {
						chatRoom = roomInfo.createChatRoomContainer();
					} catch (ContainerInstantiationException e1) {
						// can't happen
					}
					IChatMessageSender sender = chatRoom.getChatMessageSender();
					IWorkbenchWindow ww = PlatformUI.getWorkbench()
							.getActiveWorkbenchWindow();
					IWorkbenchPage wp = ww.getActivePage();
					IViewPart view = wp.showView("org.eclipse.ecf.ui.views.ChatRoomView");
					final ChatRoomView chatroomview = (ChatRoomView) view;
					// initialize the chatroomview with the necessary
					// information
					chatroomview.initialize(new IChatRoomViewCloseListener() {
						public void chatRoomViewClosing(String secondaryID) {
							newClient.dispose();
						}
					}, null, chatRoom, roomInfo, sender);
					// Add listeners so that the new chat room gets
					// asynch notifications of various relevant chat room events
					chatRoom.addMessageListener(new IMessageListener() {
						public void handleMessage(ID fromID, ID toID, Type type,
								String subject, String messageBody) {
							chatroomview.handleMessage(fromID, toID, type, subject,
									messageBody);
						}
					});
					chatRoom.addChatParticipantListener(new IChatParticipantListener() {
						public void handlePresence(ID fromID, IPresence presence) {
							chatroomview.handlePresence(fromID, presence);
						}
						public void joined(ID user) {
							chatroomview.handleJoin(user);
						}
						public void left(ID user) {
							chatroomview.handleLeave(user);
						}
					});
					chatRoom.addInvitationListener(new IInvitationListener() {
						public void handleInvitationReceived(ID roomID, ID from,
								ID toID, String subject, String body) {
							chatroomview.handleInvitationReceived(roomID, from, toID,
									subject, body);
						}
					});
				} catch (PartInitException e) {
					UiPlugin.log(
							"Exception in chat room view initialization for chat room "
									+ targetID, e);
				}
            }
        });
		return this;
	}
}