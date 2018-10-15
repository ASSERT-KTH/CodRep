client.dispose();

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

import java.io.IOException;
import java.net.ConnectException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import javax.security.auth.callback.Callback;
import javax.security.auth.callback.CallbackHandler;
import javax.security.auth.callback.NameCallback;
import javax.security.auth.callback.UnsupportedCallbackException;

import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspaceRoot;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerJoinException;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.ISharedObjectContainerListener;
import org.eclipse.ecf.core.SharedObjectContainerFactory;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.events.ISharedObjectContainerDepartedEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.security.IJoinContext;
import org.eclipse.ecf.core.security.ObjectCallback;
import org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject;
import org.eclipse.ecf.example.collab.share.SharedObjectEventListener;
import org.eclipse.ecf.example.collab.share.TreeItem;
import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.ecf.presence.IAccountManager;
import org.eclipse.ecf.presence.IMessageListener;
import org.eclipse.ecf.presence.IMessageSender;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceContainer;
import org.eclipse.ecf.presence.IPresenceListener;
import org.eclipse.ecf.presence.IPresenceSender;
import org.eclipse.ecf.presence.IRosterEntry;
import org.eclipse.ecf.presence.ISubscribeListener;
import org.eclipse.ecf.presence.impl.Presence;
import org.eclipse.ecf.ui.dialogs.AddBuddyDialog;
import org.eclipse.ecf.ui.dialogs.ReceiveAuthorizeRequestDialog;
import org.eclipse.ecf.ui.views.ILocalInputHandler;
import org.eclipse.ecf.ui.views.RosterView;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;

public class Client {
    public static final String JOIN_TIME_FORMAT = "hh:mm:ss a z";
    public static final String JMS_CONTAINER_CLIENT_NAME = "org.eclipse.ecf.provider.jms.TCPClient";
    public static final String GENERIC_CONTAINER_CLIENT_NAME = "org.eclipse.ecf.provider.generic.Client";
    public static final String GENERIC_CONTAINER_SERVER_NAME = "org.eclipse.ecf.provider.generic.Server";
    public static final String DEFAULT_SERVER_ID = "ecftcp://localhost:3282/server";
    public static final String COLLAB_SHARED_OBJECT_ID = "chat";
    public static final String FILE_DIRECTORY = "received_files";
    public static final String USERNAME = System.getProperty("user.name");
    public static final String ECFDIRECTORY = "ECF_" + FILE_DIRECTORY + "/";
    public static final String WORKSPACE_NAME = "<workspace>";
    
    static ID defaultGroupID = null;
    static Hashtable clients = new Hashtable();

    public static String getNameForResource(IResource res) {
        String preName = res.getName().trim();
        if (preName == null || preName.equals("")) {
            preName = WORKSPACE_NAME;
        }
        return preName;
    }
    public static class ClientEntry {
        String type;
        ISharedObjectContainer client;
        EclipseCollabSharedObject obj;
        
        public ClientEntry(String type, ISharedObjectContainer cont) {
            this.type = type;
            this.client = cont;
        }
        public String getType() {
            return type;
        }
        public ISharedObjectContainer getContainer() {
            return client;
        }
        public void setObject(EclipseCollabSharedObject obj) {
            this.obj = obj;
        }
        public EclipseCollabSharedObject getObject() {
            return obj;
        }
        public void dispose() {
            if (obj != null) obj.destroySelf();
            client.dispose(0);
        }
    }
    
    protected static void addClientEntry(IResource proj, ClientEntry entry) {
        synchronized (clients) {
            String name = getNameForResource(proj);
            Vector v = (Vector) clients.get(name);
            if (v == null) {
                v = new Vector();
            }
            v.add(entry);
            clients.put(name,v);
        }
    }
    protected static Vector getClientEntries(IResource proj) {
        synchronized (clients) {
            return (Vector) clients.get(getNameForResource(proj));
        }
    }
    protected  static ClientEntry getClientEntry(IResource proj, String type) {
        synchronized (clients) {
            Vector v = (Vector) getClientEntries(proj);
            if (v == null) return null;
            for(Iterator i=v.iterator(); i.hasNext(); ) {
                ClientEntry e = (ClientEntry) i.next();
                if (isType(e,type)) {
                    return e;
                }
            }
        }
        return null;
    }
    protected static boolean containsEntry(IResource proj, String type) {
        synchronized (clients) {
            Vector v = (Vector) clients.get(getNameForResource(proj));
            if (v == null) return false;
            for(Iterator i=v.iterator(); i.hasNext(); ) {
                ClientEntry e = (ClientEntry) i.next();
                if (isType(e,type)) {
                    return true;
                }
            }
        }
        return false;
    }
    protected static void removeClientEntry(IResource proj, String type) {
        synchronized (clients) {
            Vector v = (Vector) clients.get(getNameForResource(proj));
            if (v == null) return;
            ClientEntry remove = null;
            for(Iterator i=v.iterator(); i.hasNext(); ) {
                ClientEntry e = (ClientEntry) i.next();
                if (isType(e,type)) {
                    remove = e;
                }
            }
            if (remove != null) v.remove(remove);
            if (v.size()==0) {
                clients.remove(getNameForResource(proj));
            }
        }
    }
    public Client() throws Exception {
        defaultGroupID = IDFactory.getDefault().makeStringID(DEFAULT_SERVER_ID);
    }

