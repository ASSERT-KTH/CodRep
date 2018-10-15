public static final String GENERIC_CONTAINER_CLIENT_NAME = "ecf.generic.client";

package org.eclipse.ecf.example.collab;

import java.net.URISyntaxException;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Vector;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.presence.IPresenceContainer;
import org.eclipse.ecf.presence.chat.IChatRoomManager;

public class CollabClient {
	public static final String WORKSPACE_NAME = "<workspace>";
    public static final String GENERIC_CONTAINER_CLIENT_NAME = "org.eclipse.ecf.provider.generic.Client";
	static Hashtable clients = new Hashtable();
	static CollabClient collabClient = new CollabClient();

	PresenceContainerUI presenceContainerUI = null;
	ChatRoomManagerUI chatRoomManagerUI = null;
	
	/**
	 * Create a new container instance, and connect to a remote server or group.
	 * 
	 * @param containerType the container type used to create the new container instance.  Must not be null.
	 * @param uri the uri that is used to create a targetID for connection.  Must not be null.
	 * @param nickname an optional String nickname.  May be null.
	 * @param connectData optional connection data.  May be null.
	 * @param resource the resource that this container instance is associated with.  Must not be null.
	 * @throws Exception
	 */
	public void createAndConnectClient(final String containerType, String uri,
			String nickname, final Object connectData, final IResource resource)
			throws Exception {
		// First create the new container instance
		final IContainer newClient = ContainerFactory
				.getDefault().makeContainer(containerType);
		
		// Get the target namespace, so we can create a target ID of appropriate type
		Namespace targetNamespace = newClient.getConnectNamespace();
		// Create the targetID instance
		ID targetID = IDFactory.getDefault().makeID(targetNamespace, uri);
		
		// Setup username
		String username = setupUsername(targetID,nickname);
		// Create a new client entry to hold onto container once created
		final ClientEntry newClientEntry = new ClientEntry(containerType,
				newClient);
		
		// Setup user interfaces for various container adapter types
		// IFileShareContainer fsc = (IFileShareContainer) newClient.getAdapter(IFileShareContainer.class);
		
		// if (fsc == null) {
			IChatRoomManager man = (IChatRoomManager) newClient.getAdapter(IChatRoomManager.class);
			if (man != null) {
				chatRoomManagerUI = new ChatRoomManagerUI(man);
				chatRoomManagerUI = chatRoomManagerUI.setup(newClient, targetID, username);
			} else {
			     // Check for IPresenceContainer....if it is, setup presence UI, if not setup shared object container
				IPresenceContainer pc = (IPresenceContainer) newClient
						.getAdapter(IPresenceContainer.class);
				if (pc != null) {
					// Setup presence UI
					presenceContainerUI = new PresenceContainerUI(pc);
					presenceContainerUI.setup(newClient, targetID, username);
				} else {
					// Setup sharedobject container if the new instance supports this
					ISharedObjectContainer sharedObjectContainer = (ISharedObjectContainer) newClient
							.getAdapter(ISharedObjectContainer.class);
					if (sharedObjectContainer != null) {
						new SharedObjectContainerUI(this,sharedObjectContainer).setup(sharedObjectContainer,
								newClientEntry, resource, username);
					}
				}
			}
		//}
		
		// Now connect
		try {
			newClient.connect(targetID, ConnectContextFactory.makeUsernamePasswordConnectContext(username, connectData));
		} catch (ContainerConnectException e) {
			// If we have a connect exception then we remove any previously added shared object
			EclipseCollabSharedObject so = newClientEntry.getObject();
			if (so != null) so.destroySelf();
			throw e;
		}
		
		/*
		if (fsc != null) {
			// XXX Testing
			IStoreFileDescription sfs = new IStoreFileDescription() {
				public InputStream getLocalStream() throws IOException {
					return new FileInputStream("notice.html");
				}
				public String getRemoteFileName() {
					return "rnotice.html";
				}
				public ISharedFileEventListener getEventListener() {
					return null;
				}
				public Map getProperties() {
					return null;
				}
			};
			ISharedFile sf = fsc.store(sfs);
			try {
				sf.start();
			} catch (SharedFileStartException e) {
				e.printStackTrace();
			}
		}
		*/
		// only add client if the connect was successful
		addClientForResource(newClientEntry, resource);
	}

