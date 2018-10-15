.getDefault().makeSharedObjectContainer(DISCOVERY_CONTAINER);

package org.eclipse.ecf.example.collab;

import java.io.IOException;
import java.net.InetAddress;
import java.net.URI;
import java.util.Map;
import java.util.Properties;

import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.SharedObjectContainerFactory;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.ServiceID;
import org.eclipse.ecf.discovery.IDiscoveryContainer;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.example.collab.actions.ClientConnectAction;
import org.eclipse.ecf.ui.views.DiscoveryView;
import org.eclipse.ecf.ui.views.IDiscoveryController;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;

public class DiscoveryStartup {

	public static final String DISCOVERY_CONTAINER = "org.eclipse.ecf.provider.jmdns.container.JmDNS";
	public static final String TCPSERVER_DISCOVERY_TYPE = "_ecftcp._tcp.local.";
	public static final String PROP_PROTOCOL_NAME = "protocol";
	public static final String PROP_CONTAINER_TYPE_NAME = "containertype";
	public static final String PROP_CONTAINER_TYPE_VALUE = Client.GENERIC_CONTAINER_CLIENT_NAME;
	public static final String PROP_PW_REQ_NAME = "pwrequired";
	public static final String PROP_PW_REQ_VALUE = "false";
	public static final String PROP_DEF_USER_NAME = "defaultuser";
	public static final String PROP_DEF_USER_VALUE = "guest";
	public static final String PROP_PATH_NAME = "path";
	public static final int SVC_DEF_WEIGHT = 0;
	public static final int SVC_DEF_PRIORITY = 0;
	
	static IDiscoveryContainer discovery = null;
	static ISharedObjectContainer socontainer = null;
	
    protected DiscoveryView discoveryView = null;
    
    static String serviceTypes[] = new String[] {
            TCPSERVER_DISCOVERY_TYPE
        };
	public DiscoveryStartup() {
		setupDiscovery();
	}
	
	public void dispose() {
		if (socontainer != null) {
			socontainer.dispose(1000);
			socontainer = null;
		}
		discovery = null;
	}
	
	protected void setupDiscovery() {
		if (discovery == null && ClientPlugin.getDefault().getPreferenceStore().getBoolean(ClientPlugin.PREF_REGISTER_SERVER)) {
			try {
				socontainer = SharedObjectContainerFactory
						.makeSharedObjectContainer(DISCOVERY_CONTAINER);
				discovery = (IDiscoveryContainer) socontainer
						.getAdapter(IDiscoveryContainer.class);
				if (discovery != null) {
					setupDiscoveryContainer(discovery);
					socontainer.joinGroup(null,null);
					//registerServiceTypes();
				}
				else {
					if (socontainer != null) {
						socontainer.dispose(1000);
						socontainer = null;
					}
					discovery = null;
					ClientPlugin.log("No discovery container available");
				}
			} catch (Exception e) {
				if (socontainer != null) {
					socontainer.dispose(1000);
					socontainer = null;
				}
				discovery = null;
				ClientPlugin.log("Exception creating discovery container",e);
			}
		}
	}

	protected void connectToServiceFromInfo(IServiceInfo svcInfo) {
		ClientConnectAction action = new ClientConnectAction();
		Map props = svcInfo.getProperties();
		String type = (String) props.get(PROP_CONTAINER_TYPE_NAME);
		if (type == null || type.equals("")) {
			action.setContainerType(Client.GENERIC_CONTAINER_CLIENT_NAME);
		} else {
			action.setContainerType(type);
		}
		String username = System.getProperty("user.name");
		action.setUsername(username);
		ID targetID = null;
		String targetString = null;
        try {
    		targetString = svcInfo.getServiceURI().toString();
            targetID = IDFactory.makeStringID(targetString);
        } catch (Exception e) {
        	ClientPlugin.log("cannot create target id for "+targetString,e);
        }
		action.setTargetID(targetID);
		action.setProject(ResourcesPlugin.getWorkspace().getRoot());
		// do it
		action.run(null);
	}
	
