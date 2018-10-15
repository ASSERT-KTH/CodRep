root = new TreeParent(null,"Services",null);

package org.eclipse.ecf.ui.views;

import java.net.InetAddress;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map;

import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.identity.ServiceID;
import org.eclipse.ecf.discovery.IDiscoveryContainer;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.viewers.DoubleClickEvent;
import org.eclipse.jface.viewers.IDoubleClickListener;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IWorkbenchActionConstants;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;


public class DiscoveryView extends ViewPart {
    protected static final int TREE_EXPANSION_LEVELS = 3;
	private TreeViewer viewer;
	private Action requestServiceInfoAction;
	private Action registerServiceTypeAction;
	private Action connectToAction;
	
	IDiscoveryContainer container = null;
	
	public void setDiscoveryContainer(IDiscoveryContainer container) {
		this.container = container;
	}
	class TreeObject implements IAdaptable {
		private String name;
		private TreeParent parent;
		public TreeObject(String name) {
			this.name = name;
		}
		public String getName() {
			return name;
		}
		public void setParent(TreeParent parent) {
			this.parent = parent;
		}
		public TreeParent getParent() {
			return parent;
		}
		public String toString() {
			return getName();
		}
		public Object getAdapter(Class key) {
			return null;
		}
	}
	
	class TreeParent extends TreeObject {
		private ArrayList children;
		private ServiceID id;
		private URI serviceURI;
		public TreeParent(ServiceID id, String name, URI uri) {
			super(name);
			this.id = id;
			children = new ArrayList();
			serviceURI = uri;
		}
		public URI getServiceURI() {
			return serviceURI;
		}
		public ServiceID getID() {
			return id;
		}
		public void addChild(TreeObject child) {
			children.add(child);
			child.setParent(this);
		}
		public void removeChild(TreeObject child) {
			children.remove(child);
			child.setParent(null);
		}
		public TreeObject [] getChildren() {
			return (TreeObject [])children.toArray(new TreeObject[children.size()]);
		}
		public boolean hasChildren() {
			return children.size()>0;
		}
	}

	class ViewContentProvider implements IStructuredContentProvider, 
										   ITreeContentProvider {
		private TreeParent invisibleRoot;
		protected TreeParent root;
		
		public void inputChanged(Viewer v, Object oldInput, Object newInput) {
		}
		public void dispose() {
		}
		public Object[] getElements(Object parent) {
			if (parent.equals(getViewSite())) {
				if (invisibleRoot==null) initialize();
				return getChildren(invisibleRoot);
			}
			return getChildren(parent);
		}
		public Object getParent(Object child) {
			if (child instanceof TreeObject) {
				return ((TreeObject)child).getParent();
			}
			return null;
		}
		public Object [] getChildren(Object parent) {
			if (parent instanceof TreeParent) {
				return ((TreeParent)parent).getChildren();
			}
			return new Object[0];
		}
		public boolean hasChildren(Object parent) {
			if (parent instanceof TreeParent)
				return ((TreeParent)parent).hasChildren();
			return false;
		}
		private void initialize() {
			invisibleRoot = new TreeParent(null,"",null);
			root = new TreeParent(null,"Discovered Service Types",null);
			invisibleRoot.addChild(root);
		}
		void replaceOrAdd(TreeParent top, TreeParent newEntry) {
			TreeObject [] childs = top.getChildren();
			for(int i=0; i < childs.length; i++) {
				if (childs[i] instanceof TreeParent) {
					ServiceID childID = ((TreeParent) childs[i]).getID();
					if (childID.equals(newEntry.getID())) {
						// It's already there...replace
						top.removeChild(childs[i]);
					}
				}
			}
			// Now add
			top.addChild(newEntry);
		}
		void addServiceTypeInfo(String type) {
			TreeParent typenode = findServiceTypeNode(type);
			if (typenode == null) {
				root.addChild(new TreeParent(null,type,null));
			}
		}
		TreeParent findServiceTypeNode(String typename) {
			TreeObject[] types = root.getChildren();
			for(int i=0; i < types.length; i++) {
				if (types[i] instanceof TreeParent) {
					String type = types[i].getName();
					if (type.equals(typename)) {
						return (TreeParent) types[i];
					}
				}
			}
			return null;
		}
		void addServiceInfo(ServiceID id) { 
			TreeParent typenode = findServiceTypeNode(id.getServiceType());
			if (typenode == null) {
				typenode = new TreeParent(null,id.getServiceType(),null);
				root.addChild(typenode);
			}
			TreeParent newEntry = new TreeParent(id,id.getServiceName(),null);
			replaceOrAdd(typenode,newEntry);
		}
		void addServiceInfo(IServiceInfo serviceInfo) {
			if (serviceInfo == null) return;
			ServiceID svcID = serviceInfo.getServiceID();
			TreeParent typenode = findServiceTypeNode(svcID.getServiceType());
			URI uri = null;
			try {
				uri = serviceInfo.getServiceURI();
			} catch (URISyntaxException e) {
				
			}
			if (typenode == null) {
				typenode = new TreeParent(null,svcID.getServiceType(),uri);
				root.addChild(typenode);
			}
			TreeParent newEntry = new TreeParent(svcID,svcID.getServiceName(),uri);
			InetAddress addr = serviceInfo.getAddress();
			if (addr != null) {
				TreeObject toaddr = new TreeObject("Address: "+addr.getHostAddress());
				newEntry.addChild(toaddr);
			}
			TreeObject typeo = new TreeObject("Type: " + svcID.getServiceType());
			newEntry.addChild(typeo);
			TreeObject porto = new TreeObject("Port: " + serviceInfo.getPort());
			newEntry.addChild(porto);
			/*
			TreeObject prioo = new TreeObject("Priority: " + serviceInfo.getPriority());
			newEntry.addChild(prioo);
			TreeObject weighto = new TreeObject("Weight: " + serviceInfo.getWeight());
			newEntry.addChild(weighto);
			*/
			TreeObject urio = new TreeObject("URI: "+uri);
			newEntry.addChild(urio);
			Map props = serviceInfo.getProperties();
			if (props != null) {
				for(Iterator i=props.keySet().iterator(); i.hasNext(); ) {
					Object key = i.next();
					if (key instanceof String) {
						String keys = (String) key;
						Object val = props.get(key);
						if (val instanceof String) {
							TreeObject prop = new TreeObject(keys+"="+(String)val);
							newEntry.addChild(prop);
						}
					}
				}
			}
			replaceOrAdd(typenode,newEntry);
		}
		void removeServiceInfo(IServiceInfo serviceInfo) {
			if (serviceInfo == null) return;
			ServiceID svcID = serviceInfo.getServiceID();
			TreeParent typenode = findServiceTypeNode(svcID.getServiceType());
			if (typenode == null) {
				return;
			}
			TreeObject [] childs = (TreeObject []) typenode.getChildren();
			for(int i=0; i < childs.length; i++) {
				if (childs[i] instanceof TreeParent) {
					TreeParent parent = (TreeParent) childs[i];
					ServiceID existingID = parent.getID();
					if (existingID.equals(svcID)) {
						typenode.removeChild(parent);
					}
				}
			}
		}
	}
	class ViewLabelProvider extends LabelProvider {