	public ClientEntry isConnected(IResource project, String type) {
		ClientEntry entry = getClientEntry(project, type);
		return entry;
	}

	protected static void addClientForResource(ClientEntry entry, IResource proj) {
		synchronized (clients) {
			String name = getNameForResource(proj);
			Vector v = (Vector) clients.get(name);
			if (v == null) {
				v = new Vector();
			}
			v.add(entry);
			clients.put(name, v);
		}
	}

	protected static void removeClientForResource(IResource proj, ID targetID) {
		synchronized (clients) {
			String resourceName = getNameForResource(proj);
			Vector v = (Vector) clients.get(resourceName);
			if (v == null)
				return;
			ClientEntry remove = null;
			for (Iterator i = v.iterator(); i.hasNext();) {
				ClientEntry e = (ClientEntry) i.next();
				ID connectedID = e.getConnectedID();
				if (connectedID == null || connectedID.equals(targetID)) {
					remove = e;
				}
			}
			if (remove != null)
				v.remove(remove);
			if (v.size() == 0) {
				clients.remove(resourceName);
			}
		}
	}

	public static String getNameForResource(IResource res) {
		String preName = res.getName().trim();
		if (preName == null || preName.equals("")) {
			preName = WORKSPACE_NAME;
		}
		return preName;
	}

	protected static IResource getWorkspace() throws Exception {
		IWorkspaceRoot ws = ResourcesPlugin.getWorkspace().getRoot();
		return ws;
	}

	protected static Vector getClientEntries(IResource proj) {
		synchronized (clients) {
			return (Vector) clients.get(getNameForResource(proj));
		}
	}

	protected static ClientEntry getClientEntry(IResource proj, ID targetID) {
		synchronized (clients) {
			Vector v = (Vector) getClientEntries(proj);
			if (v == null)
				return null;
			for (Iterator i = v.iterator(); i.hasNext();) {
				ClientEntry e = (ClientEntry) i.next();
				ID connectedID = e.getConnectedID();
				if (connectedID == null)
					continue;
				else if (connectedID.equals(targetID)) {
					return e;
				}
			}
		}
		return null;
	}

	protected static ClientEntry getClientEntry(IResource proj,
			String containerType) {
		synchronized (clients) {
			Vector v = (Vector) getClientEntries(proj);
			if (v == null)
				return null;
			for (Iterator i = v.iterator(); i.hasNext();) {
				ClientEntry e = (ClientEntry) i.next();
				ID connectedID = e.getConnectedID();
				if (connectedID == null)
					continue;
				else {
					String contType = e.getContainerType();
					if (contType.equals(containerType)) {
						return e;
					}
				}
			}
		}
		return null;
	}

	protected static boolean containsEntry(IResource proj, ID targetID) {
		synchronized (clients) {
			Vector v = (Vector) clients.get(getNameForResource(proj));
			if (v == null)
				return false;
			for (Iterator i = v.iterator(); i.hasNext();) {
				ClientEntry e = (ClientEntry) i.next();
				ID connectedID = e.getConnectedID();
				if (connectedID == null)
					continue;
				else if (connectedID.equals(targetID)) {
					return true;
				}
			}
		}
		return false;
	}
    public synchronized static ISharedObjectContainer getContainer(IResource proj) {
        ClientEntry entry = getClientEntry(proj,GENERIC_CONTAINER_CLIENT_NAME);
        if (entry == null) {
            entry = getClientEntry(ResourcesPlugin.getWorkspace().getRoot(),GENERIC_CONTAINER_CLIENT_NAME);
        }
        if (entry != null) {
        	IContainer cont = entry.getContainer();
        	if (cont != null) return (ISharedObjectContainer) cont.getAdapter(ISharedObjectContainer.class);
        	else return null;
        }
        else return null;
    }
	public static CollabClient getDefault() {
		return collabClient;
	}
	protected synchronized void disposeClient(IResource proj, ClientEntry entry) {
		entry.dispose();
		removeClientForResource(proj, entry.getConnectedID());
	}

	protected String setupUsername(ID targetID, String nickname) throws URISyntaxException {
		String username = null;
		if (nickname != null) {
			username = nickname;
		} else {
			username = targetID.toURI().getUserInfo();
			if (username == null || username.equals(""))
				username = System.getProperty("user.name");
		}
		return username;
	}


}