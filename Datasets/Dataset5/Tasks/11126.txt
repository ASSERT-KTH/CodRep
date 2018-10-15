System.out.println("RosterSharedObject.handleMessage(" + message + ")");

package org.eclipse.ecf.example.collab.share;

import java.io.IOException;

import org.eclipse.ecf.core.events.ISharedObjectMessageEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.AbstractSharedObject;
import org.eclipse.ecf.core.sharedobject.SharedObjectMsg;
import org.eclipse.ecf.core.sharedobject.SharedObjectMsgEvent;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.example.collab.ui.CollabRosterView;

public class RosterSharedObject extends AbstractSharedObject {

	CollabRosterView view;

	public RosterSharedObject(CollabRosterView view) {
		this.view = view;
	}

	public void sendMessageTo(ID targetID, String message) {
		try {
			super.sendSharedObjectMsgTo(targetID, SharedObjectMsg.createMsg(
					null, "handleMessage", message));
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	protected Event handleSharedObjectMsgEvent(ISharedObjectMessageEvent event) {
		try {
			((SharedObjectMsgEvent) event.getData()).getSharedObjectMsg()
					.invoke(this);
		} catch (Exception e) {
			e.printStackTrace();
		}
		return event;
	}

	protected void handleMessage(String message) {
		// XXX this should call the view back to display the message/do other things, etc
		System.out.println("GOT MESSAGE: " + message);
	}
}