		public String getText(Object obj) {
			return obj.toString();
		}
		public Image getImage(Object obj) {
			String imageKey = null;
			if (obj instanceof TreeParent) {
				if (((TreeParent) obj).getID() != null) {
					imageKey = ISharedImages.IMG_OBJ_ELEMENT;
				} else {
					imageKey = ISharedImages.IMG_OBJ_FOLDER;
				}
			}
			return PlatformUI.getWorkbench().getSharedImages().getImage(imageKey);
		}
	}
	/**
	 * The constructor.
	 */
	public DiscoveryView() {
	}
	
	IServiceConnectListener serviceConnectListener = null;
	public DiscoveryView(IServiceConnectListener listener) {
		this.serviceConnectListener = listener;
	}
	public void addServiceTypeInfo(final String type) {
        Display.getDefault().asyncExec(new Runnable() {
            public void run() {
                try {
                    ViewContentProvider vcp = (ViewContentProvider) viewer
                    .getContentProvider();
            		if (vcp != null) {
            			vcp.addServiceTypeInfo(type);
            			refreshView();
            		} 
                } catch (Exception e) {
                }
            }
        });
	}
	public void addServiceInfo(final IServiceInfo serviceInfo) {
        Display.getDefault().asyncExec(new Runnable() {
            public void run() {
                try {
                    ViewContentProvider vcp = (ViewContentProvider) viewer
                    .getContentProvider();
            		if (vcp != null) {
            			vcp.addServiceInfo(serviceInfo);
            			refreshView();
            		} 
                } catch (Exception e) {
                }
            }
        });
	}
	public void addServiceInfo(final ServiceID id) {
        Display.getDefault().asyncExec(new Runnable() {
            public void run() {
                try {
                    ViewContentProvider vcp = (ViewContentProvider) viewer
                    .getContentProvider();
            		if (vcp != null) {
            			vcp.addServiceInfo(id);
            			refreshView();
            		} 
                } catch (Exception e) {
                }
            }
        });
	}
	public void removeServiceInfo(final IServiceInfo serviceInfo) {
        Display.getDefault().asyncExec(new Runnable() {
            public void run() {
                try {
                    ViewContentProvider vcp = (ViewContentProvider) viewer
                    .getContentProvider();
            		if (vcp != null) {
            			vcp.removeServiceInfo(serviceInfo);
            			refreshView();
            		} 
                } catch (Exception e) {
                }
            }
        });
	}
    protected void refreshView() {
        Display.getDefault().asyncExec(new Runnable() {
            public void run() {
                try {
                    viewer.refresh();
                    expandAll();
                } catch (Exception e) {
                }
            }
        });
    }
    protected void expandAll() {
        viewer.expandToLevel(TREE_EXPANSION_LEVELS);
    }

