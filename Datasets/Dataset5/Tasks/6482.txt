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

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Vector;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.IContainerEjectedEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.example.collab.share.SharedObjectEventListener;
import org.eclipse.ecf.example.collab.share.TreeItem;
import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;

public class SharedObjectContainerUI {
	public static final String JOIN_TIME_FORMAT = "hh:mm:ss a z";
	public static final String FILE_DIRECTORY = "received_files";
	public static final String ECFDIRECTORY = "ECF_" + FILE_DIRECTORY + "/";
	public static final String COLLAB_SHARED_OBJECT_ID = "chat";
	ISharedObjectContainer soc = null;
	CollabClient collabclient = null;
	
	public SharedObjectContainerUI(CollabClient client, ISharedObjectContainer soc) {
		this.collabclient = client;
		this.soc = soc;
	}

	protected String getSharedFileDirectoryForProject(IResource proj) {
		String eclipseDir = Platform.getLocation().lastSegment();
		if (proj == null)
			return eclipseDir + "/" + ECFDIRECTORY;
		else
			return FILE_DIRECTORY;
	}

	protected User getUserData(String containerType, ID clientID,
			String usernick, IResource project) {
		Vector topElements = new Vector();
		topElements.add(new TreeItem("Project", CollabClient
				.getNameForResource(project)));
		SimpleDateFormat sdf = new SimpleDateFormat(JOIN_TIME_FORMAT);
		topElements.add(new TreeItem("Time", sdf.format(new Date())));
		try {
			String userLang = System.getProperty("user.language");
			topElements.add(new TreeItem("Language", userLang));
		} catch (Exception e) {
		}
		try {
			String timeZone = System.getProperty("user.timezone");
			topElements.add(new TreeItem("Time Zone", timeZone));
		} catch (Exception e) {
		}
		try {
			String osgiVersion = System
					.getProperty("org.osgi.framework.version");
			topElements.add(new TreeItem("OSGI version", osgiVersion));
		} catch (Exception e) {
		}
		try {
			String javaVersion = System.getProperty("java.version");
			topElements.add(new TreeItem("Java", javaVersion));
		} catch (Exception e) {
		}
		try {
			String osName = Platform.getOS();
			topElements.add(new TreeItem("OS", osName));
		} catch (Exception e) {
		}
		return new User(clientID, usernick, topElements);
	}

	void addObjectToClient(ISharedObjectContainer soContainer, ClientEntry client, String username, IResource proj)
			throws Exception {
		IResource project = (proj == null) ? CollabClient.getWorkspace() : proj;
		User user = getUserData(client.getClass().getName(), client
				.getContainer().getID(), username, proj);
		createAndAddSharedObject(soContainer, client, project, user,
				getSharedFileDirectoryForProject(project));
	}

	public void setup(final ISharedObjectContainer soContainer, final ClientEntry newClientEntry,
			final IResource resource, String username) throws Exception {
		addObjectToClient(soContainer, newClientEntry, username, resource);
		soc.addListener(new IContainerListener() {
			public void handleEvent(IContainerEvent evt) {
				if (evt instanceof IContainerDisconnectedEvent) {
					IContainerDisconnectedEvent cd = (IContainerDisconnectedEvent) evt;
					final ID departedContainerID = cd.getTargetID();
					ID connectedID = newClientEntry.getConnectedID();
					if (connectedID == null
							|| connectedID.equals(departedContainerID)) {
						// This container is done
						if (!newClientEntry.isDisposed()) {
							collabclient.disposeClient(resource, newClientEntry);
						}
					}
				} else if (evt instanceof IContainerEjectedEvent) {
					IContainerEjectedEvent ce = (IContainerEjectedEvent) evt;
					final ID departedContainerID = ce.getTargetID();
					ID connectedID = newClientEntry.getConnectedID();
					if (connectedID == null || connectedID.equals(departedContainerID)) {
						if (!newClientEntry.isDisposed()) {
							collabclient.disposeClient(resource, newClientEntry);
						}
					}
				}
			}
		}, "");
	}

	protected void createAndAddSharedObject(final ISharedObjectContainer soContainer, final ClientEntry client,
			final IResource proj, User user, String fileDir) throws Exception {
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
				.getActiveWorkbenchWindow();
		EclipseCollabSharedObject sharedObject = new EclipseCollabSharedObject(
				proj, ww, user, fileDir);
		sharedObject.setListener(new SharedObjectEventListener() {
			public void memberRemoved(ID member) {
				ID groupID = client.getConnectedID();
				if (member.equals(groupID)) {
					if (!client.isDisposed()) {
						collabclient.disposeClient(proj, client);
					}
				}
			}

			public void memberAdded(ID member) {
			}

			public void otherActivated(ID other) {
			}

			public void otherDeactivated(ID other) {
			}

			public void windowClosing() {
				ID groupID = client.getConnectedID();
				CollabClient.removeClientForResource(proj, groupID);
			}
		});
		ID newID = IDFactory.getDefault().createStringID(COLLAB_SHARED_OBJECT_ID);
		soContainer.getSharedObjectManager().addSharedObject(newID,
				sharedObject, new HashMap());
			client.setObject(sharedObject);
	}
}