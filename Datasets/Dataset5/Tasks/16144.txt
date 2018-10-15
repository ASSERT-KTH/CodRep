final StringBuffer se = new StringBuffer("Shared selection on ");

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
package org.eclipse.ecf.example.collab.share;

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.Date;
import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.share.io.EclipseFileTransfer;
import org.eclipse.ecf.example.collab.share.io.FileTransferParams;
import org.eclipse.ecf.example.collab.ui.ChatLine;
import org.eclipse.ecf.example.collab.ui.FileReceiverUI;
import org.eclipse.ecf.example.collab.ui.LineChatClientView;
import org.eclipse.ecf.example.collab.ui.LineChatHandler;
import org.eclipse.ecf.example.collab.ui.LineChatView;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Control;
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
		LineChatHandler, EclipseProject {
	
	protected static final String SHARED_MARKER_TYPE = ClientPlugin.SHARED_MARKER_TYPE;
	protected static final String SHARED_MARKER_KEY = ClientPlugin.SHARED_MARKER_KEY;
	
	protected static final String CHAT_VIEW_ID = LineChatView.class.getName();
	protected static String DEFAULTTREETOPLABEL = "Presence";
	public static final String ECLIPSEOBJECTNAME = "chat";
	public static final String INIT_TEXT = "Collaboration for ";
	Date creationTime = new Date();
	String downloaddir = "";
	protected LineChatClientView localGUI;
	IResource localProject;
	User localUser;
	String localVersion = "";
	ID serverID;
	SharedObjectEventListener sessionListener;
	IWorkbenchWindow shellWindow;
	String treeTopLabel;
	String windowtitle = "Chat";
	URL[] projectCodebase = null;

	public EclipseCollabSharedObject() {
	}
	public EclipseCollabSharedObject(IResource proj, IWorkbenchWindow shell,
			User user, String downloaddir) {
		this.localProject = proj;
		this.shellWindow = shell;
		this.localUser = user;
		this.downloaddir = downloaddir;
		localGUI = createOutputView();
		if (localGUI == null)
			throw new NullPointerException(
					"Local GUI cannot be created...exiting");
	}
	public void activated(ID[] others) {
		super.activated(others);
		if (localGUI == null) {
			try {
				if (!getContext().isGroupManager())
					destroySelfLocal();
			} catch (Exception e) {
				debugdump(e, "Unable to check whether we are server instance");
				destroySelfLocal();
			}
		}
	}
	public void chatException(Exception e, String text) {
		debugdump(e, text);
	}
	public void chatGUIDestroy() {
		debugmsg("chatGUIDestroy()");
		if (sessionListener != null) {
			sessionListener.windowClosing();
		}
		destroySelf();
	}
	protected void checkRegisterProxyPolicy(String operation, User sender,
			String proxyClass) throws SecurityException {
		// by default let it through;
	}
	public void deactivated() {
		super.deactivated();
		synchronized (this) {
			if (localGUI != null) {
				localGUI.disposeClient();
				localGUI = null;
			}
		}
		if (sessionListener != null) {
			sessionListener = null;
		}
		if (shellWindow != null) {
			shellWindow = null;
		}
		if (localProject != null) {
			localProject = null;
		}
	}
	public void debugdump(Exception e, String aString) {
		ClientPlugin.log(aString,e);
	}
	public void debugmsg(String aString) {
		// ClientPlugin.log(aString);
	}
	public void destroySelf() {
		// Make sure we disconnect
		try {
			if (isHost()) {
				leaveGroup();
			}
		} catch (Exception e) {
			debugdump(e, "Exception in destroySelf");
		}
		// Destroy self
		super.destroySelfLocal();
	}
	public String getDownloaddir(String dir) {
		return downloaddir;
	}
	public SharedObjectEventListener getListener() {
		return sessionListener;
	}
	public String getLocalFullProjectPath() {
		String eclipseDir = null;
		try {
			eclipseDir = Platform.getLocation().toOSString();
		} catch (Exception e) {
			debugdump(e,
					"EclipseCollabSharedObject.  Exception getting local project path");
		}
		if (eclipseDir == null) {
			eclipseDir = ".";
		}
		String projectDir = null;
		if (getResource() == null) {
			projectDir = downloaddir;
		} else {
			projectDir = getResource().getFullPath().toOSString();
		}
		File fresult = new File(eclipseDir, projectDir);
		return fresult.getAbsolutePath();
	}
	public String getLocalFullDownloadPath() {
		String projectPath = getLocalFullProjectPath();
		File downloadpath = new File(projectPath, downloaddir);
		return downloadpath.getAbsolutePath();
	}
	public ID getObjectID() {
		return getID();
	}
	protected LineChatClientView createOutputView() {
		final String pn = (localProject == null || localProject.getName()
				.trim().equals("")) ? "<workspace>" : localProject.getName();
		final String init = INIT_TEXT + pn + "\n\n";
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (LineChatView.isDisposed())
						showView();
					localGUI = LineChatView.makeClientView(
							EclipseCollabSharedObject.this, pn, init,
							getLocalFullDownloadPath());
				} catch (Exception e) {
					debugdump(e,
							"Exception creating output window in getOutputWindow");
				}
			}
		});
		return localGUI;
	}
	public IResource getResource() {
		return localProject;
	}
	protected SharedObjectDescription getReplicaDescription(ID remoteID) {
		// no replication...depend upon clients to create
		// local instance of their own copy of this object...with local
		// data.
		return null;
	}
	public ID getServerID() {
		return serverID;
	}
	public String getTreeTopLabel() {
		return DEFAULTTREETOPLABEL;
	}
	public ID getUniqueID() {
		try {
			return getLocalContainerID();
		} catch (Exception e) {
			debugdump(e, "Exception getting unique id");
			return null;
		}
	}
	public User getUser() {
		return localUser;
	}
	public User getUserForID(final ID user) {
		if (localGUI != null) {
			return localGUI.getUser(user);
		}
		return null;
	}
	public String getUserName() {
		return localUser.getNickname();
	}
	public String getVersionString() {
		return localVersion;
	}
	public String getWindowTitle() {
		return windowtitle;
	}
	public IWorkbenchWindow getWorkbenchWindow() {
		return shellWindow;
	}
	// SharedObjectMsg handlers
	protected void handleCreateObject(SharedObjectDescription cons) {
		try {
			makeObject(cons.getID(), cons.getClassname(), cons.getProperties());
		} catch (Exception e) {
			debugdump(e, "Exception creating local object " + cons);
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
			debugdump(e, "Exception checking for membership");
		}
		if (add) {
			boolean addUserResult = false;
			if (localGUI != null) {
				addUserResult = localGUI.addUser(user);
			}
			// If addUserResult is false, it means that this is a new user
			// And we need to report our own existence to them
			if (addUserResult) {
				sendNotifyUserAdded();
			}
		}
	}
	protected void handleRegisterProxy(User sender, String proxyClass,
			String name) {
		if (sender == null || proxyClass == null || name == null)
			throw new NullPointerException("sender or proxyClass is null");
		try {
			checkRegisterProxyPolicy("register", sender, proxyClass);
		} catch (SecurityException e) {
			debugdump(e, "SecurityException with registering Eclipse proxy");
			throw e;
		}
		localRegisterProxy(sender, proxyClass, name);
	}
	protected void handleRequestUserUpdate(ID requestor) {
		sendUserUpdate(requestor);
	}
	protected void handleShowPrivateTextMsg(final User remote,
			final String aString) {
		// Show line on local interface
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						ChatLine line = new ChatLine(aString);
						line.setOriginator(remote);
						line.setPrivate(true);
						localGUI.showLine(line);
					}
				} catch (Exception e) {
					debugdump(e, "Exception in showLineOnGUI");
				}
			}
		});
	}
	protected void handleShowTextMsg(ID remote, String aString) {
		// Show line on local interface
		showLineOnGUI(remote, aString);
	}
	protected void handleUnregisterProxy(User sender, String name) {
		if (sender == null || name == null)
			throw new NullPointerException("sender or proxyClass is null");
		// loadClass and create instance if possible
		try {
			checkRegisterProxyPolicy("deregister", sender, name);
		} catch (SecurityException e) {
			debugdump(e, "SecurityException with deregistering Eclipse proxy");
			throw e;
		}
		localUnregisterProxy(sender, name);
	}
	protected void handleUpdateTreeDisplay(final ID fromID, final TreeItem item) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null)
						localGUI.updateTreeDisplay(fromID, item);
				} catch (Exception e) {
					debugdump(e, "Exception in showLineOnGUI");
				}
			}
		});
	}
	protected void handleUserUpdate(final User ud) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null)
						localGUI.changeUser(ud);
				} catch (Exception e) {
					debugdump(e, "Exception in showLineOnGUI");
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
					MessageDialog.openInformation(null, "Private Message from "
							+ sender.getNickname(), message);
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
			forwardMsgTo(null, SharedObjectMsg.makeMsg(null,
					"handleStartedTyping", localUser));
		} catch (Exception e) {
			debugdump(e, "Exception on sendStartedTyping to remote clients");
		}
	}
	public void inputText(String aString) {
		sendShowTextMsg(aString);
	}
	public boolean isHost() {
		return super.isHost();
	}
	public void joinGroup(ID remote, IConnectContext data)
			throws ContainerConnectException {
		ISharedObjectContext crs = getContext();
		if (crs == null) {
			throw new ContainerConnectException("Cannot join remote space "
					+ remote + ".  Have no local space access capability.");
		} else {
			if (remote != null) {
				// Do it.
				ChatLine line = new ChatLine();
				if (localGUI != null) {
					line.setText("Connecting to " + remote.getName());
					localGUI.showLine(line);
				}
				crs.connect(remote, data);
				if (localGUI != null) {
					line.setText("Connected to " + remote.getName());
					localGUI.showLine(line);
				}
				// Success
			} else {
				throw new ContainerConnectException("Invalid remote space ID "
						+ remote);
			}
		}
	}
	public void leaveGroup() {
		ISharedObjectContext crs = getContext();
		if (crs == null) {
		} else {
			// Do it.
			crs.disconnect();
		}
	}
	public URL[] getCodeBase() {
		return null;
	}
	public void localRegisterProxy(User sender, String proxyClass, String name) {
		EclipseProjectComponent ec = null;
		try {
			ClassLoader classLoader = getClass().getClassLoader();
			URL[] codeBase = getCodeBase();
			URLClassLoader ucl = new URLClassLoader(codeBase, classLoader);
			Class cl = Class.forName(proxyClass, true, ucl);
			ec = (EclipseProjectComponent) cl.newInstance();
		} catch (Exception e) {
			debugdump(e,
					"Exception loading proxy class or creating proxy instance for user "
							+ sender.getNickname());
			throw new RuntimeException("Exception creating proxy instance", e);
		}
		try {
			ec.register(this, sender);
		} catch (Exception e) {
			debugdump(e, "Exception initializing EclipseProjectComponent");
			throw new RuntimeException(
					"Exception initializing EclipseProjectComponent", e);
		}
		// OK, we have new instance...now we add it to our registered proxies
		registerProxy(ec, name, EclipseProjectComponent.INVOKE_METHOD_NAME);
	}
	public void localUnregisterProxy(User ud, String name) {
		MsgMap m = null;
		Object removed = null;
		synchronized (msgMapLock) {
			// Get entry (if exists)
			m = (MsgMap) ((msgMap == null) ? null : (msgMap.get(name)));
			if (m == null)
				throw new RuntimeException(
						"deregisterProxy: No proxy registered for " + name);
			// Then remove
			removed = msgMap.remove(name);
		}
		if (removed != null) {
			try {
				MsgMap mm = (MsgMap) removed;
				EclipseProjectComponent ec = (EclipseProjectComponent) mm
						.getObject();
				// Call it to give it a chance to clean up
				if (ec != null)
					ec.deregister(this);
			} catch (Exception e) {
				debugdump(e, "Exception deregistering component with name "
						+ name + " with User " + ud);
			}
		}
	}
	public Object getObject(ID obj) {
		ISharedObjectContext crs = getContext();
		if (crs == null)
			return null;
		return crs.getSharedObjectManager().getSharedObject(obj);
	}
	public void makeProxyObject(ID target, String proxyClass, String name) {
		ID[] targets = new ID[1];
		targets[0] = target;
		if (name == null)
			name = proxyClass;
		registerEclipseProxy((target == null), targets, proxyClass, name);
	}
	public void memberAdded(ID member) {
		if (sessionListener != null) {
			sessionListener.memberAdded(member);
		}
		super.memberAdded(member);
		sendNotifyUserAdded();
	}
	public void memberRemoved(final ID member) {
		if (sessionListener != null) {
			sessionListener.memberRemoved(member);
		}
		super.memberRemoved(member);
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						localGUI.removeUser(member);
					}
				} catch (Exception e) {
					debugdump(e, "Exception in showLineOnGUI");
				}
			}
		});
	}
	public void messageProxyObject(ID target, String classname, String meth,
			Object[] args) {
		SharedObjectMsg m = SharedObjectMsg.makeMsg(null, classname, meth,
				(Object[]) args);
		try {
			forwardMsgTo(target, m);
			if (target == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception sending message to proxy object");
		}
	}
	public void otherActivated(ID object) {
		if (sessionListener != null) {
			sessionListener.otherActivated(object);
		}
		super.otherActivated(object);
	}
	public void otherDeactivated(ID object) {
		if (sessionListener != null) {
			sessionListener.otherDeactivated(object);
		}
		super.otherDeactivated(object);
	}
	public void refreshProject() {
		if (localProject != null) {
			try {
				localProject.refreshLocal(IResource.DEPTH_INFINITE,
						new NullProgressMonitor());
			} catch (Exception e) {
				debugdump(e, "Exception refreshing project "
						+ localProject.getName());
			}
		}
	}
	public void registerEclipseProxy(boolean localAlso, ID[] toReceivers,
			String proxyClass, String name) {
		// first, do it locally if this is what is desired
		if (localAlso) {
			try {
				localRegisterProxy(localUser, proxyClass, name);
			} catch (Exception e) {
				debugdump(e, "Exception registering proxy class " + proxyClass
						+ " locally");
				throw new RuntimeException(
						"registerEclipseProxy.  Local registration failed", e);
			}
		}
		// Now send register message to appropriate receiver(s).
		if (toReceivers == null)
			sendRegisterProxy(null, proxyClass, name);
		else if (toReceivers.length == 1)
			sendRegisterProxy(toReceivers[0], proxyClass, name);
		else {
			for (int i = 0; i < toReceivers.length; i++) {
				try {
					sendRegisterProxy(toReceivers[i], proxyClass, name);
				} catch (Exception e) {
					debugdump(e, "Exception sending register proxy message to "
							+ toReceivers[i]);
				}
			}
		}
	}
	public void removeProxyObject(ID target, String name) {
		ID[] targets = new ID[1];
		targets[0] = target;
		unregisterEclipseProxy((target == null), targets, name);
	}
	// SharedObjectMsg senders
	public void sendNotifyUserAdded() {
		try {
			forwardMsgTo(null, SharedObjectMsg.makeMsg(null,
					"handleNotifyUserAdded", localUser));
		} catch (Exception e) {
			debugdump(e, "Exception on sendNotifyUserAdded to remote clients");
		}
	}
	public void sendPrivateMessageToUser(User touser, String msg) {
		try {
			forwardMsgTo(touser.getUserID(), SharedObjectMsg.makeMsg(null,
					"handleShowPrivateTextMsg", localUser, msg));
		} catch (Exception e) {
			debugdump(e,
					"Exception on sendShowPrivateTextMsg to remote clients");
		}
	}
	public void sendRegisterProxy(ID toID, String proxyClass, String name) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.makeMsg(null,
					"handleRegisterProxy", localUser, proxyClass, name));
		} catch (IOException e) {
			debugdump(e, "Exception sendRegisterProxy");
		}
	}
	public void sendRequestUserUpdate(ID requestTarget) {
		try {
			forwardMsgTo(requestTarget, SharedObjectMsg.makeMsg(null,
					"handleRequestUserUpdate", getUniqueID()));
		} catch (Exception e) {
			debugdump(e, "Exception on sendRequestUserUpdate to remote clients");
		}
	}
	public void sendCVSProjectUpdateRequest(User touser, String msg) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null,
					"handleCVSProjectUpdateRequest", getUser(), msg);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception on sendCVSProjectUpdateRequest to "
					+ touser);
		}
	}
	public boolean isCVSShared() {
		try {
			// return CVSWorkspaceRoot.isSharedWithCVS(getProject());
			return false;
		} catch (Exception e) {
			debugdump(e,"CVS Exception calling isSharedWithCVS in TeamUpdateAction");
			return false;
		}
	}
	protected void doCVSUpdateOperation(IResource proj, User fromUser) {
		/*
		 * IResource[] resources = new IResource[1]; resources[0] = proj; try {
		 * new UpdateOperation(getViewPart(), resources,
		 * Command.NO_LOCAL_OPTIONS, null).run(); } catch
		 * (InvocationTargetException e) { ClientPlugin.log("Exception calling
		 * update operation from user " + fromUser, e);
		 * CVSUIPlugin.openError(Display.getDefault().getActiveShell(), null,
		 * null, e); } catch (InterruptedException e) { }
		 */
	}
	protected void handleCVSProjectUpdateRequest(final User fromUser,
			final String msg) {
		final IResource proj = getResource();
		// If project doesn't actually exist, just return silently
		if (!proj.exists() || !isCVSShared())
			return;
		doCVSUpdateOperation(proj, fromUser);
	}
	public void sendRingMessageToUser(User user, String msg) {
		 ID receiver = null;
		if (user != null) {
			receiver = user.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null,
					"handleUserMessage", this.localUser, msg);
			forwardMsgTo(receiver, m);
			if (receiver == null)
				sendSelf(m);
		} catch (Exception e) {
			debugdump(e, "Exception on sendMessageToUser to " + user);
		}
	}
	public void sendShowTextMsg(String msg) {
		try {
			trace("sendShowTextMsg(" + msg + ")");
			forwardMsgTo(null, SharedObjectMsg.makeMsg(null,
					"handleShowTextMsg", getUniqueID(), msg));
		} catch (Exception e) {
			debugdump(e, "Exception on sendShowTextMsg to remote clients");
		}
	}
	public void sendUnregisterProxy(ID toID, String proxyClass) {
		try {
			forwardMsgTo(toID, SharedObjectMsg.makeMsg(null,
					"handleUnregisterProxy", localUser, proxyClass));
		} catch (IOException e) {
			debugdump(e, "Exception sendRegisterProxy");
		}
	}
	public void sendUpdateTreeDisplay(ID target, TreeItem item) {
		try {
			forwardMsgTo(target, SharedObjectMsg.makeMsg(null,
					"handleUpdateTreeDisplay", getUniqueID(), item));
		} catch (Exception e) {
			debugdump(e, "Exception on sendUpdateTreeDisplay to remote clients");
		}
	}
	public void sendUserUpdate(ID target) {
		try {
			forwardMsgTo(target, SharedObjectMsg.makeMsg(null,
					"handleUserUpdate", localUser));
		} catch (Exception e) {
			debugdump(e, "Exception on sendUserUpdate to remote clients");
		}
	}
	public void setListener(SharedObjectEventListener l) {
		sessionListener = l;
	}
	public void setServerID(ID server) {
		serverID = server;
	}
	public void setVersionString(String ver) {
		localVersion = ver;
	}
	public void setWindowTitle(String title) {
		windowtitle = title;
		synchronized (this) {
			if (localGUI != null) {
				localGUI.setTitle(title);
			}
		}
	}
	public void show(final boolean show) {
		if (localGUI != null) {
			Display.getDefault().syncExec(new Runnable() {
				public void run() {
					localGUI.setVisible(show);
					localGUI.toFront();
				}
			});
		}
	}
	public void showLineOnGUI(final ID remote, final String line) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null)
						localGUI.showLine(new ChatLine(line,
								getUserForID(remote)));
				} catch (Exception e) {
					debugdump(e, "Exception in showLineOnGUI");
				}
			}
		});
	}
	public void showRawLine(final ID sender, final String line, final Runnable onClick) {
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
					debugdump(e, "Exception in showLineOnGUI");
				}
			}
		});
	}
	public void showView() {
		try {
			showView(CHAT_VIEW_ID);
		} catch (Exception e) {
			debugdump(e, "Exception showing view");
		}
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
	public void sendAddMarkerForFile(User touser, String resourceName, int offset, int length) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null,
					"handleAddMarkerForFile", getUser(), resourceName, new SharedMarker("ECF marker",new Integer(offset), new Integer(length)));
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception on sendAddMarkerForFile to " + touser);
		}
	}
	public void sendOpenAndSelectForFile(User touser, String resourceName, int offset, int length) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null,
					"handleOpenAndSelectForFile", getUser(), resourceName, new SharedMarker("ECF marker",new Integer(offset), new Integer(length)));
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception on sendAddMarkerForFile to " + touser);
		}
	}
	public void sendLaunchEditorForFile(User touser, String resourceName) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null,
					"handleLaunchEditorForFile", getUser(), resourceName);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception on sendLaunchEditorForFile to " + touser);
		}
	}
	protected void openEditorForFile(final IFile file) {
		trace("openEditorForFile("+file+")");
		if (file == null) {
			return;
		}
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				IWorkbench wb = PlatformUI.getWorkbench();
				IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				EditorHelper eh = new EditorHelper(ww);
				try {
					eh.openEditorForFile(file);
				} catch (PartInitException e) {
					debugdump(e,"Exception in showEditorForFile");
				}
			}
		});
	}
	protected Runnable createOpenEditorAndSelectForFileRunnable(final String resourceName, final SharedMarker marker) {
		trace("openEditorAndSelectForFile("+resourceName+")");
		final Integer offset = marker.getOffset();
		final Integer length = marker.getLength();
		return new Runnable() {
			public void run() {
				IWorkbench wb = PlatformUI.getWorkbench();
				IWorkbenchWindow ww = wb.getActiveWorkbenchWindow();
				IFile file = getLocalFileForRemote(resourceName);
				if(file==null) {
					MessageDialog.openInformation(ww.getShell(), "Cannot open file", "The file was not found in your workspace.");
					return;
				}
				EditorHelper eh = new EditorHelper(ww);
				try {
					eh.openAndSelectForFile(file, (offset==null)?0:offset.intValue(), (length==null)?0:length.intValue());
				} catch (Exception e) {
					debugdump(e,"Exception in addMarkerForFile");
				}
			}
		};
	}
	protected void addMarkerForFile(final IFile file, final SharedMarker marker) {
		trace("addMarkerForFile("+file+")");
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
					debugdump(e,"Exception in addMarkerForFile");
				}
			}
		});
	}
	protected void handleAddMarkerForFile(final User fromuser,
			final String resourceName, SharedMarker marker) {
		trace("handleAddMarkerForFile(" + fromuser + "," + resourceName + ","+marker+")");
		addMarkerForFile(getLocalFileForRemote(resourceName),marker);
	}
	protected void handleOpenAndSelectForFile(final User fromuser,
			final String resourceName, SharedMarker marker) {
		trace("handleOpenAndSelectForFile(" + fromuser + "," + resourceName + ","+marker+")");
		Runnable runnable = createOpenEditorAndSelectForFileRunnable(resourceName, marker);
		showEventInChatOutput(fromuser,resourceName,marker, runnable);
		Display.getDefault().asyncExec(runnable);
	}
	protected void handleLaunchEditorForFile(final User fromuser,
			final String resourceName) {
		trace("handleLaunchEditorForFile(" + fromuser + "," + resourceName + ")");
		showEventInChatOutput(fromuser, resourceName, null, null);
		openEditorForFile(getLocalFileForRemote(resourceName));
	}
	protected void showEventInChatOutput(User fromuser, String resourceName, SharedMarker marker, Runnable runnable) {
		if (localGUI != null) {
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
			// XXX construct string for output
			final StringBuffer se = new StringBuffer("Share my selection on ");
			se.append(projectName).append(resourceName);
			if (marker != null) {
				se.append(" (");
				se.append(marker.getOffset()).append("-").append(marker.getOffset().intValue()+marker.getLength().intValue());
			}
			se.append(")");
			// XXX
			showRawLine(fromuser.getUserID(),se.toString(), runnable);
		}
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
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null,
					"handleShowViewWithID", getUser(), id, secID, mode);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception on handleShowViewWithID to " + touser);
		}
	}
	public void sendShowView(User touser, String id) {
		ID receiver = null;
		if (touser != null) {
			receiver = touser.getUserID();
		}
		try {
			SharedObjectMsg m = SharedObjectMsg.makeMsg(null, "handleShowView",
					getUser(), id);
			forwardMsgTo(receiver, m);
			if (receiver == null) {
				sendSelf(m);
			}
		} catch (Exception e) {
			debugdump(e, "Exception on sendCVSProjectUpdateRequest to "
					+ touser);
		}
	}
	protected void handleShowViewWithID(User fromUser, final String id,
			final String secID, final Integer mode) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					showViewWithID(id, secID, mode.intValue());
				} catch (Exception e) {
					debugdump(e, "Exception in showing view id=" + id
							+ ";secID=" + secID + ";mode=" + mode);
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
					debugdump(e, "Exception in showing view id=" + id);
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
			throw new NullPointerException("showViewWithID(" + id + ") "
					+ "workbench page is null");
		return wp.showView(id, secID, mode);
	}
	protected IViewPart showView(String id) throws PartInitException {
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
				.getActiveWorkbenchWindow();
		IWorkbenchPage wp = ww.getActivePage();
		if (wp == null)
			throw new NullPointerException("showView(" + id + ") "
					+ "workbench page is null");
		return wp.showView(id);
	}
	public void unregisterEclipseProxy(boolean localAlso, ID[] toReceivers,
			String name) {
		// first, do it locally if this is what is desired
		if (localAlso) {
			try {
				localUnregisterProxy(getUser(), name);
			} catch (Exception e) {
				debugdump(e, "Exception deregistering " + name + " locally");
				throw new RuntimeException(
						"deregisterEclipseProxy.  Local deregistration failed",
						e);
			}
		}
		// Now send register message to appropriate receiver(s).
		if (toReceivers == null)
			sendUnregisterProxy(null, name);
		else if (toReceivers.length == 1)
			sendUnregisterProxy(toReceivers[0], name);
		else {
			for (int i = 0; i < toReceivers.length; i++) {
				try {
					sendUnregisterProxy(toReceivers[i], name);
				} catch (Exception e) {
					debugdump(e, "Exception sending register proxy message to "
							+ toReceivers[i]);
				}
			}
		}
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
				showRawLine(from, "\t" + nick + " is sending you '"
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
						+ nick + ".  Stored in: " + getLocalFullDownloadPath(), null);
				refreshProject();
			}
		};
	}
	public void updateTreeDisplay(final TreeItem item) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				try {
					if (localGUI != null) {
						localGUI.updateTreeDisplay(getUniqueID(), item);
					}
				} catch (Exception e) {
					debugdump(e, "Exception in updateTreeDisplay");
				}
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
	public Control getTreeControl() {
		if (localGUI == null)
			return null;
		return localGUI.getTreeControl();
	}
	public Control getTextControl() {
		if (localGUI == null)
			return null;
		return localGUI.getTextControl();
	}
}
 No newline at end of file