	private void makeActions() {
		requestServiceInfoAction = new Action() {
            public void run() {
                TreeObject treeObject = getSelectedTreeObject();
                if (treeObject instanceof TreeParent) {
                	TreeParent p = (TreeParent) treeObject;
                    final ServiceID targetID = p.getID();
                    if (container != null) {
                    	container.requestServiceInfo(targetID,3000);
                    }
                }
            }
		};
		requestServiceInfoAction.setText("Request info...");
		requestServiceInfoAction.setToolTipText("Request info for selected service");
		requestServiceInfoAction.setEnabled(true);
		
		registerServiceTypeAction = new Action() {
            public void run() {
                TreeObject treeObject = getSelectedTreeObject();
                if (treeObject instanceof TreeParent) {
                	TreeParent p = (TreeParent) treeObject;
                    if (container != null) {
                    	container.registerServiceType(p.getName());
                    }
                }
            }
		};
		registerServiceTypeAction.setText("Register type...");
		registerServiceTypeAction.setToolTipText("Register for selected service type");
		registerServiceTypeAction.setEnabled(true);

		connectToAction = new Action() {
            public void run() {
                TreeObject treeObject = getSelectedTreeObject();
                if (treeObject instanceof TreeParent) {
                	TreeParent p = (TreeParent) treeObject;
                	URI uri = p.getServiceURI();
                	connectToContainer(uri);
                }
            }
		};
		connectToAction.setText("Connect to service...");
		connectToAction.setToolTipText("Connect to this service");
		connectToAction.setEnabled(true);
}
	private void fillContextMenu(IMenuManager manager) {
		final TreeObject treeObject = getSelectedTreeObject();
		if (treeObject != null && treeObject instanceof TreeParent) {
			TreeParent tp = (TreeParent) treeObject;
			if (tp.getID() != null) {
				requestServiceInfoAction.setText("Request info about "+tp.getName());
				manager.add(requestServiceInfoAction);
				URI uri = tp.getServiceURI();
				if (uri != null) {
					connectToAction.setText("Connect to this service");
					manager.add(connectToAction);
				}
			} else {
				if (!tp.equals(((ViewContentProvider) viewer.getContentProvider()).root)) {
					registerServiceTypeAction.setText("Register type "+tp.getName());
					manager.add(registerServiceTypeAction);
				}
			}
		}
		// Other plug-ins can contribute there actions here
		manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));
	}
	protected void connectToContainer(URI svcURI) {
    	if (serviceConnectListener != null) {
    		serviceConnectListener.connectToService(svcURI);
    	} else {
    		System.out.println("Would connect to "+svcURI);
    	}
	}
    protected TreeObject getSelectedTreeObject() {
        ISelection selection = viewer.getSelection();
        Object obj = ((IStructuredSelection) selection)
                .getFirstElement();
        TreeObject treeObject = (TreeObject) obj;
        return treeObject;
    }
	public void createPartControl(Composite parent) {
		viewer = new TreeViewer(parent, SWT.MULTI | SWT.H_SCROLL | SWT.V_SCROLL);
		viewer.setContentProvider(new ViewContentProvider());
		viewer.setLabelProvider(new ViewLabelProvider());
		viewer.setInput(getViewSite());
		makeActions();
		hookContextMenu();
		hookDoubleClickAction();
	}

	private void hookContextMenu() {
		MenuManager menuMgr = new MenuManager("#PopupMenu");
		menuMgr.setRemoveAllWhenShown(true);
		menuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {
				DiscoveryView.this.fillContextMenu(manager);
			}
		});
		Menu menu = menuMgr.createContextMenu(viewer.getControl());
		viewer.getControl().setMenu(menu);
		getSite().registerContextMenu(menuMgr, viewer);
	}
	
	private void hookDoubleClickAction() {
		viewer.addDoubleClickListener(new IDoubleClickListener() {
			public void doubleClick(DoubleClickEvent event) {
				Object obj = ((IStructuredSelection) event.getSelection())
                .getFirstElement();
				final TreeObject treeObject = (TreeObject) obj;
				if (treeObject != null && treeObject instanceof TreeParent) {
					TreeParent tp = (TreeParent) treeObject;
					if (tp.getID() != null) {
						requestServiceInfoAction.run();
					}
				}
			}
		});
	}
	public void dispose() {
		container = null;
	}
	/**
	 * Passing the focus request to the viewer's control.
	 */
	public void setFocus() {
		viewer.getControl().setFocus();
	}
}
 No newline at end of file