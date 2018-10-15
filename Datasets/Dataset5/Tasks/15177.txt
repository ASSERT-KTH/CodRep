+ " has completed and placed in directory: "+getLocalFullDownloadPath());

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
import java.net.URL;
import java.net.URLClassLoader;
import java.util.Date;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.SharedObjectContainerJoinException;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.share.io.EclipseFileTransfer;
import org.eclipse.ecf.example.collab.share.io.FileTransferParams;
import org.eclipse.ecf.example.collab.ui.FileReceiverUI;
import org.eclipse.ecf.example.collab.ui.LineChatClientView;
import org.eclipse.ecf.example.collab.ui.LineChatHandler;
import org.eclipse.ecf.example.collab.ui.LineChatView;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

public class EclipseCollabSharedObject extends GenericSharedObject implements
        LineChatHandler, EclipseProject {
    protected static final String CHAT_VIEW_ID = LineChatView.class.getName();
    protected static String DEFAULTTREETOPLABEL = "Presence";
    public static final String ECLIPSEOBJECTNAME = "chat";
    public static final String INIT_TEXT = "Collaboration for '";
    Date creationTime = new Date();
    String downloaddir = "";
    protected LineChatClientView localGUI;
    IProject localProject;
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

    public EclipseCollabSharedObject(IProject proj, IWorkbenchWindow shell,
            User user, String downloaddir) {
        this.localProject = proj;
        this.shellWindow = shell;
        this.localUser = user;
        this.downloaddir = downloaddir;
        localGUI = getOutputWindow();
        if (localGUI == null)
            throw new NullPointerException(
                    "Local GUI cannot be created...exiting");
    }

    public void activated(ID[] others) {
        super.activated(others);
        if (localGUI == null) {
            try {
                if (!getContext().isGroupServer())
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
    }

    public void debugmsg(String aString) {
        // ClientPlugin.log(aString);
    }

    public void destroySelf() {
        // Make sure we disconnect
        try {
            if (isHost()) {
                try {
                    // try to disconnect
                    leaveGroup();
                } catch (Exception e) {
                    debugdump(e, "Exception leaving space");
                }
            }
        } catch (Exception e) {
            debugdump(e,"Exception in destroySelf");
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
        String result = null;
        try {
            eclipseDir = Platform.getLocation().toOSString();
        } catch (Exception e) {
            debugdump(e,
                    "EclipseCollabSharedObject.  Exception getting local project path");
        }
        if (eclipseDir==null) {
            eclipseDir = ".";
        }
        String projectDir = null;
        if (getProject()==null) {
            projectDir = downloaddir;
        } else {
            projectDir = getProject().getFullPath().toOSString();
        }
        File fresult = new File(eclipseDir,projectDir);
        return fresult.getAbsolutePath();
    }

    public String getLocalFullDownloadPath() {
        String projectPath = getLocalFullProjectPath();
        File downloadpath = new File(projectPath,downloaddir);
        return downloadpath.getAbsolutePath();
    }
    public ID getObjectID() {
        return getID();
    }

    protected LineChatClientView getOutputWindow() {
        final String pn = (localProject==null)?"<workspace>":localProject.getName();
        final String projectName = pn;
        final String init = INIT_TEXT + pn
                + "' project\n\n";
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                try {
                    if (LineChatView.isDisposed())
                        showView();
                    localGUI = LineChatView.makeClientView(
                            EclipseCollabSharedObject.this, projectName, init,
                            getLocalFullDownloadPath());
                } catch (Exception e) {
                    debugdump(e,
                            "Exception creating output window in getOutputWindow");
                }
            }
        });
        return localGUI;
    }

    public IProject getProject() {
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

    protected void handleShowPrivateTextMsg(final User remote, final String aString) {
        // Show line on local interface
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                try {
                    if (localGUI != null)
                        localGUI.showPrivate(remote.getUserID(), aString);
                } catch (Exception e) {
                    debugdump(e,
                            "Exception in showLineOnGUI");
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
        EclipseProjectComponent ec = null;
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
                    debugdump(e,
                            "Exception in showLineOnGUI");
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
                    debugdump(e,
                            "Exception in showLineOnGUI");
                }
            }
        });
    }

    protected void handleUserMessage(final User sender, String msg) {
        // Show line on local interface
        final String username = sender.getNickname();
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
                        MessageDialog.openInformation(null,
                                "Private Message from " + sender.getNickname(),
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

    public void joinGroup(ID remote, Object data)
            throws SharedObjectContainerJoinException {
        ISharedObjectContext crs = getContext();
        if (crs == null) {
            throw new SharedObjectContainerJoinException(
                    "Cannot join remote space " + remote
                            + ".  Have no local space access capability.");
        } else {
            if (remote != null) {
                // Do it.
                if (localGUI != null) {
                    String name = remote.getName();
                    localGUI.showLine(getID(), "Connecting to: " + name);
                }
                crs.joinGroup(remote, data);
                if (localGUI != null) {
                    localGUI.showLine(getID(), "Connected.");
                }
                // Success
            } else {
                throw new SharedObjectContainerJoinException(
                        "Invalid remote space ID " + remote);
            }
        }
    }

    public void leaveGroup() {
        ISharedObjectContext crs = getContext();
        if (crs == null) {
        } else {
            // Do it.
            crs.leaveGroup();
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
                    debugdump(e,
                            "Exception in showLineOnGUI");
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
            //return CVSWorkspaceRoot.isSharedWithCVS(getProject());
            return false;
        } catch (Exception e) {
            ClientPlugin
                    .log(
                            "CVS Exception calling isSharedWithCVS in TeamUpdateAction",
                            e);
            return false;
        }
    }

    protected void doCVSUpdateOperation(IProject proj, User fromUser) {
        /*
        IResource[] resources = new IResource[1];
        resources[0] = proj;
        try {
            new UpdateOperation(getViewPart(), resources,
                    Command.NO_LOCAL_OPTIONS, null).run();
        } catch (InvocationTargetException e) {
            ClientPlugin.log("Exception calling update operation from user "
                    + fromUser, e);
            CVSUIPlugin.openError(Display.getDefault().getActiveShell(), null,
                    null, e);
        } catch (InterruptedException e) {
        }
        */
    }

    protected void handleCVSProjectUpdateRequest(final User fromUser,
            final String msg) {
        final IProject proj = getProject();
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
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                try {
                    if (localGUI != null)
                        localGUI.showLine(remote, line);
                } catch (Exception e) {
                    debugdump(e,
                            "Exception in showLineOnGUI");
                }
            }
        });
    }

    public void showRawLine(final ID sender, final String line) {
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                try {
                    if (localGUI != null) {
                        localGUI.showRawLine(sender, line);
                    }
                } catch (Exception e) {
                    debugdump(e,
                            "Exception in showLineOnGUI");
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
                        + aFile.getName() + "'");
            }

            public void receiveData(ID from, File aFile, int dataLength) {
            }

            public void receiveDone(ID from, File aFile, Exception e) {
                User user = getUserForID(from);
                String nick = "<unknown>";
                if (user != null) {
                    nick = user.getNickname();
                }
                showRawLine(from, "\t'" + aFile.getName() + "' from " + nick
                        + " has arrived " + aFile.getAbsolutePath());
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
                    debugdump(e,
                            "Exception in updateTreeDisplay");
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