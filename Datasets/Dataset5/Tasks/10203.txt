public static final String DEFAULT_SERVER_ID = "ecftcp://localhost:3282/server";

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

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Vector;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IWorkspace;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.SharedObjectContainerFactory;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.example.collab.share.SharedObjectEventListener;
import org.eclipse.ecf.example.collab.share.TreeItem;
import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;

public class Client {
    private static final int CONTAINER_DISPOSE = 1000;
    public static final String JOIN_TIME_FORMAT = "hh:mm:ss a z";
    public static final String GENERIC_CONTAINER_CLIENT_NAME = "org.eclipse.ecf.provider.generic.Client";
    public static final String GENERIC_CONTAINER_SERVER_NAME = "org.eclipse.ecf.provider.generic.Server";
    public static final String DEFAULT_SERVER_ID = "ecftcp://localhost:3282//server";
    public static final String COLLAB_SHARED_OBJECT_ID = "chat";
    public static final String FILE_DIRECTORY = "received_files";
    public static final String USERNAME = System.getProperty("user.name");
    public static final String ECFDIRECTORY = "ECF_" + FILE_DIRECTORY + "/";
    static ISharedObjectContainer client = null;
    static EclipseCollabSharedObject sharedObject = null;
    static ID defaultGroupID = null;
    static ID groupID = null;
    static ID sharedObjectID = null;

    public Client() throws Exception {
        defaultGroupID = IDFactory.makeStringID(DEFAULT_SERVER_ID);
    }

    protected User getUserData(String containerType, ID clientID, String usernick, String proj) {
        Vector topElements = new Vector();
        String contType = containerType.substring(containerType.lastIndexOf(".")+1);
        topElements.add(new TreeItem("Project", proj));
        SimpleDateFormat sdf = new SimpleDateFormat(JOIN_TIME_FORMAT);
        topElements.add(new TreeItem("Join Time",sdf.format(new Date())));
        topElements.add(new TreeItem("Container Type",contType));
        return new User(clientID, usernick, topElements);
    }

    protected String getSharedFileDirectoryForProject(IProject proj) {
        String eclipseDir = Platform.getLocation().lastSegment();
        if (proj == null)
            return eclipseDir + "/" + ECFDIRECTORY;
        else return FILE_DIRECTORY;
    }

    protected IProject getFirstProjectFromWorkspace() throws Exception {
        IWorkspace ws = ResourcesPlugin.getWorkspace();
        IWorkspaceRoot wr = ws.getRoot();
        IProject[] projects = wr.getProjects();
        if (projects == null)
            return null;
        return projects[0];
    }

    protected void makeAndAddSharedObject(ISharedObjectContainer client,
            IProject proj, User user, String fileDir) throws Exception {
        IWorkbenchWindow ww = PlatformUI.getWorkbench()
                .getActiveWorkbenchWindow();
        sharedObject = new EclipseCollabSharedObject(proj, ww,
                user, fileDir);
        sharedObject.setListener(new SharedObjectEventListener() {
            public void memberRemoved(ID member) {
                if (member.equals(groupID)) {
                    disposeClient();
                }
            }
            public void memberAdded(ID member) {}
            public void otherActivated(ID other) {}
            public void otherDeactivated(ID other) {}
            public void windowClosing() {
                disposeClient();
            }
        });
        ID newID = IDFactory.makeStringID(COLLAB_SHARED_OBJECT_ID);
        client.getSharedObjectManager().addSharedObject(newID, sharedObject,
                new HashMap(), null);
    }

    protected void addObjectToClient(ISharedObjectContainer client,
            String username, IProject proj) throws Exception {
        IProject project = (proj == null) ? getFirstProjectFromWorkspace()
                : proj;
        String fileDir = getSharedFileDirectoryForProject(project);
        String projName = (project == null) ? "<workspace>" : project.getName();
        User user = getUserData(client.getClass().getName(),client.getConfig().getID(),
                (username == null) ? USERNAME : username, projName);
        makeAndAddSharedObject(client, project, user, fileDir);
    }

    public synchronized boolean isConnected() {
        return (client != null);
    }

    public synchronized void createAndConnectClient(String type, ID gID, String username,
            Object data, IProject proj) throws Exception {
        String containerType = (type==null)?GENERIC_CONTAINER_CLIENT_NAME:type;
        client = SharedObjectContainerFactory
                .makeSharedObjectContainer(containerType);
        if (gID == null) {
            groupID = defaultGroupID;
        } else {
            groupID = gID;
        }
        addObjectToClient(client, username, proj);
        if (groupID == null)
            client.joinGroup(defaultGroupID, data);
        else
            client.joinGroup(groupID, data);
    }

    public synchronized void disposeClient() {
        if (isConnected()) {
            try {
                if (sharedObject != null) sharedObject.destroySelf();
            } catch (Exception e) {}
            sharedObject = null;
        }
    }
    
    public synchronized ISharedObjectContainer getContainer() {
        return client;
    }
}