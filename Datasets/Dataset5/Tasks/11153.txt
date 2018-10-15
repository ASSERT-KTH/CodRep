private Vector listeners = new Vector();

package org.eclipse.ecf.provider.jmdns.container;

import java.io.IOException;
import java.net.InetAddress;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;
import java.util.Vector;
import java.util.logging.ConsoleHandler;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.jmdns.JmDNS;
import javax.jmdns.ServiceEvent;
import javax.jmdns.ServiceInfo;
import javax.jmdns.ServiceListener;
import javax.jmdns.ServiceTypeListener;

import org.eclipse.core.runtime.Platform;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.ContainerConnectedEvent;
import org.eclipse.ecf.core.events.ContainerConnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.ContainerDisconnectingEvent;
import org.eclipse.ecf.core.events.ContainerDisposeEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.identity.IDInstantiationException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.identity.ServiceID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.discovery.IDiscoveryContainer;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.ServiceContainerEvent;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.provider.jmdns.JmdnsPlugin;
import org.eclipse.ecf.provider.jmdns.Trace;
import org.eclipse.ecf.provider.jmdns.identity.JMDNSServiceID;

public class JMDNSDiscoveryContainer implements IContainer,
		IDiscoveryContainer, ServiceListener, ServiceTypeListener {

	public static final int DEFAULT_REQUEST_TIMEOUT = 3000;
	static Trace trace = Trace.create("container");

	public static final String JMDNS_NAMESPACE_ID = JmdnsPlugin.getDefault().getNamespaceIdentifier();
	
	protected static void trace(String msg) {
		if (trace != null && Trace.ON) {
			trace.msg(msg);
		}
	}

	ContainerConfig config = null;
	InetAddress intf = null;
	JmDNS jmdns = null;
	Object lock = new Object();
	int requestTimeout = DEFAULT_REQUEST_TIMEOUT;
	Map serviceListeners = new HashMap();
	Vector serviceTypeListeners = new Vector();
	private Vector listeners = null;

	public JMDNSDiscoveryContainer() throws IOException,
			IDInstantiationException {
		this(null);
	}
	public ID getID() {
		if (config == null) return null;
		else return config.getID();
	}
	public JMDNSDiscoveryContainer(InetAddress addr) throws IOException,
			IDInstantiationException {
		super();
		trace("<init>");
		intf = (addr == null) ? InetAddress.getLocalHost() : addr;
		this.config = new ContainerConfig(IDFactory
				.getDefault().makeStringID(JMDNSDiscoveryContainer.class.getName()));
	}

	public void addServiceListener(ServiceID type, IServiceListener listener) {
		if (type == null || listener == null)
			return;
		synchronized (serviceListeners) {
			Vector v = (Vector) serviceListeners.get(type);
			if (v == null) {
				v = new Vector();
				serviceListeners.put(type, v);
			}
			v.add(listener);
		}
	}

	public void addServiceTypeListener(IServiceTypeListener listener) {
		serviceTypeListeners.add(listener);
	}

	protected void fireContainerEvent(IContainerEvent event) {
		synchronized (listeners) {
			for (Iterator i = listeners.iterator(); i.hasNext();) {
				IContainerListener l = (IContainerListener) i.next();
				l.handleEvent(event);
			}
		}
	}
	public void dispose() {
		fireContainerEvent(new ContainerDisposeEvent(getID()));
		disconnect();
	}

	protected void fireServiceAdded(ServiceEvent arg0) {
		IServiceInfo iinfo = makeIServiceInfoFromServiceEvent(arg0);
		ServiceID svcID = makeServiceID(arg0.getType(), null);
		synchronized (serviceListeners) {
			Vector v = (Vector) serviceListeners.get(svcID);
			if (v != null) {
				for (Iterator i = v.iterator(); i.hasNext();) {
					IServiceListener l = (IServiceListener) i.next();
					l.serviceAdded(new ServiceContainerEvent(iinfo, config
							.getID()));
				}
			}
		}
	}

	protected void fireServiceRemoved(ServiceEvent arg0) {
		IServiceInfo iinfo = makeIServiceInfoFromServiceEvent(arg0);
		ServiceID svcID = makeServiceID(arg0.getType(), null);
		synchronized (serviceListeners) {
			Vector v = (Vector) serviceListeners.get(svcID);
			if (v != null) {
				for (Iterator i = v.iterator(); i.hasNext();) {
					IServiceListener l = (IServiceListener) i.next();
					l.serviceRemoved(new ServiceContainerEvent(iinfo, config
							.getID()));
				}
			}
		}
	}

	protected void fireServiceResolved(ServiceEvent arg0) {
		IServiceInfo iinfo = makeIServiceInfoFromServiceEvent(arg0);
		ServiceID svcID = makeServiceID(arg0.getType(), null);
		synchronized (serviceListeners) {
			Vector v = (Vector) serviceListeners.get(svcID);
			if (v != null) {
				for (Iterator i = v.iterator(); i.hasNext();) {
					IServiceListener l = (IServiceListener) i.next();
					l.serviceResolved(new ServiceContainerEvent(iinfo, config
							.getID()));
				}
			}
		}
	}

	protected void fireServiceTypeAdded(ServiceEvent arg0) {
		synchronized (serviceTypeListeners) {
			for (Iterator i = serviceTypeListeners.iterator(); i.hasNext();) {
				IServiceTypeListener l = (IServiceTypeListener) i.next();
				l
						.serviceTypeAdded(new ServiceContainerEvent(
								makeIServiceInfoFromServiceEvent(arg0), config
										.getID()));
			}
		}
	}

	public Object getAdapter(Class adapter) {
		if (adapter.isInstance(this)) {
			return this;
		} else {
			return Platform.getAdapterManager().getAdapter(this, adapter);
		}
	}

	public ID getConnectedID() {
		return null;
	}

	public IServiceInfo getServiceInfo(ServiceID service, int timeout) {
		trace("getServiceInfo(" + service + "," + timeout + ")");
		synchronized (lock) {
			if (jmdns != null) {
				return makeIServiceInfoFromServiceInfo(jmdns.getServiceInfo(
						service.getServiceType(), service.getServiceName(),
						timeout));
			} else
				return null;
		}
	}

	public IServiceInfo[] getServices(ServiceID type) {
		IServiceInfo svs[] = new IServiceInfo[0];
		synchronized (lock) {
			if (jmdns != null) {
				ServiceInfo[] svcs = jmdns.list(type.getServiceType());
				if (svcs != null) {
					svs = new IServiceInfo[svcs.length];
					for (int i = 0; i < svcs.length; i++) {
						svs[i] = makeIServiceInfoFromServiceInfo(svcs[i]);
					}
				}
			}
		}
		return svs;
	}

	public void connect(ID groupID, IConnectContext joinContext)
			throws ContainerConnectException {
		fireContainerEvent(new ContainerConnectingEvent(this
				.getID(), groupID, joinContext));
		synchronized (lock) {
			try {
				if (this.jmdns == null) {
					if (trace != null) {
						Logger logger = Logger.getLogger(JmDNS.class.toString());
						ConsoleHandler handler = new ConsoleHandler();
						logger.addHandler(handler);
						logger.setLevel(Level.FINER);
						handler.setLevel(Level.FINER);
					}
					this.jmdns = new JmDNS(intf);
					jmdns.addServiceTypeListener(this);
				}
				if (groupID != null && groupID instanceof JMDNSServiceID) {
					ServiceID svcid = (ServiceID) groupID;
					jmdns.addServiceListener(svcid.getServiceType(), this);
				}
			} catch (IOException e) {
				ContainerConnectException soe = new ContainerConnectException(
						"Exception creating JmDNS instance");
				soe.setStackTrace(e.getStackTrace());
				throw soe;
			}
		}
		fireContainerEvent(new ContainerConnectedEvent(this
				.getID(), groupID));
	}

	public void disconnect() {
		fireContainerEvent(new ContainerDisconnectingEvent(this
				.getID(), getConnectedID()));
		synchronized (lock) {
			if (this.jmdns != null) {
				jmdns.close();
				jmdns = null;
			}
		}
		fireContainerEvent(new ContainerDisconnectedEvent(this
				.getID(), getConnectedID()));
	}

	protected IServiceInfo makeIServiceInfoFromServiceEvent(ServiceEvent event) {
		ServiceID sID = makeServiceID(event.getType(), event.getName());
		ServiceInfo sinfo = event.getInfo();
		if (sinfo != null) {
			return makeIServiceInfoFromServiceInfo(sinfo);
		}
		IServiceInfo newInfo = new JMDNSServiceInfo(null, sID, -1, -1, -1,
				new ServiceProperties());
		return newInfo;
	}

	protected IServiceInfo makeIServiceInfoFromServiceInfo(
			final ServiceInfo serviceInfo) {
		if (serviceInfo == null)
			return null;
		ServiceID sID = makeServiceID(serviceInfo.getType(), serviceInfo
				.getName());
		InetAddress addr = serviceInfo.getAddress();
		int port = serviceInfo.getPort();
		int priority = serviceInfo.getPriority();
		int weight = serviceInfo.getWeight();
		IServiceProperties newProps = new IServiceProperties() {
			public Enumeration getPropertyNames() {
				return serviceInfo.getPropertyNames();
			}
			public String getPropertyString(String name) {
				return serviceInfo.getPropertyString(name);
			}
			public byte[] getPropertyBytes(String name) {
				return serviceInfo.getPropertyBytes(name);
			}
			public Object getProperty(String name) {
				return getPropertyBytes(name);
			}
		};
		IServiceInfo newInfo = new JMDNSServiceInfo(addr, sID, port, priority,
				weight, newProps);
		return newInfo;
	}

	protected ServiceID makeServiceID(String type, String name) {
		ServiceID id = null;
		try {
			id = (ServiceID) IDFactory.getDefault().makeID(JMDNS_NAMESPACE_ID, new Object[] {
					type, name });
		} catch (IDInstantiationException e) {
			// Should never happen
			if (trace != null) {
				trace.dumpStack(e, "JDNSDiscoveryContainer.makeServiceID");
			}
		}
		return id;
	}
	protected ServiceInfo makeServiceInfoFromIServiceInfo(
			IServiceInfo serviceInfo) {
		if (serviceInfo == null)
			return null;
		ServiceID sID = serviceInfo.getServiceID();
		Hashtable props = new Hashtable();
		IServiceProperties svcProps = serviceInfo.getServiceProperties();
		if (svcProps != null) {
			for (Enumeration e=svcProps.getPropertyNames(); e.hasMoreElements(); ) {
				String key = (String) e.nextElement();
				Object val = svcProps.getProperty(key);
				if (val != null) {
					props.put(key, val);
				}
			}
		}
		ServiceInfo si = new ServiceInfo(sID.getServiceType(), sID
				.getServiceName(), serviceInfo.getPort(), serviceInfo
				.getPriority(), serviceInfo.getWeight(), props);
		return si;
	}

	protected String prepareSvcTypeForBonjour(String svcType) {
		String result = svcType;
		if (svcType.endsWith(".local.")) {
			result = svcType.substring(0, svcType.indexOf(".local."));
		}
		return result;
	}

	public void registerService(IServiceInfo serviceInfo) throws IOException {
		registerServiceWithJmDNS(serviceInfo);
	}

	public void registerServiceType(ServiceID serviceType) {
		String type = serviceType.getServiceType();
		trace("registerServiceType(" + type + ")");
		registerServiceType(type);
	}

	public void registerServiceType(String serviceType) {
		trace("registerServiceType(" + serviceType + ")");
		synchronized (lock) {
			if (jmdns != null) {
				jmdns.registerServiceType(serviceType);
				jmdns.addServiceListener(serviceType, this);
			}
		}
	}

	protected void registerServiceWithJmDNS(IServiceInfo serviceInfo)
			throws IOException {
		synchronized (lock) {
			if (trace != null) {
				trace.msg("registering service with jmdns: " + serviceInfo);
			}
			jmdns.registerService(makeServiceInfoFromIServiceInfo(serviceInfo));
		}
	}

	public void removeServiceListener(ServiceID type, IServiceListener listener) {
		if (type == null || listener == null)
			return;
		synchronized (serviceListeners) {
			Vector v = (Vector) serviceListeners.get(type);
			if (v == null) {
				return;
			}
			v.remove(listener);
		}
	}

	public void removeServiceTypeListener(IServiceTypeListener listener) {
		serviceTypeListeners.add(listener);
	}

	public void requestServiceInfo(ServiceID service, int timeout) {
		trace("requestServiceInfo(" + service + "," + timeout + ")");
		synchronized (lock) {
			if (jmdns != null) {
				jmdns.requestServiceInfo(service.getServiceType(), service
						.getServiceName(), timeout);
			}
		}
	}

	public void serviceAdded(ServiceEvent arg0) {
		synchronized (lock) {
			if (jmdns != null) {
				try {
					fireServiceAdded(arg0);
				} catch (Exception e) {
					if (trace != null) {
						trace.dumpStack(e,
								"JMDNSDiscoveryContainer.serviceAdded(" + arg0
										+ ")");
					}
				}
			}
		}
	}

	public void serviceRemoved(ServiceEvent arg0) {
		synchronized (lock) {
			if (jmdns != null) {
				try {
					fireServiceRemoved(arg0);
				} catch (Exception e) {
					if (trace != null) {
						trace.dumpStack(e,
								"JMDNSDiscoveryContainer.serviceRemoved("
										+ arg0 + ")");
					}
				}
			}
		}
	}

	public void serviceResolved(ServiceEvent arg0) {
		synchronized (lock) {
			if (jmdns != null) {
				try {
					fireServiceResolved(arg0);
				} catch (Exception e) {
					if (trace != null) {
						trace.dumpStack(e,
								"JMDNSDiscoveryContainer.serviceResolved("
										+ arg0 + ")");
					}
				}
			}
		}
	}

	public void serviceTypeAdded(ServiceEvent arg0) {
		synchronized (lock) {
			if (jmdns != null) {
				try {
					fireServiceTypeAdded(arg0);
				} catch (Exception e) {
					if (trace != null) {
						trace.dumpStack(e,
								"JMDNSDiscoveryContainer.serviceTypeAdded("
										+ arg0 + ")");
					}
				}
			}
		}
	}

	public void unregisterAllServices() {
		synchronized (lock) {
			if (jmdns != null) {
				if (trace != null) {
					trace.msg("unregistering all services");
				}
				jmdns.unregisterAllServices();
			}
		}
	}

	public void unregisterService(IServiceInfo serviceInfo) {
		synchronized (lock) {
			if (jmdns != null) {
				if (trace != null) {
					trace
							.msg("unregistring service with jmdns: "
									+ serviceInfo);
				}
				jmdns
						.unregisterService(makeServiceInfoFromIServiceInfo(serviceInfo));
			}
		}
	}
	public Namespace getConnectNamespace() {
		return IDFactory.getDefault().getNamespaceByName(JMDNS_NAMESPACE_ID);
	}
	public void addListener(IContainerListener l, String filter) {
		synchronized (listeners) {
			listeners.add(l);
		}
	}
	public void removeListener(IContainerListener l) {
		synchronized (listeners) {
			listeners.remove(l);
		}
	}

}