    protected User getUserData(String containerType, ID clientID, String usernick, IResource project) {
        Vector topElements = new Vector();
        topElements.add(new TreeItem("Project", getNameForResource(project)));
        SimpleDateFormat sdf = new SimpleDateFormat(JOIN_TIME_FORMAT);
        topElements.add(new TreeItem("Time",sdf.format(new Date())));
        try {
            String userLang = System.getProperty("user.language");
            topElements.add(new TreeItem("Language",userLang));
        } catch (Exception e) {}
        try {
            String timeZone = System.getProperty("user.timezone");
            topElements.add(new TreeItem("Time Zone",timeZone));
        } catch (Exception e) {}
        try {
            String osgiVersion = System.getProperty("org.osgi.framework.version");
            topElements.add(new TreeItem("OSGI version",osgiVersion));
        } catch (Exception e) {}
        try {
            String javaVersion = System.getProperty("java.version");
            topElements.add(new TreeItem("Java",javaVersion));
        } catch (Exception e) {}
        try {
            String osName = Platform.getOS();
            topElements.add(new TreeItem("OS",osName));
        } catch (Exception e) {}
        return new User(clientID, usernick, topElements);
    }

    protected String getSharedFileDirectoryForProject(IResource proj) {
        String eclipseDir = Platform.getLocation().lastSegment();
        if (proj == null)
            return eclipseDir + "/" + ECFDIRECTORY;
        else return FILE_DIRECTORY;
    }

    protected IResource getWorkspace() throws Exception {
        IWorkspaceRoot ws = ResourcesPlugin.getWorkspace().getRoot();
        return ws;
    }

    protected void makeAndAddSharedObject(final ClientEntry client,
            final IResource proj, User user, String fileDir) throws Exception {
        IWorkbenchWindow ww = PlatformUI.getWorkbench()
                .getActiveWorkbenchWindow();
        EclipseCollabSharedObject sharedObject = new EclipseCollabSharedObject(proj, ww,
                user, fileDir);
        sharedObject.setListener(new SharedObjectEventListener() {
            public void memberRemoved(ID member) {
                ID groupID = client.getContainer().getGroupID();
                if (member.equals(groupID)) {
                    disposeClient(proj, client);
                }
            }
            public void memberAdded(ID member) {}
            public void otherActivated(ID other) {}
            public void otherDeactivated(ID other) {}
            public void windowClosing() {
                removeClientEntry(proj,client.getType());
            }
        });
        ID newID = IDFactory.getDefault().makeStringID(COLLAB_SHARED_OBJECT_ID);
        client.getContainer().getSharedObjectManager().addSharedObject(newID, sharedObject,
                new HashMap());
        client.setObject(sharedObject);
    }

    protected void addObjectToClient(ClientEntry client,
            String username, IResource proj) throws Exception {
        IResource project = (proj == null) ? getWorkspace()
                : proj;
        User user = getUserData(client.getClass().getName(),client.getContainer().getConfig().getID(),
                (username == null) ? USERNAME : username, proj);
        makeAndAddSharedObject(client, project, user, getSharedFileDirectoryForProject(project));
    }
    public synchronized ClientEntry isConnected(IResource project, String type) {
        if (type == null) type = GENERIC_CONTAINER_CLIENT_NAME;
        ClientEntry entry = getClientEntry(project,type);
        return entry;
    }