    protected void setupDiscoveryContainer(final IDiscoveryContainer dc) {
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                try {
                    IWorkbenchWindow ww = PlatformUI.getWorkbench()
                            .getActiveWorkbenchWindow();
                    IWorkbenchPage wp = ww.getActivePage();
                    IViewPart view = wp.showView("org.eclipse.ecf.ui.view.discoveryview");
                    discoveryView = (DiscoveryView) view;
                    discoveryView.setShowTypeDetails(false);
                    discoveryView.setDiscoveryController(new IDiscoveryController() {
						public void connectToService(IServiceInfo service) {
							connectToServiceFromInfo(service);
						}

						public void setupDiscoveryContainer(DiscoveryView dview) {
							System.out.println("setupDiscoveryContainer");	
							ClientPlugin.getDefault().initDiscovery();
						}

						public void disposeDiscoveryContainer(DiscoveryView dview) {
							System.out.println("disposeDiscoveryContainer");						
							ClientPlugin.getDefault().disposeDiscovery();
						}

						public IDiscoveryContainer getDiscoveryContainer() {
							return discovery;
						}

						public ISharedObjectContainer getSharedObjectContainer() {
							return socontainer;
						}

						public String[] getServiceTypes() {
							return serviceTypes;
						}
                    });
                } catch (Exception e) {
                    IStatus status = new Status(IStatus.ERROR,ClientPlugin.PLUGIN_ID,IStatus.OK,"Exception showing presence view",e);
                    ClientPlugin.getDefault().getLog().log(status);
                }
            }
        });
        if (discoveryView != null) {
	        dc.addServiceTypeListener(new IServiceTypeListener() {
				public void serviceTypeAdded(IServiceEvent event) {
					ServiceID svcID = event.getServiceInfo().getServiceID();
					discoveryView.addServiceTypeInfo(svcID.getServiceType());
					dc.addServiceListener(event.getServiceInfo().getServiceID(), new IServiceListener() {
						public void serviceAdded(IServiceEvent evt) {
							discoveryView.addServiceInfo(evt.getServiceInfo().getServiceID());
							dc.requestServiceInfo(evt.getServiceInfo().getServiceID(),3000);
						}
						public void serviceRemoved(IServiceEvent evt) {
							discoveryView.removeServiceInfo(evt.getServiceInfo());
						}
						public void serviceResolved(IServiceEvent evt) {
							discoveryView.addServiceInfo(evt.getServiceInfo());
						}});
					dc.registerServiceType(svcID);
				}});
        }
	}
	public static void unregisterServerType() {
		if (discovery != null) {
			discovery.unregisterAllServices();
		}
	}
	
	public static void registerService(URI uri) {
		if (discovery != null) {
			try {
				String path = uri.getPath();
				Properties props = new Properties();
				String protocol = uri.getScheme();
				props.setProperty(PROP_CONTAINER_TYPE_NAME,PROP_CONTAINER_TYPE_VALUE);
				props.setProperty(PROP_PROTOCOL_NAME,protocol);
				props.setProperty(PROP_PW_REQ_NAME, PROP_PW_REQ_VALUE);
				props.setProperty(PROP_DEF_USER_NAME, PROP_DEF_USER_VALUE);
				props.setProperty(PROP_PATH_NAME, path);
				InetAddress host = InetAddress.getByName(uri.getHost());
				int port = uri.getPort();
				String svcName = System.getProperty("user.name")+"."+protocol;
				ServiceInfo svcInfo = new ServiceInfo(host, new ServiceID(TCPSERVER_DISCOVERY_TYPE,svcName), port, SVC_DEF_PRIORITY,
						SVC_DEF_WEIGHT, props);
				discovery.registerService(svcInfo);
			} catch (IOException e) {
				ClientPlugin.log("Exception registering service "+uri);
			}
		} else {
			ClientPlugin.log("Cannot register service "+uri+" because no discovery service is available");
		}
	}

	public static void unregisterServer(ISharedObjectContainer container) {

	}

	public static void registerServiceTypes() {
		if (discovery != null) {
			for(int i=0; i < serviceTypes.length; i++) {
				discovery.registerServiceType(serviceTypes[i]);
			}
		}
	}


}