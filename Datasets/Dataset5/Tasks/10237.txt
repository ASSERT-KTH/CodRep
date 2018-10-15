from+"'s '"+groupName+"' group has "+activeSize+" active and "+totalSize+" total group members");

package org.eclipse.ecf.example.collab.share;

import java.io.IOException;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.AbstractSharedObject;
import org.eclipse.ecf.core.sharedobject.SharedObjectMsg;
import org.eclipse.ecf.example.collab.ui.CollabRosterView;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;

public class RosterSharedObject extends AbstractSharedObject {

	CollabRosterView view;

	public RosterSharedObject(CollabRosterView view) {
		this.view = view;
	}

	protected boolean handleSharedObjectMsg(SharedObjectMsg msg) {
		try {
			msg.invoke(this);
			return true;
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}

	public void sendPrivateMessageTo(ID targetID, String fromName, String message) {
		try {
			super.sendSharedObjectMsgTo(targetID, SharedObjectMsg.createMsg(
					null, "handlePrivateMessage", fromName, message));
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	protected void handlePrivateMessage(final String fromName, final String message) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				String from = ((fromName == null) ? "<nobody>" : fromName);
				MessageDialog.openInformation(Display.getCurrent()
						.getActiveShell(), "ECF Private Message from "
						+ from,
						from+" says: "+message);
			}
		});
	}
	
	public void sendGroupSizeMessageTo(ID targetID, String fromName, String groupName, Integer activeSize, Integer totalSize) {
		try {
			super.sendSharedObjectMsgTo(targetID, SharedObjectMsg.createMsg(
					null, "handleRosterSizeMessage", fromName, groupName, activeSize, totalSize));
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	protected void handleRosterSizeMessage(final String fromName, final String groupName, final Integer activeSize, final Integer totalSize) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				String from = ((fromName == null) ? "<nobody>" : fromName);
				MessageDialog.openInformation(Display.getCurrent()
						.getActiveShell(), "ECF Roster Size Message from "
						+ from,
						"For Group '"+groupName+"' active="+activeSize+" and total="+totalSize);
			}
		});
	}
	
	
	/**
	 * Message sender to show a view of given ID to target user.  This method sends
	 * a message which the receiver RosterSharedObject is expected to call {@link #handleShowViewWithID(String, String, Integer)}
	 * to handle the message
	 * 
	 * @param targetID the ID of the target user to receive the sendShowViewWithID request.  Must not be null
	 * @param viewID the String identifying the view to display
	 */
	public void sendShowViewWithID(ID targetID, String viewID, String secID, Integer mode) {
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					"handleShowViewWithID", viewID, secID, mode);
			sendSharedObjectMsgTo(targetID,m);
			sendSharedObjectMsgToSelf(m);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	/**
	 * Message sender to show a view of given ID to target user.  This method sends
	 * a message which the receiver RosterSharedObject is expected to call {@link #handleShowView(String)}
	 * to handle the message
	 * 
	 * @param targetID the ID of the target user to receive the sendShowView request.  Must not be null
	 * @param viewID the String identifying the view to display
	 */
	public void sendShowView(ID targetID, String viewID) {
		if (targetID == null) return;
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null, "handleShowView",viewID);
			sendSharedObjectMsgTo(targetID,m);
			sendSharedObjectMsgToSelf(m);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	/**
	 * Message handler for {@link #sendShowViewWithID(ID, String, String, Integer)} message sender.  This message
	 * handler takes the given viewID and opens it on the local Display
	 * 
	 * @param viewID the viewID to display
	 */
	protected void handleShowViewWithID(final String viewID,
			final String secID, final Integer mode) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					IWorkbenchWindow ww = PlatformUI.getWorkbench()
							.getActiveWorkbenchWindow();
					IWorkbenchPage wp = ww.getActivePage();
					if (wp == null)
						throw new NullPointerException("showViewWithID(" + viewID + ") "
								+ "workbench page is null");
					wp.showView(viewID, secID, mode.intValue());
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}
	/**
	 * Message handler for {@link #sendShowView(ID, String)} message sender.  This message
	 * handler takes the given viewID and opens it on the local Display
	 * 
	 * @param viewID the viewID to display
	 */
	protected void handleShowView(final String viewID) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					IWorkbenchWindow ww = PlatformUI.getWorkbench()
							.getActiveWorkbenchWindow();
					IWorkbenchPage wp = ww.getActivePage();
					if (wp == null)
						throw new NullPointerException("showView(" + viewID + ") "
								+ "workbench page is null");
					wp.showView(viewID);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

}