    public static boolean isType(ClientEntry entry, String type) {
        if (entry == null || type == null) return false;
        String name = entry.getType();
        if (name.equals(type)) return true;
        else return false;
    }
	protected IJoinContext getJoinContext(final String username, final Object password) {
		return new IJoinContext() {
			public CallbackHandler getCallbackHandler() {
				return new CallbackHandler() {
					public void handle(Callback[] callbacks) throws IOException, UnsupportedCallbackException {
						if (callbacks == null) return;
						for (int i=0; i < callbacks.length; i++) {
							if (callbacks[i] instanceof NameCallback) {
								NameCallback ncb = (NameCallback) callbacks[i];
								ncb.setName(username);
							} else if (callbacks[i] instanceof ObjectCallback) {
								ObjectCallback ocb = (ObjectCallback) callbacks[i];
								ocb.setObject(password);
							}
						}
					}					
				};
			}			
		};
	}
    public synchronized void createAndConnectClient(String type, final ID gID, String username,
            Object data, final IResource proj) throws Exception {
        
        if (proj == null) throw new NullPointerException("Resource cannot be null");
        ClientEntry entry = getClientEntry(proj,type);
        if (entry != null) {
            // Already got a session going...that's OK as long as it's not of the same type...
                throw new ConnectException("Already connected");
        }
        
        String containerType = (type==null)?GENERIC_CONTAINER_CLIENT_NAME:type;
        final ISharedObjectContainer client = SharedObjectContainerFactory
        .getDefault().makeSharedObjectContainer(containerType);
        final ClientEntry newClient = new ClientEntry(containerType,client);
        final ID groupID = (gID==null)?defaultGroupID:gID;
        
        if (containerType.equals(GENERIC_CONTAINER_CLIENT_NAME) || containerType.equals(JMS_CONTAINER_CLIENT_NAME)) {
            addObjectToClient(newClient, username, proj);
        } else {
            client.addListener(new ISharedObjectContainerListener() {
                public void handleEvent(IContainerEvent evt) {
                    if (evt instanceof ISharedObjectContainerDepartedEvent) {
                        ISharedObjectContainerDepartedEvent cd = (ISharedObjectContainerDepartedEvent) evt;
                        final ID departedContainerID = cd.getDepartedContainerID();
                        if (groupID.equals(departedContainerID)) {
                            // This container is done
                            disposeClient(proj,newClient);                        
                        }
                    }
                }
                
            },"");           
        }
        
        // Check for IPresenceContainer....if it is, setup
        IPresenceContainer pc = (IPresenceContainer) client.getAdapter(IPresenceContainer.class);
        if (pc != null) setupPresenceContainer(client,pc,groupID,username);

        try {
            client.joinGroup(groupID, getJoinContext(username,data));
        } catch (ContainerJoinException e) {
            try {
                EclipseCollabSharedObject so = newClient.getObject();
                if (so != null) {
                    so.destroySelf();
                }
            } catch (Exception e1) {}
            throw e;
        }
        // only add client if the join successful
        addClientEntry(proj,newClient);
    }

    protected RosterView rosterView = null;
    protected IMessageSender messageSender = null;
    protected IPresenceSender presenceSender = null;
	protected IAccountManager accountManager = null;
	
