args);

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

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
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
import org.eclipse.ecf.internal.example.collab.ui.ChatLine;
import org.eclipse.ecf.internal.example.collab.ui.EditorHelper;
import org.eclipse.ecf.internal.example.collab.ui.FileReceiverUI;
import org.eclipse.ecf.internal.example.collab.ui.ImageWrapper;
import org.eclipse.ecf.internal.example.collab.ui.LineChatClientView;
import org.eclipse.ecf.internal.example.collab.ui.LineChatHandler;
import org.eclipse.ecf.internal.example.collab.ui.LineChatView;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

public class EclipseCollabSharedObject extends GenericSharedObject implements
		LineChatHandler {
	private static final String HANDLE_SHOW_VIEW_MSG = "handleShowView";
	private static final String HANDLE_SHOW_VIEW_WITH_ID_MSG = "handleShowViewWithID";
	private static final String HANDLE_LAUNCH_EDITOR_FOR_FILE_MSG = "handleLaunchEditorForFile";
	private static final String HANDLE_OPEN_AND_SELECT_FOR_FILE_MSG = "handleOpenAndSelectForFile";
	private static final String HANDLE_ADD_MARKER_FOR_FILE_MSG = "handleAddMarkerForFile";
	private static final String HANDLE_USER_UPDATE_MSG = "handleUserUpdate";
	private static final String HANDLE_UPDATE_TREE_DISPLAY_MSG = "handleUpdateTreeDisplay";
	private static final String HANDLE_UNREGISTER_PROXY_MSG = "handleUnregisterProxy";
	private static final String HANDLE_SHOW_TEXT_MSG = "handleShowTextMsg";
	private static final String HANDLE_SHOW_IMAGE_MSG = "handleShowImage";
	private static final String HANDLE_USER_MSG = "handleUserMessage";
	private static final String HANDLE_CVS_PROJECT_UPDATE_REQUEST_MSG = "handleCVSProjectUpdateRequest";
	private static final String HANDLE_REQUEST_USER_UPDATE_MSG = "handleRequestUserUpdate";
	private static final String HANDLE_REGISTER_PROXY_MSG = "handleRegisterProxy";
	private static final String HANDLE_SHOW_PRIVATE_TEXT_MSG = "handleShowPrivateTextMsg";
	private static final String HANDLE_NOTIFY_USER_ADDED_MSG = "handleNotifyUserAdded";
	private static final String HANDLE_STARTED_TYPING_MSG = "handleStartedTyping";

	public static final String SHARED_MARKER_TYPE = ClientPlugin.SHARED_MARKER_TYPE;
	public static final String SHARED_MARKER_KEY = ClientPlugin.SHARED_MARKER_KEY;
	public static final String ID = "chat";

	private static final String DEFAULT_WINDOW_TITLE = "Chat";

	private String windowTitle = DEFAULT_WINDOW_TITLE;
	private String downloadDirectory = "";
	private LineChatClientView localGUI = null;
	private IResource localResource = null;
	private User localUser = null;
	private String localVersion = "";
	private ID serverID = null;
	private SharedObjectEventListener sharedObjectEventListener = null;
	private IWorkbenchWindow workbenchWindow = null;

	public EclipseCollabSharedObject() {
	}

	public EclipseCollabSharedObject(IResource proj, IWorkbenchWindow window,
			User user, String downloaddir) {
		this.localResource = proj;
		this.workbenchWindow = window;
		this.localUser = user;
		this.downloadDirectory = downloaddir;
		createOutputView();
		Assert.isNotNull(localGUI, "Local GUI cannot be created...exiting");
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
		} catch (Exception e) {
			log("Exception in destroySelf", e);
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
		} catch (IllegalStateException e) {
			log("Exception getting local resource path", e);
		}
		if (eclipseDir == null)
			eclipseDir = ".";
		String projectDir = (getResource() == null) ? downloadDirectory
				: getResource().getFullPath().toOSString();
		return new File(eclipseDir, projectDir).getAbsolutePath();
	}

	public String getLocalFullDownloadPath() {
		return new File(getLocalFullProjectPath(), downloadDirectory)
				.getAbsolutePath();
	}

	protected void createOutputView() {
		final String projectName = (localResource == null || localResource
				.getName().trim().equals("")) ? "<workspace>" : localResource
				.getName();
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					IWorkbenchWindow ww = PlatformUI.getWorkbench()
							.getActiveWorkbenchWindow();
					IWorkbenchPage wp = ww.getActivePage();
					wp.showView(LineChatView.VIEW_ID);
					LineChatView.setViewName(NLS.bind("Collaboration: {0}",
							localUser.getNickname()));
					localGUI = LineChatView.createClientView(
							EclipseCollabSharedObject.this, projectName, NLS
									.bind("Collaboration for {0} \n\n",
											projectName),
							getLocalFullDownloadPath());
				} catch (Exception e) {
					log("Exception creating LineChatView", e);
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
		return "Presence";
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
		} catch (Exception e) {
			log("Exception creating local object", e);
		}
	}

	public void handleNotifyUserAdded(User user) {
		boolean add = false;
		try {
			ID[] members = getContext().getGroupMemberIDs();
			for (int i = 0; i < members.length; i++) {
				if (members[i].equals(user.getUserID())) {
					add = true;
					break;
				}
			}
		} catch (Exception e) {
			log("Exception checking for membership", e);
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

	protected void handleShowPrivateTextMsg(final User remote,
			final String aString) {
		// Show line on local interface
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						ChatLine line = new ChatLine(aString);
						line.setOriginator(remote);
						line.setPrivate(true);
						localGUI.showLine(line);
						localGUI.toFront();
					}
				} catch (Exception e) {
					log("Exception in showLineOnGUI", e);
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
				} catch (Exception e) {
					log("Exception in showLineOnGUI", e);
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
				} catch (Exception e) {
					log("Exception in showLineOnGUI", e);
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
					Shell[] shells = Display.getDefault().getShells();
					if (shells != null && shells.length > 0) {
						shells[0].setActive();
					}
					MessageDialog.openInformation(null, NLS.bind(
							"Private Message from {0}", sender.getNickname()),
							message);
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
			forwardMsgTo(null, SharedObjectMsg.createMsg(null,
					HANDLE_STARTED_TYPING_MSG, localUser));
		} catch (Exception e) {
			log("Exception on sendStartedTyping to remote clients", e);
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
				} catch (Exception e) {
					log("Exception in showLineOnGUI", e);
				}
			}
		});
	}

	public void messageProxyObject(ID target, String classname, String meth,
			Object[] args) {
		SharedObjectMsg m = SharedObjectMsg.createMsg(null, classname, meth,
				(Object[]) args);
		try {
			forwardMsgTo(target, m);
			if (target == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception sending message to proxy object", e);
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
				localResource.refreshLocal(IResource.DEPTH_INFINITE,
						new NullProgressMonitor());
			} catch (Exception e) {
				log("Exception refreshing resource " + localResource.getName(),
						e);
			}
		}
	}

	// SharedObjectMsg senders
	public void sendNotifyUserAdded() {
		try {
			forwardMsgTo(null, SharedObjectMsg.createMsg(null,
					HANDLE_NOTIFY_USER_ADDED_MSG, localUser));
		} catch (Exception e) {
			log("Exception on sendNotifyUserAdded to remote clients", e);
		}
	}

	public void sendPrivateMessageToUser(User touser, String msg) {
		try {
			forwardMsgTo(touser.getUserID(), SharedObjectMsg.createMsg(null,
					HANDLE_SHOW_PRIVATE_TEXT_MSG, localUser, msg));
		} catch (Exception e) {
			log("Exception on sendShowPrivateTextMsg to remote clients", e);
		}
	}

	public void sendRegisterProxy(ID toID, String proxyClass, String name) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.createMsg(null,
					HANDLE_REGISTER_PROXY_MSG, localUser, proxyClass, name));
		} catch (IOException e) {
			log("Exception sendRegisterProxy", e);
		}
	}

	public void sendRequestUserUpdate(ID requestTarget) {
		try {
			forwardMsgTo(requestTarget, SharedObjectMsg.createMsg(null,
					HANDLE_REQUEST_USER_UPDATE_MSG, localContainerID));
		} catch (Exception e) {
			log("Exception on sendRequestUserUpdate to remote clients", e);
		}
	}

	public void sendCVSProjectUpdateRequest(User touser, String msg) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_CVS_PROJECT_UPDATE_REQUEST_MSG, getUser(), msg);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception on sendCVSProjectUpdateRequest to " + touser, e);
		}
	}

	public boolean isCVSShared() {
		try {
			// return CVSWorkspaceRoot.isSharedWithCVS(getProject());
			return false;
		} catch (Exception e) {
			log("CVS Exception calling isSharedWithCVS in TeamUpdateAction", e);
			return false;
		}
	}

	public void sendRingMessageToUser(User user, String msg) {
		ID receiver = null;
		if (user != null) {
			receiver = user.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_USER_MSG, this.localUser, msg);
			forwardMsgTo(receiver, m);
			if (receiver == null)
				sendSelf(m);
		} catch (Exception e) {
			log("Exception on sendMessageToUser to " + user, e);
		}
	}

	public void sendImage(ImageWrapper wrapper) {
		try {
			forwardMsgTo(null, SharedObjectMsg.createMsg(null,
					HANDLE_SHOW_IMAGE_MSG, localContainerID, wrapper));
		} catch (Exception e) {
			log("Exception on sendShowTextMsg to remote clients", e);
		}
	}

	protected void handleShowImage(ID id, ImageWrapper wrapper) {
		final Display display = localGUI.getTextControl().getDisplay();
		final Image image = new Image(display, wrapper.createImageData());
		display.asyncExec(new Runnable() {
			public void run() {
				Shell shell = new Shell(display);
				shell.setBounds(image.getBounds());
				shell.addDisposeListener(new DisposeListener() {
					public void widgetDisposed(DisposeEvent e) {
						image.dispose();
					}
				});

				shell.addPaintListener(new PaintListener() {
					public void paintControl(PaintEvent e) {
						e.gc.drawImage(image, 0, 0);
					}
				});

				shell.open();
			}
		});
	}

	public void sendShowTextMsg(String msg) {
		try {
			forwardMsgTo(null, SharedObjectMsg.createMsg(null,
					HANDLE_SHOW_TEXT_MSG, localContainerID, msg));
		} catch (Exception e) {
			log("Exception on sendShowTextMsg to remote clients", e);
		}
	}

	public void sendUnregisterProxy(ID toID, String proxyClass) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.createMsg(null,
					HANDLE_UNREGISTER_PROXY_MSG, localUser, proxyClass));
		} catch (IOException e) {
			log("Exception sendRegisterProxy", e);
		}
	}

	public void sendUpdateTreeDisplay(ID target, TreeItem item) {
		try {
			forwardMsgTo(target, SharedObjectMsg.createMsg(null,
					HANDLE_UPDATE_TREE_DISPLAY_MSG, localContainerID, item));
		} catch (Exception e) {
			log("Exception on sendUpdateTreeDisplay to remote clients", e);
		}
	}

	public void sendUserUpdate(ID target) {
		try {
			forwardMsgTo(target, SharedObjectMsg.createMsg(null,
					HANDLE_USER_UPDATE_MSG, localUser));
		} catch (Exception e) {
			log("Exception on sendUserUpdate to remote clients", e);
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
					IWorkbenchWindow ww = PlatformUI.getWorkbench()
							.getActiveWorkbenchWindow();
					IWorkbenchPage wp = ww.getActivePage();
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
						localGUI.showLine(new ChatLine(line,
								getUserForID(remote)));
				} catch (Exception e) {
					log("Exception in showLineOnGUI", e);
				}
			}
		});
	}

	public void showRawLine(final ID sender, final String line,
			final Runnable onClick) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						ChatLine rawLine = new ChatLine(line,
								getUserForID(sender), onClick);
						rawLine.setRaw(true);
						localGUI.showLine(rawLine);
					}
				} catch (Exception e) {
					log("Exception in showLineOnGUI", e);
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
			StringBuffer buf = new StringBuffer("SharedMarker[");
			buf.append("message=").append(message).append(";");
			buf.append("offset=").append(offset).append(";");
			buf.append("length=").append(length).append("]");
			return buf.toString();
		}
	}

	public void sendAddMarkerForFile(User touser, String resourceName,
			int offset, int length) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_ADD_MARKER_FOR_FILE_MSG, getUser(), resourceName,
					new SharedMarker("ECF marker", new Integer(offset),
							new Integer(length)));
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception on sendAddMarkerForFile to " + touser, e);
		}
	}

	public void sendOpenAndSelectForFile(User touser, String resourceName,
			int offset, int length) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_OPEN_AND_SELECT_FOR_FILE_MSG, getUser(),
					resourceName, new SharedMarker("ECF marker", new Integer(
							offset), new Integer(length)));
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception on sendAddMarkerForFile to " + touser, e);
		}
	}

	public void sendLaunchEditorForFile(User touser, String resourceName) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_LAUNCH_EDITOR_FOR_FILE_MSG, getUser(), resourceName);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception on sendLaunchEditorForFile to " + touser, e);
		}
	}

	protected Runnable createOpenEditorAndSelectForFileRunnable(
			final String resourceName, final SharedMarker marker) {
		final Integer offset = marker.getOffset();
		final Integer length = marker.getLength();
		return new Runnable() {
			public void run() {
				IWorkbench wb = PlatformUI.getWorkbench();
				IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				IFile file = getIFileForResource(ww, resourceName);
				if (file != null) {
					EditorHelper eh = new EditorHelper(ww);
					try {
						eh.openAndSelectForFile(file, (offset == null) ? 0
								: offset.intValue(), (length == null) ? 0
								: length.intValue());
					} catch (Exception e) {
						log("Exception in openEditorAndSelectForFile", e);
					}
				}
			}
		};
	}

	protected IFile getIFileForResource(IWorkbenchWindow ww, String resourceName) {
		IFile file = getLocalFileForRemote(resourceName);
		if (file == null || !file.exists()) {
			MessageDialog.openInformation(ww.getShell(), "Cannot open editor",
					"'" + resourceName + "' was not found in your workspace.");
			return null;
		}
		return file;
	}

	protected Runnable createOpenEditorForFileRunnable(final String resourceName) {
		return new Runnable() {
			public void run() {
				IWorkbench wb = PlatformUI.getWorkbench();
				IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				IFile file = getIFileForResource(ww, resourceName);
				if (file != null) {
					EditorHelper eh = new EditorHelper(ww);
					try {
						eh.openEditorForFile(file);
					} catch (Exception e) {
						log("Exception in openEditorAndSelectForFile", e);
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
				IWorkbench wb = PlatformUI.getWorkbench();
				IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				EditorHelper eh = new EditorHelper(ww);
				try {
					eh.openAndAddMarkerForFile(file, marker);
				} catch (Exception e) {
					log("Exception in addMarkerForFile", e);
				}
			}
		});
	}

	protected void handleAddMarkerForFile(final User fromuser,
			final String resourceName, SharedMarker marker) {
		addMarkerForFile(getLocalFileForRemote(resourceName), marker);
	}

	protected void handleOpenAndSelectForFile(final User fromuser,
			final String resourceName, SharedMarker marker) {
		User local = getUserForID(fromuser.getUserID());
		if (local != null) {
			Runnable runnable = createOpenEditorAndSelectForFileRunnable(
					resourceName, marker);
			showEventInChatOutput(fromuser, resourceName, marker, runnable);
			verifyAndOpenEditorLocally(fromuser, resourceName, runnable);
		}
	}

	protected boolean isLocalUser(User fromuser) {
		if (fromuser != null
				&& fromuser.getUserID().equals(getUser().getUserID()))
			return true;
		return false;
	}

	protected void verifyAndOpenEditorLocally(final User fromuser,
			final String resourceName, final Runnable runnable) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (isLocalUser(fromuser)) {
					runnable.run();
				} else {
					if (showSharedEditorEventsImmediately()) {
						if (!askUserToDisplaySharedEditorEvents()
								|| MessageDialog.openQuestion(null,
										"Open Shared Editor?",
										"Open shared editor for '"
												+ resourceName + "' from "
												+ fromuser.getNickname() + "?")) {
							runnable.run();
						}
					}
				}
			}
		});
	}

	protected void handleLaunchEditorForFile(final User fromuser,
			final String resourceName) {
		final User local = getUserForID(fromuser.getUserID());
		if (local != null) {
			final Runnable runnable = createOpenEditorForFileRunnable(resourceName);
			showEventInChatOutput(fromuser, resourceName, null, runnable);
			verifyAndOpenEditorLocally(fromuser, resourceName, runnable);
		}
	}

	protected boolean showSharedEditorEventsImmediately() {
		return ClientPlugin.getDefault().getPreferenceStore().getBoolean(
				ClientPlugin.PREF_SHAREDEDITOR_PLAY_EVENTS_IMMEDIATELY);
	}

	protected boolean askUserToDisplaySharedEditorEvents() {
		return ClientPlugin.getDefault().getPreferenceStore().getBoolean(
				ClientPlugin.PREF_SHAREDEDITOR_ASK_RECEIVER);
	}

	protected void showEventInChatOutput(User fromuser, String resourceName,
			SharedMarker marker, Runnable runnable) {
		if (localGUI != null) {
			showRawLine(fromuser.getUserID(), createDisplayStringForEditorOpen(
					resourceName, marker), runnable);
		}
	}

	protected String createDisplayStringForEditorOpen(String resourceName,
			SharedMarker marker) {
		IResource localRes = getResource();
		String projectName = "";
		if (localRes != null) {
			projectName = localRes.getName();
		}
		if (projectName.equals("")) {
			projectName = "<workspace>/";
		} else {
			projectName = projectName + "/";
		}
		final StringBuffer se = new StringBuffer(
				(marker == null) ? "open editor on " : "share selection on ");
		se.append(projectName).append(resourceName);
		if (marker != null) {
			se.append(" (");
			se.append(marker.getOffset()).append("-").append(
					marker.getOffset().intValue()
							+ marker.getLength().intValue());
			se.append(")");
		}
		return se.toString();
	}

	protected IFile getLocalFileForRemote(String file) {
		IResource res = getResource();
		IFile aFile = null;
		IProject proj = res.getProject();
		if (proj == null) {
			// workspace
			IWorkspaceRoot myWorkspaceRoot = ResourcesPlugin.getWorkspace()
					.getRoot();
			aFile = myWorkspaceRoot.getFile(new Path(file));
		} else {
			aFile = proj.getFile(file);
		}
		return aFile;
	}

	public void sendShowViewWithID(User touser, String id, String secID,
			Integer mode) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_SHOW_VIEW_WITH_ID_MSG, getUser(), id, secID, mode);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception on handleShowViewWithID to " + touser, e);
		}
	}

	public void sendShowView(User touser, String id) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.createMsg(null,
					HANDLE_SHOW_VIEW_MSG, getUser(), id);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			log("Exception on sendCVSProjectUpdateRequest to " + touser, e);
		}
	}

	protected void handleShowViewWithID(User fromUser, final String id,
			final String secID, final Integer mode) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					showViewWithID(id, secID, mode.intValue());
				} catch (Exception e) {
					log("Exception in showing view id=" + id + ";secID="
							+ secID + ";mode=" + mode, e);
				}
			}
		});
	}

	protected void handleShowView(User fromUser, final String id) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					showView(id);
				} catch (Exception e) {
					log("Exception in showing view id=" + id, e);
				}
			}
		});
	}

	protected IViewPart showViewWithID(String id, String secID, int mode)
			throws PartInitException {
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
				.getActiveWorkbenchWindow();
		IWorkbenchPage wp = ww.getActivePage();
		if (wp == null)
			throw new PartInitException("workbench page is null");
		return wp.showView(id, secID, mode);
	}

	protected IViewPart showView(String id) throws PartInitException {
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
				.getActiveWorkbenchWindow();
		IWorkbenchPage wp = ww.getActivePage();
		if (wp == null)
			throw new PartInitException("workbench page is null");
		return wp.showView(id);
	}

	public FileReceiverUI getFileReceiverUI(EclipseFileTransfer transfer,
			FileTransferParams params) {
		return new FileReceiverUI() {
			public void receiveStart(ID from, File aFile, long length,
					float rate) {
				User user = getUserForID(from);
				String nick = "<unknown>";
				if (user != null) {
					nick = user.getNickname();
				}
				showRawLine(from, "\t" + nick + " is sending you "
						+ aFile.getName() + "'", null);
			}

			public void receiveData(ID from, File aFile, int dataLength) {
			}

			public void receiveDone(ID from, File aFile, Exception e) {
				User user = getUserForID(from);
				String nick = "<unknown>";
				if (user != null) {
					nick = user.getNickname();
				}
				showRawLine(from, "\t'" + aFile.getName() + "' received from "
						+ nick + ".  Stored in: " + getLocalFullDownloadPath(),
						null);
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

	public ID createObject(ID target, String classname, Map map)
			throws Exception {
		return createObject(target, new ReplicaSharedObjectDescription(Class
				.forName(classname), IDFactory.getDefault().createGUID(),
				config.getHomeContainerID(), map));
	}
}
 No newline at end of file