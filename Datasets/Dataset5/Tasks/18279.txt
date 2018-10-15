log("sendOpenAndSelectForFile", e); //$NON-NLS-1$

/****************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.example.collab.share;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ReplicaSharedObjectDescription;
import org.eclipse.ecf.example.collab.share.io.EclipseFileTransfer;
import org.eclipse.ecf.example.collab.share.io.FileTransferParams;
import org.eclipse.ecf.internal.example.collab.ClientPlugin;
import org.eclipse.ecf.internal.example.collab.Messages;
import org.eclipse.ecf.internal.example.collab.ui.ChatLine;
import org.eclipse.ecf.internal.example.collab.ui.EditorHelper;
import org.eclipse.ecf.internal.example.collab.ui.FileReceiverUI;
import org.eclipse.ecf.internal.example.collab.ui.LineChatClientView;
import org.eclipse.ecf.internal.example.collab.ui.LineChatView;
import org.eclipse.ecf.internal.example.collab.ui.hyperlink.EclipseCollabHyperlinkDetector;
import org.eclipse.ecf.ui.screencapture.ImageWrapper;
import org.eclipse.ecf.ui.screencapture.ScreenCaptureUtil;
import org.eclipse.ecf.ui.screencapture.ShowImageShell;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

public class EclipseCollabSharedObject extends GenericSharedObject {
	/**
	 * 
	 */
	private static final int MAX_MESSAGE_SIZE = 8096;
	private static final String HANDLE_SHOW_VIEW_MSG = "handleShowView"; //$NON-NLS-1$
	private static final String HANDLE_SHOW_VIEW_WITH_ID_MSG = "handleShowViewWithID"; //$NON-NLS-1$
	private static final String HANDLE_LAUNCH_EDITOR_FOR_FILE_MSG = "handleLaunchEditorForFile"; //$NON-NLS-1$
	private static final String HANDLE_OPEN_AND_SELECT_FOR_FILE_MSG = "handleOpenAndSelectForFile"; //$NON-NLS-1$
	private static final String HANDLE_ADD_MARKER_FOR_FILE_MSG = "handleAddMarkerForFile"; //$NON-NLS-1$
	private static final String HANDLE_USER_UPDATE_MSG = "handleUserUpdate"; //$NON-NLS-1$
	private static final String HANDLE_UPDATE_TREE_DISPLAY_MSG = "handleUpdateTreeDisplay"; //$NON-NLS-1$
	private static final String HANDLE_UNREGISTER_PROXY_MSG = "handleUnregisterProxy"; //$NON-NLS-1$
	private static final String HANDLE_SHOW_TEXT_MSG = "handleShowTextMsg"; //$NON-NLS-1$
	private static final String HANDLE_USER_MSG = "handleUserMessage"; //$NON-NLS-1$
	private static final String HANDLE_CVS_PROJECT_UPDATE_REQUEST_MSG = "handleCVSProjectUpdateRequest"; //$NON-NLS-1$
	private static final String HANDLE_REQUEST_USER_UPDATE_MSG = "handleRequestUserUpdate"; //$NON-NLS-1$
	private static final String HANDLE_REGISTER_PROXY_MSG = "handleRegisterProxy"; //$NON-NLS-1$
	private static final String HANDLE_SHOW_PRIVATE_TEXT_MSG = "handleShowPrivateTextMsg"; //$NON-NLS-1$
	private static final String HANDLE_NOTIFY_USER_ADDED_MSG = "handleNotifyUserAdded"; //$NON-NLS-1$
	private static final String HANDLE_STARTED_TYPING_MSG = "handleStartedTyping"; //$NON-NLS-1$

	public static final String SHARED_MARKER_TYPE = ClientPlugin.SHARED_MARKER_TYPE;
	public static final String ID = "chat"; //$NON-NLS-1$

	private static final String DEFAULT_WINDOW_TITLE = Messages.EclipseCollabSharedObject_WINDOW_TITLE;
	private static final String HANDLE_SHOW_IMAGE_START_MSG = "handleShowImageStart"; //$NON-NLS-1$
	private static final String HANDLE_SHOW_IMAGE_DATA_MSG = "handleShowImageData"; //$NON-NLS-1$

	private String windowTitle = DEFAULT_WINDOW_TITLE;
	private String downloadDirectory = ""; //$NON-NLS-1$
	private LineChatClientView localGUI = null;
	private IResource localResource = null;
	private User localUser = null;
	private String localVersion = ""; //$NON-NLS-1$
	private ID serverID = null;
	private SharedObjectEventListener sharedObjectEventListener = null;
	private IWorkbenchWindow workbenchWindow = null;

	public EclipseCollabSharedObject() {
	}

	public EclipseCollabSharedObject(IResource proj, IWorkbenchWindow window, User user, String downloaddir) {
		this.localResource = proj;
		this.workbenchWindow = window;
		this.localUser = user;
		this.downloadDirectory = downloaddir;
		createOutputView();
		Assert.isNotNull(localGUI, "Local GUI cannot be created...exiting"); //$NON-NLS-1$
	}

	public void activated(ID[] others) {
		super.activated(others);
		if (localGUI == null && !getContext().isGroupManager())
			destroySelfLocal();
	}

	public void chatException(Exception e, String text) {
		log(text, e);
	}

	public void chatGUIDestroy() {
		if (sharedObjectEventListener != null) {
			sharedObjectEventListener.windowClosing();
			sharedObjectEventListener = null;
		}
		destroySelf();
	}

	public void deactivated() {
		super.deactivated();
		synchronized (this) {
			if (localGUI != null) {
				localGUI.disposeClient();
				localGUI = null;
			}
		}
		shells.clear();
		if (sharedObjectEventListener != null) {
			sharedObjectEventListener = null;
		}
		if (workbenchWindow != null) {
			workbenchWindow = null;
		}
		if (localResource != null) {
			localResource = null;
		}
	}

	public void destroySelf() {
		// Make sure we disconnect
		try {
			if (isHost())
				disconnect();
		} catch (final Exception e) {
			log("Exception in destroySelf", e); //$NON-NLS-1$
		}
		// Destroy self
		super.destroySelfLocal();
	}

	public String getDownloadDirectory(String dir) {
		return downloadDirectory;
	}

	public SharedObjectEventListener getSharedObjectEventListener() {
		return sharedObjectEventListener;
	}

	public String getLocalFullProjectPath() {
		String eclipseDir = null;
		try {
			eclipseDir = Platform.getLocation().toOSString();
		} catch (final IllegalStateException e) {
			log("Exception getting local resource path", e); //$NON-NLS-1$
		}
		if (eclipseDir == null)
			eclipseDir = "."; //$NON-NLS-1$
		final String projectDir = (getResource() == null) ? downloadDirectory : getResource().getFullPath().toOSString();
		return new File(eclipseDir, projectDir).getAbsolutePath();
	}

	public String getLocalFullDownloadPath() {
		return new File(getLocalFullProjectPath(), downloadDirectory).getAbsolutePath();
	}

	protected void createOutputView() {
		final String projectName = (localResource == null || localResource.getName().trim().equals("")) ? Messages.EclipseCollabSharedObject_WORKSPACE_RESOURCE_NAME : localResource.getName(); //$NON-NLS-1$
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					final IWorkbenchWindow ww = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
					final IWorkbenchPage wp = ww.getActivePage();
					wp.showView(LineChatView.VIEW_ID);
					windowTitle = NLS.bind(Messages.EclipseCollabSharedObject_TITLE_BAR, localUser.getNickname());
					LineChatView.setViewName(windowTitle);
					localGUI = LineChatView.createClientView(EclipseCollabSharedObject.this, projectName, NLS.bind(Messages.EclipseCollabSharedObject_PROJECT_NAME, projectName), getLocalFullDownloadPath());
				} catch (final Exception e) {
					log("Exception creating LineChatView", e); //$NON-NLS-1$
				}
			}
		});
	}

	public IResource getResource() {
		return localResource;
	}

	protected ReplicaSharedObjectDescription getReplicaDescription(ID remoteID) {
		return null;
	}

	public ID getServerID() {
		return serverID;
	}

	public String getTreeTopLabel() {
		return Messages.EclipseCollabSharedObject_TREE_TOP_LABEL;
	}

	public User getUser() {
		return localUser;
	}

	public User getUserForID(final ID user) {
		return (localGUI != null) ? localGUI.getUser(user) : null;
	}

	public String getUserName() {
		return localUser.getNickname();
	}

	public String getVersionString() {
		return localVersion;
	}

	public String getWindowTitle() {
		return windowTitle;
	}

	public IWorkbenchWindow getWorkbenchWindow() {
		return workbenchWindow;
	}

	// SharedObjectMsg handlers
	protected void handleCreateObject(ReplicaSharedObjectDescription cons) {
		try {
			createObject(null, cons);
		} catch (final Exception e) {
			log("Exception creating local object", e); //$NON-NLS-1$
		}
	}

	public void handleNotifyUserAdded(User user) {
		boolean add = false;
		try {
			final ID[] members = getContext().getGroupMemberIDs();
			for (int i = 0; i < members.length; i++) {
				if (members[i].equals(user.getUserID())) {
					add = true;
					break;
				}
			}
		} catch (final Exception e) {
			log("Exception checking for membership", e); //$NON-NLS-1$
		}
		if (add) {
			boolean addUserResult = false;
			if (localGUI != null) {
				addUserResult = localGUI.addUser(user);
			}
			// If addUserResult is false, it means that this is a new user
			// And we need to report our own existence to them
			if (addUserResult)
				sendNotifyUserAdded();
		}
	}

	protected void handleRequestUserUpdate(ID requestor) {
		sendUserUpdate(requestor);
	}

	protected void handleShowPrivateTextMsg(final User remote, final String aString) {
		// Show line on local interface
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						final ChatLine line = new ChatLine(aString);
						line.setOriginator(remote);
						line.setPrivate(true);
						localGUI.showLine(line);
						localGUI.toFront();
					}
				} catch (final Exception e) {
					log("Exception in showLineOnGUI", e); //$NON-NLS-1$
				}
			}
		});
	}

	protected void handleShowTextMsg(ID remote, String aString) {
		// Show line on local interface
		showLineOnGUI(remote, aString);
	}

	protected void handleUpdateTreeDisplay(final ID fromID, final TreeItem item) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null)
						localGUI.updateTreeDisplay(fromID, item);
				} catch (final Exception e) {
					log("Exception in showLineOnGUI", e); //$NON-NLS-1$
				}
			}
		});
	}

	protected void handleUserUpdate(final User ud) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null)
						localGUI.changeUser(ud);
				} catch (final Exception e) {
					log("Exception in showLineOnGUI", e); //$NON-NLS-1$
				}
			}
		});
	}

	protected void handleUserMessage(final User sender, String msg) {
		// Show line on local interface
		final String message = msg;
		if (sender == null)
			return;
		if (localGUI != null) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					Display.getDefault().beep();
					final Shell[] shells = Display.getDefault().getShells();
					if (shells != null && shells.length > 0) {
						shells[0].setActive();
					}
					MessageDialog.openInformation(null, NLS.bind(Messages.EclipseCollabSharedObject_PRIVATE_MESSAGE_TEXT, sender.getNickname()), message);
				}
			});
		}
	}

	protected synchronized void handleStartedTyping(User user) {
		if (localGUI != null)
			localGUI.startedTyping(user);
	}

	public void sendStartedTyping() {
		try {
			forwardMsgTo(null, SharedObjectMsg.createMsg(null, HANDLE_STARTED_TYPING_MSG, localUser));
		} catch (final Exception e) {
			log("Exception on sendStartedTyping to remote clients", e); //$NON-NLS-1$
		}
	}

	public void inputText(String aString) {
		sendShowTextMsg(aString);
	}

	public boolean isHost() {
		return super.isHost();
	}

	public void disconnect() {
		getContext().disconnect();
	}

	public Object getObject(ID obj) {
		return getContext().getSharedObjectManager().getSharedObject(obj);
	}

	public void memberAdded(ID member) {
		if (sharedObjectEventListener != null) {
			sharedObjectEventListener.memberAdded(member);
		}
		super.memberAdded(member);
		sendNotifyUserAdded();
	}

	public void memberRemoved(final ID member) {
		if (sharedObjectEventListener != null) {
			sharedObjectEventListener.memberRemoved(member);
		}
		super.memberRemoved(member);
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						localGUI.removeUser(member);
					}
				} catch (final Exception e) {
					log("Exception in showLineOnGUI", e); //$NON-NLS-1$
				}
			}
		});
	}

	public void messageProxyObject(ID target, String classname, String meth, Object[] args) {
		final SharedObjectMsg m = SharedObjectMsg.createMsg(null, classname, meth, args);
		try {
			forwardMsgTo(target, m);
			if (target == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception sending message to proxy object", e); //$NON-NLS-1$
		}
	}

	public void otherActivated(ID object) {
		if (sharedObjectEventListener != null) {
			sharedObjectEventListener.otherActivated(object);
		}
		super.otherActivated(object);
	}

	public void otherDeactivated(ID object) {
		if (sharedObjectEventListener != null) {
			sharedObjectEventListener.otherDeactivated(object);
		}
		super.otherDeactivated(object);
	}

	public void refreshProject() {
		if (localResource != null) {
			try {
				localResource.refreshLocal(IResource.DEPTH_INFINITE, new NullProgressMonitor());
			} catch (final Exception e) {
				log("Exception refreshing resource " + localResource.getName(), e); //$NON-NLS-1$
			}
		}
	}

	// SharedObjectMsg senders
	public void sendNotifyUserAdded() {
		try {
			forwardMsgTo(null, SharedObjectMsg.createMsg(null, HANDLE_NOTIFY_USER_ADDED_MSG, localUser));
		} catch (final Exception e) {
			log("Exception on sendNotifyUserAdded to remote clients", e); //$NON-NLS-1$
		}
	}

	public void sendPrivateMessageToUser(User touser, String msg) {
		try {
			forwardMsgTo(touser.getUserID(), SharedObjectMsg.createMsg(null, HANDLE_SHOW_PRIVATE_TEXT_MSG, localUser, msg));
		} catch (final Exception e) {
			log("Exception on sendShowPrivateTextMsg to remote clients", e); //$NON-NLS-1$
		}
	}

	public void sendRegisterProxy(ID toID, String proxyClass, String name) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.createMsg(null, HANDLE_REGISTER_PROXY_MSG, localUser, proxyClass, name));
		} catch (final IOException e) {
			log("Exception sendRegisterProxy", e); //$NON-NLS-1$
		}
	}

	public void sendRequestUserUpdate(ID requestTarget) {
		try {
			forwardMsgTo(requestTarget, SharedObjectMsg.createMsg(null, HANDLE_REQUEST_USER_UPDATE_MSG, localContainerID));
		} catch (final Exception e) {
			log("Exception on sendRequestUserUpdate to remote clients", e); //$NON-NLS-1$
		}
	}

	public void sendCVSProjectUpdateRequest(User touser, String msg) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_CVS_PROJECT_UPDATE_REQUEST_MSG, getUser(), msg);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception on sendCVSProjectUpdateRequest to " + touser, e); //$NON-NLS-1$
		}
	}

	public boolean isCVSShared() {
		try {
			// return CVSWorkspaceRoot.isSharedWithCVS(getProject());
			return false;
		} catch (final Exception e) {
			log("CVS Exception calling isSharedWithCVS in TeamUpdateAction", e); //$NON-NLS-1$
			return false;
		}
	}

	public void sendRingMessageToUser(User user, String msg) {
		ID receiver = null;
		if (user != null) {
			receiver = user.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_USER_MSG, this.localUser, msg);
			forwardMsgTo(receiver, m);
			if (receiver == null)
				sendSelf(m);
		} catch (final Exception e) {
			log("Exception on sendMessageToUser to " + user, e); //$NON-NLS-1$
		}
	}

	public void sendImage(ID toID, ImageData imageData) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.createMsg(null, HANDLE_SHOW_IMAGE_START_MSG, localContainerID, localUser.getNickname(), new ImageWrapper(imageData)));
			final byte[] compressedData = ScreenCaptureUtil.compress(imageData.data);
			final ByteArrayOutputStream bos = new ByteArrayOutputStream(MAX_MESSAGE_SIZE);
			int startPos = 0;
			while (startPos <= compressedData.length) {
				bos.reset();
				final int length = Math.min(compressedData.length - startPos, MAX_MESSAGE_SIZE);
				bos.write(compressedData, startPos, length);
				startPos += MAX_MESSAGE_SIZE;
				bos.flush();
				final Boolean done = new Boolean((compressedData.length - startPos) < 0);
				forwardMsgTo(toID, SharedObjectMsg.createMsg(null, HANDLE_SHOW_IMAGE_DATA_MSG, localContainerID, bos.toByteArray(), done));
			}
		} catch (final Exception e) {
			log("Exception on sendImage", e); //$NON-NLS-1$
		}
	}

	Map shells = new HashMap();

	protected void handleShowImageStart(final ID id, final String fromUser, final ImageWrapper imageWrapper) {
		final Display display = localGUI.getTextControl().getDisplay();
		display.asyncExec(new Runnable() {
			public void run() {
				ShowImageShell showImageShell = (ShowImageShell) shells.get(id);
				if (showImageShell == null) {
					showImageShell = new ShowImageShell(display, id, new DisposeListener() {
						public void widgetDisposed(DisposeEvent e) {
							shells.remove(id);
						}
					});
					shells.put(id, showImageShell);
				}
				showImageShell.initialize(Messages.EclipseCollabSharedObject_SCREEN_CAPTURE_FROM + fromUser, imageWrapper);
				showImageShell.open();
			}
		});
	}

	protected void handleShowImageData(final ID id, final byte[] data, final Boolean done) {
		final ShowImageShell showImageShell = (ShowImageShell) shells.get(id);
		if (showImageShell != null) {
			final Display display = showImageShell.getDisplay();
			if (display != null) {
				display.asyncExec(new Runnable() {
					public void run() {
						showImageShell.addData(data);
						if (done.booleanValue())
							showImageShell.showImage();
					}
				});
			}
		}
	}

	public void sendShowTextMsg(String msg) {
		try {
			forwardMsgTo(null, SharedObjectMsg.createMsg(null, HANDLE_SHOW_TEXT_MSG, localContainerID, msg));
		} catch (final Exception e) {
			log("Exception on sendShowTextMsg to remote clients", e); //$NON-NLS-1$
		}
	}

	public void sendUnregisterProxy(ID toID, String proxyClass) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.createMsg(null, HANDLE_UNREGISTER_PROXY_MSG, localUser, proxyClass));
		} catch (final IOException e) {
			log("Exception sendRegisterProxy", e); //$NON-NLS-1$
		}
	}

	public void sendUpdateTreeDisplay(ID target, TreeItem item) {
		try {
			forwardMsgTo(target, SharedObjectMsg.createMsg(null, HANDLE_UPDATE_TREE_DISPLAY_MSG, localContainerID, item));
		} catch (final Exception e) {
			log("Exception on sendUpdateTreeDisplay to remote clients", e); //$NON-NLS-1$
		}
	}

	public void sendUserUpdate(ID target) {
		try {
			forwardMsgTo(target, SharedObjectMsg.createMsg(null, HANDLE_USER_UPDATE_MSG, localUser));
		} catch (final Exception e) {
			log("Exception on sendUserUpdate to remote clients", e); //$NON-NLS-1$
		}
	}

	public void setListener(SharedObjectEventListener l) {
		sharedObjectEventListener = l;
	}

	public void setServerID(ID server) {
		serverID = server;
	}

	public void setVersionString(String ver) {
		localVersion = ver;
	}

	public void setWindowTitle(String title) {
		this.windowTitle = title;
		synchronized (this) {
			if (localGUI != null) {
				localGUI.setTitle(windowTitle);
			}
		}
	}

	protected void activateView() {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (localGUI != null) {
					final IWorkbenchWindow ww = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
					final IWorkbenchPage wp = ww.getActivePage();
					wp.activate(localGUI.getView());
				}
			}
		});
	}

	public void showLineOnGUI(final ID remote, final String line) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null)
						localGUI.showLine(new ChatLine(line, getUserForID(remote)));
				} catch (final Exception e) {
					log("Exception in showLineOnGUI", e); //$NON-NLS-1$
				}
			}
		});
	}

	public void showRawLine(final ID sender, final String line, final Runnable onClick) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						final ChatLine rawLine = new ChatLine(line, getUserForID(sender), onClick);
						rawLine.setRaw(true);
						localGUI.showLine(rawLine);
					}
				} catch (final Exception e) {
					log("Exception in showLineOnGUI", e); //$NON-NLS-1$
				}
			}
		});
	}

	public static class SharedMarker implements Serializable {
		private static final long serialVersionUID = 7419507867486828728L;
		String message = null;
		Integer offset = null;
		Integer length = null;

		public SharedMarker(String message, Integer offset, Integer length) {
			this.message = message;
			this.offset = offset;
			this.length = length;
		}

		public String getMessage() {
			return message;
		}

		public Integer getOffset() {
			return offset;
		}

		public Integer getLength() {
			return length;
		}

		public String toString() {
			final StringBuffer buf = new StringBuffer("SharedMarker["); //$NON-NLS-1$
			buf.append("message=").append(message).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
			buf.append("offset=").append(offset).append(";"); //$NON-NLS-1$ //$NON-NLS-2$
			buf.append("length=").append(length).append("]"); //$NON-NLS-1$ //$NON-NLS-2$
			return buf.toString();
		}
	}

	public void sendAddMarkerForFile(User touser, String resourceName, int offset, int length) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_ADD_MARKER_FOR_FILE_MSG, getUser(), resourceName, new SharedMarker(Messages.EclipseCollabSharedObject_MARKER_NAME, new Integer(offset), new Integer(length)));
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception on sendAddMarkerForFile to " + touser, e); //$NON-NLS-1$
		}
	}

	public void sendOpenAndSelectForFile(User touser, String resourceName, int offset, int length) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_OPEN_AND_SELECT_FOR_FILE_MSG, getUser(), resourceName, new SharedMarker(Messages.EclipseCollabSharedObject_MARKER_NAME, new Integer(offset), new Integer(length)));
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception on sendAddMarkerForFile to " + touser, e); //$NON-NLS-1$
		}
	}

	public void sendLaunchEditorForFile(User touser, String resourceName) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_LAUNCH_EDITOR_FOR_FILE_MSG, getUser(), resourceName);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception on sendLaunchEditorForFile to " + touser, e); //$NON-NLS-1$
		}
	}

	protected Runnable createOpenEditorAndSelectForFileRunnable(final String resourceName, final SharedMarker marker) {
		final Integer offset = marker.getOffset();
		final Integer length = marker.getLength();
		return new Runnable() {
			public void run() {
				final IWorkbench wb = PlatformUI.getWorkbench();
				final IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				final IFile file = getIFileForResource(ww, resourceName);
				if (file != null) {
					final EditorHelper eh = new EditorHelper(ww);
					try {
						eh.openAndSelectForFile(file, (offset == null) ? 0 : offset.intValue(), (length == null) ? 0 : length.intValue());
					} catch (final Exception e) {
						log("Exception in openEditorAndSelectForFile", e); //$NON-NLS-1$
					}
				}
			}
		};
	}

	protected IFile getIFileForResource(IWorkbenchWindow ww, String resourceName) {
		final IFile file = getLocalFileForRemote(resourceName);
		if (file == null || !file.exists()) {
			MessageDialog.openInformation(ww.getShell(), Messages.EclipseCollabSharedObject_CANNOT_OPEN_EDITOR_TITLE, NLS.bind(Messages.EclipseCollabSharedObject_CANNOT_OPEN_EDITOR_MESSAGE, resourceName));
			return null;
		}
		return file;
	}

	protected Runnable createOpenEditorForFileRunnable(final String resourceName) {
		return new Runnable() {
			public void run() {
				final IWorkbench wb = PlatformUI.getWorkbench();
				final IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				final IFile file = getIFileForResource(ww, resourceName);
				if (file != null) {
					final EditorHelper eh = new EditorHelper(ww);
					try {
						eh.openEditorForFile(file);
					} catch (final Exception e) {
						log("Exception in openEditorAndSelectForFile", e); //$NON-NLS-1$
					}
				}
			}
		};
	}

	protected void addMarkerForFile(final IFile file, final SharedMarker marker) {
		if (file == null) {
			return;
		}
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				final IWorkbench wb = PlatformUI.getWorkbench();
				final IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				final EditorHelper eh = new EditorHelper(ww);
				try {
					eh.openAndAddMarkerForFile(file, marker);
				} catch (final Exception e) {
					log("Exception in addMarkerForFile", e); //$NON-NLS-1$
				}
			}
		});
	}

	protected void handleAddMarkerForFile(final User fromuser, final String resourceName, SharedMarker marker) {
		addMarkerForFile(getLocalFileForRemote(resourceName), marker);
	}

	protected void handleOpenAndSelectForFile(final User fromuser, final String resourceName, SharedMarker marker) {
		final User local = getUserForID(fromuser.getUserID());
		if (local != null) {
			final Runnable runnable = createOpenEditorAndSelectForFileRunnable(resourceName, marker);
			showEventInChatOutput(fromuser, resourceName, marker, runnable);
			verifyAndOpenEditorLocally(fromuser, resourceName, runnable);
		}
	}

	protected boolean isLocalUser(User fromuser) {
		if (fromuser != null && fromuser.getUserID().equals(getUser().getUserID()))
			return true;
		return false;
	}

	protected void verifyAndOpenEditorLocally(final User fromuser, final String resourceName, final Runnable runnable) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (isLocalUser(fromuser)) {
					runnable.run();
				} else {
					if (showSharedEditorEventsImmediately()) {
						if (!askUserToDisplaySharedEditorEvents() || MessageDialog.openQuestion(null, Messages.EclipseCollabSharedObject_DIALOG_OPEN_SHARED_EDITOR_TEXT, NLS.bind(Messages.EclipseCollabSharedObject_OPEN_SHARED_EDITOR_QUESTION, resourceName, fromuser.getNickname()))) {
							runnable.run();
						}
					}
				}
			}
		});
	}

	protected void handleLaunchEditorForFile(final User fromuser, final String resourceName) {
		final User local = getUserForID(fromuser.getUserID());
		if (local != null) {
			final Runnable runnable = createOpenEditorForFileRunnable(resourceName);
			showEventInChatOutput(fromuser, resourceName, null, runnable);
			verifyAndOpenEditorLocally(fromuser, resourceName, runnable);
		}
	}

	protected boolean showSharedEditorEventsImmediately() {
		return ClientPlugin.getDefault().getPreferenceStore().getBoolean(ClientPlugin.PREF_SHAREDEDITOR_PLAY_EVENTS_IMMEDIATELY);
	}

	protected boolean askUserToDisplaySharedEditorEvents() {
		return ClientPlugin.getDefault().getPreferenceStore().getBoolean(ClientPlugin.PREF_SHAREDEDITOR_ASK_RECEIVER);
	}

	protected void showEventInChatOutput(User fromuser, String resourceName, SharedMarker marker, Runnable runnable) {
		if (localGUI != null) {
			showRawLine(fromuser.getUserID(), createDisplayStringForEditorOpen(resourceName, marker), runnable);
		}
	}

	protected String createDisplayStringForEditorOpen(String resourceName, SharedMarker marker) {
		return EclipseCollabHyperlinkDetector.createDisplayStringForEditorOpen(resourceName, marker);
	}

	protected IFile getLocalFileForRemote(String file) {
		final IResource res = getResource();
		if (res instanceof IWorkspaceRoot) {
			return ((IWorkspaceRoot) res).getFile(new Path(file));
		}
		IFile aFile = null;
		final IProject proj = res.getProject();
		if (proj == null) {
			// workspace
			final IWorkspaceRoot myWorkspaceRoot = ResourcesPlugin.getWorkspace().getRoot();
			aFile = myWorkspaceRoot.getFile(new Path(file));
		} else {
			aFile = proj.getFile(file);
		}
		return aFile;
	}

	public void sendShowViewWithID(User touser, String id, String secID, Integer mode) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_SHOW_VIEW_WITH_ID_MSG, getUser(), id, secID, mode);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception on handleShowViewWithID to " + touser, e); //$NON-NLS-1$
		}
	}

	public void sendShowView(User touser, String id) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			final SharedObjectMsg m = SharedObjectMsg.createMsg(null, HANDLE_SHOW_VIEW_MSG, getUser(), id);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (final Exception e) {
			log("Exception on sendCVSProjectUpdateRequest to " + touser, e); //$NON-NLS-1$
		}
	}

	protected void handleShowViewWithID(User fromUser, final String id, final String secID, final Integer mode) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					showViewWithID(id, secID, mode.intValue());
				} catch (final Exception e) {
					log("Exception in showing view id=" + id + ";secID=" + secID + ";mode=" + mode, e); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
				}
			}
		});
	}

	protected void handleShowView(User fromUser, final String id) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					showView(id);
				} catch (final Exception e) {
					log("Exception in showing view id=" + id, e); //$NON-NLS-1$
				}
			}
		});
	}

	protected IViewPart showViewWithID(String id, String secID, int mode) throws PartInitException {
		final IWorkbenchWindow ww = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		final IWorkbenchPage wp = ww.getActivePage();
		if (wp == null)
			throw new PartInitException("workbench page is null"); //$NON-NLS-1$
		return wp.showView(id, secID, mode);
	}

	protected IViewPart showView(String id) throws PartInitException {
		final IWorkbenchWindow ww = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		final IWorkbenchPage wp = ww.getActivePage();
		if (wp == null)
			throw new PartInitException("workbench page is null"); //$NON-NLS-1$
		return wp.showView(id);
	}

	public FileReceiverUI getFileReceiverUI(EclipseFileTransfer transfer, FileTransferParams params) {
		return new FileReceiverUI() {
			public void receiveStart(ID from, File aFile, long length, float rate) {
				final User user = getUserForID(from);
				String nick = Messages.EclipseCollabSharedObject_UNKNOWN_USERNAME;
				if (user != null) {
					nick = user.getNickname();
				}
				showRawLine(from, NLS.bind(Messages.EclipseCollabSharedObject_FILE_TRANSFER_RECEIVING, nick, aFile.getName()), null);
			}

			public void receiveData(ID from, File aFile, int dataLength) {
			}

			public void receiveDone(ID from, File aFile, Exception e) {
				final User user = getUserForID(from);
				String nick = Messages.EclipseCollabSharedObject_UNKNOWN_USERNAME;
				if (user != null) {
					nick = user.getNickname();
				}
				showRawLine(from, NLS.bind(Messages.EclipseCollabSharedObject_FILE_TRANSFER_RECEIVED, new Object[] {aFile.getName(), nick, getLocalFullDownloadPath()}), null);
				refreshProject();
			}
		};
	}

	public void updateTreeDisplay(final TreeItem item) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				if (localGUI != null)
					localGUI.updateTreeDisplay(localContainerID, item);
			}
		});
		// Send update message to all replicas
		sendUpdateTreeDisplay(null, item);
	}

	public ViewPart getViewPart() {
		if (localGUI == null)
			return null;
		return localGUI.getView();
	}

	public ID createObject(ID target, String classname, Map map) throws Exception {
		return createObject(target, new ReplicaSharedObjectDescription(Class.forName(classname), IDFactory.getDefault().createGUID(), config.getHomeContainerID(), map));
	}
}
 No newline at end of file