    protected void setupPresenceContainer(final ISharedObjectContainer container, IPresenceContainer pc, final ID localUser, final String nick) {
        
        messageSender = pc.getMessageSender();
        presenceSender = pc.getPresenceSender();
		accountManager = pc.getAccountManager();
		
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                try {
                    IWorkbenchWindow ww = PlatformUI.getWorkbench()
                            .getActiveWorkbenchWindow();
                    IWorkbenchPage wp = ww.getActivePage();
                    IViewPart view = wp.showView("org.eclipse.ecf.ui.view.rosterview");
                    rosterView = (RosterView) view;
                    String nickname = null;
                    if (nick != null) {
                        nickname = nick;
                    } else {
                        String name = localUser.getName();
                        nickname = name.substring(0,name.indexOf("@"));
                    }
                    rosterView.setLocalUser(new org.eclipse.ecf.core.user.User(localUser,nickname),new ILocalInputHandler() {

                        public void inputText(ID userID, String text) {
                            messageSender.sendMessage(localUser,userID,null,null,text);
                        }

                        public void startTyping(ID userID) {
                            //System.out.println("handleStartTyping("+userID+")");
                        }

                        public void disconnect() {
                            container.leaveGroup();
                        }

						public void updatePresence(ID userID, IPresence presence) {
							presenceSender.sendPresenceUpdate(localUser,userID,presence);
						}

						public void sendRosterAdd(String user, String name, String[] groups) {
							// Send roster add
							presenceSender.sendRosterAdd(localUser, user,name,groups);
						}
						
						public void sendRosterRemove(ID userID) {
							presenceSender.sendRosterRemove(localUser, userID);
						}
                        
                    });
                } catch (Exception e) {
                    IStatus status = new Status(IStatus.ERROR,ClientPlugin.PLUGIN_ID,IStatus.OK,"Exception showing presence view",e);
                    ClientPlugin.getDefault().getLog().log(status);
                }
            }
        });

        pc.addMessageListener(new IMessageListener() {
            public void handleMessage(final ID fromID, final ID toID, final Type type, final String subject, final String message) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
                        rosterView.handleMessage(fromID,toID,type,subject,message);
                    }
                });
            }                
        });
        pc.addPresenceListener(new IPresenceListener() {

            public void handleContainerJoined(final ID joinedContainer) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
                        rosterView.setGroup(joinedContainer);
                    }
                });
				// XXX TESTING OF ACCOUNT CREATION
				/*
				try {
					accountManager.createAccount("foo1","foo1",null);
				} catch (ECFException e) {
					e.printStackTrace();
				}
				*/
				
            }

            public void handleRosterEntry(final IRosterEntry entry) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
                        rosterView.handleRosterEntry(entry);
                    }
                });
            }

            public void handlePresence(final ID fromID, final IPresence presence) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
                        rosterView.handlePresence(fromID,presence);
                    }
                });
            }

            public void handleContainerDeparted(final ID departedContainer) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
						if (rosterView != null) {
							rosterView.memberDeparted(departedContainer);
						}
                    }
                });
                messageSender = null;
                rosterView = null;
            }

			public void handleSetRosterEntry(final IRosterEntry entry) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
                        rosterView.handleSetRosterEntry(entry);
                    }
                });
			}
            
        });
		pc.addSubscribeListener(new ISubscribeListener() {

			public void handleSubscribeRequest(final ID fromID, IPresence presence) {
		        Display.getDefault().syncExec(new Runnable() {
		            public void run() {
		                try {
		                    IWorkbenchWindow ww = PlatformUI.getWorkbench()
		                            .getActiveWorkbenchWindow();
							ReceiveAuthorizeRequestDialog authRequest = new ReceiveAuthorizeRequestDialog(ww.getShell(),fromID.getName(),localUser.getName());
							authRequest.setBlockOnOpen(true);
							authRequest.open();
							int res = authRequest.getButtonPressed();
							if (res == ReceiveAuthorizeRequestDialog.AUTHORIZE_AND_ADD) {								
								if (presenceSender != null) {
									presenceSender.sendPresenceUpdate(localUser,fromID,new Presence(IPresence.Type.SUBSCRIBED));
									// Get group info here
									if (rosterView != null) {
										String [] groupNames = rosterView.getGroupNames();
										List g = Arrays.asList(groupNames);
										String selectedGroup = rosterView.getSelectedGroupName();
										int selected = (selectedGroup==null)?-1:g.indexOf(selectedGroup);
										AddBuddyDialog sg = new AddBuddyDialog(ww.getShell(),fromID.getName(),groupNames,selected);
										sg.open();
										if (sg.getResult() == Window.OK) {
											String group = sg.getGroup();
											String user = sg.getUser();
											String nickname = sg.getNickname();
											sg.close();
											if (!g.contains(group)) {
												// create group with name
												rosterView.addGroup(group);
											}
											// Finally, send the information and request subscription
											presenceSender.sendRosterAdd(localUser, user,nickname,new String[] { group } );
										}
									}
								} 
							} else if (res == ReceiveAuthorizeRequestDialog.AUTHORIZE_ID) {
								if (presenceSender != null) {
									presenceSender.sendPresenceUpdate(localUser,fromID,new Presence(IPresence.Type.SUBSCRIBED));
								} 
							} else if (res == ReceiveAuthorizeRequestDialog.REFUSE_ID) {
								System.out.println("Refuse hit");
							} else {
								System.out.println("No buttons hit");
							}
						} catch (Exception e) {
		                    IStatus status = new Status(IStatus.ERROR,ClientPlugin.PLUGIN_ID,IStatus.OK,"Exception showing authorization dialog",e);
		                    ClientPlugin.getDefault().getLog().log(status);
						}
		            }
		        });
			}

			public void handleUnsubscribeRequest(ID fromID, IPresence presence) {
				if (presenceSender != null) {
					presenceSender.sendPresenceUpdate(localUser,fromID,new Presence(IPresence.Type.UNSUBSCRIBED));
				}
			}

			public void handleSubscribed(ID fromID, IPresence presence) {
				//System.out.println("subscribed from "+fromID);			
			}

			public void handleUnsubscribed(ID fromID, IPresence presence) {
				//System.out.println("unsubscribed from "+fromID);			
			}
		});
	}
    public synchronized void disposeClient(IResource proj, ClientEntry entry) {
        entry.dispose();
        removeClientEntry(proj,entry.getType());
    }

    public synchronized static ISharedObjectContainer getContainer(IResource proj) {
        ClientEntry entry = getClientEntry(proj,GENERIC_CONTAINER_CLIENT_NAME);
        if (entry == null) {
            entry = getClientEntry(ResourcesPlugin.getWorkspace().getRoot(),GENERIC_CONTAINER_CLIENT_NAME);
        }
        if (entry != null) return entry.getContainer();
        else return null;
    }
}