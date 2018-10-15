serviceInfo = new ServiceInfo(Constants.DISCOVERY_SERVICE_TYPE, null, 80, serviceID, new ServiceProperties(new DiscoveryProperties(className, ECF_GENERIC_CLIENT, serviceHostContainer)));

package org.eclipse.ecf.internal.examples.remoteservices.server;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.ServiceInfo;
import org.eclipse.ecf.discovery.ServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.ecf.discovery.service.IDiscoveryService;
import org.eclipse.ecf.examples.remoteservices.common.IRemoteEnvironmentInfo;
import org.eclipse.ecf.remoteservice.Constants;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.util.DiscoveryProperties;
import org.eclipse.ecf.remoteservice.util.RemoteServiceProperties;
import org.eclipse.osgi.service.environment.EnvironmentInfo;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.util.tracker.ServiceTracker;

/**
 * The activator class controls the plug-in life cycle
 */
public class Activator implements BundleActivator {

	private static final String ECF_GENERIC_CLIENT = "ecf.generic.client";

	private static final String ECF_DISCOVERY_JMDNS = "ecf.discovery.jmdns";

	// The plug-in ID
	public static final String PLUGIN_ID = "org.eclipse.ecf.examples.remoteservices.server";

	private static final String REMOTE_SERVICE_TYPE = "_" + Constants.DISCOVERY_SERVICE_TYPE + "._tcp.local.";

	private static final String DEFAULT_CONNECT_TARGET = "ecftcp://ecf.eclipse.org:3283/server";

	// The shared instance
	private static Activator plugin;

	private BundleContext context;

	private IContainer serviceHostContainer;

	private IServiceInfo serviceInfo;

	private IDiscoveryContainerAdapter discovery;

	private ServiceTracker environmentInfoTracker;

	/**
	 * The constructor
	 */
	public Activator() {
	}

	public EnvironmentInfo getEnvironmentInfo() {
		if (environmentInfoTracker == null) {
			environmentInfoTracker = new ServiceTracker(context, org.eclipse.osgi.service.environment.EnvironmentInfo.class.getName(), null);
			environmentInfoTracker.open();
		}
		return (EnvironmentInfo) environmentInfoTracker.getService();
	}

	private void registerRemoteService(String className, Object service) {
		try {
			final IRemoteServiceContainerAdapter containerAdapter = (IRemoteServiceContainerAdapter) serviceHostContainer.getAdapter(IRemoteServiceContainerAdapter.class);
			Assert.isNotNull(containerAdapter);
			// register remote service
			containerAdapter.registerRemoteService(new String[] {className}, service, new RemoteServiceProperties(ECF_GENERIC_CLIENT, serviceHostContainer));
			System.out.println("Remote service registered for class " + className);

			// then register for discovery
			final String serviceName = System.getProperty("user.name") + System.currentTimeMillis();
			final IServiceID serviceID = ServiceIDFactory.getDefault().createServiceID(discovery.getServicesNamespace(), REMOTE_SERVICE_TYPE, serviceName);
			serviceInfo = new ServiceInfo(null, 80, serviceID, new ServiceProperties(new DiscoveryProperties(className, ECF_GENERIC_CLIENT, serviceHostContainer)));
			// register discovery here
			discovery.registerService(serviceInfo);
			System.out.println("Service registered for discovery with IServiceID: " + serviceID);
		} catch (final Exception e) {
			e.printStackTrace();
		}
	}

	private void setupDiscovery() {
		try {
			if (discovery == null) {
				final ServiceTracker serviceTracker = new ServiceTracker(context, IDiscoveryService.class.getName(), null);
				serviceTracker.open();
				// XXX this should not be done in Activator...but we're going do do it anyway
				discovery = (IDiscoveryContainerAdapter) serviceTracker.waitForService(5000);
				serviceTracker.close();
				if (discovery == null) {
					final IContainer discoveryContainer = ContainerFactory.getDefault().createContainer(ECF_DISCOVERY_JMDNS);
					discoveryContainer.connect(null, null);
					discovery = (IDiscoveryContainerAdapter) discoveryContainer.getAdapter(IDiscoveryContainerAdapter.class);
				}
			}
		} catch (final Exception e) {
			e.printStackTrace();
		}
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ui.plugin.AbstractUIPlugin#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext context) throws Exception {
		plugin = this;
		this.context = context;
		setupDiscovery();
		createAndConnectServiceHostContainer();
		registerRemoteService(IRemoteEnvironmentInfo.class.getName(), new RemoteEnvironmentInfoImpl());
	}

	private void createAndConnectServiceHostContainer() {
		try {
			serviceHostContainer = ContainerFactory.getDefault().createContainer(ECF_GENERIC_CLIENT);
			final ID targetID = IDFactory.getDefault().createID(serviceHostContainer.getConnectNamespace(), DEFAULT_CONNECT_TARGET);
			serviceHostContainer.connect(targetID, null);
		} catch (final Exception e) {
			e.printStackTrace();
		}
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.ui.plugin.AbstractUIPlugin#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		plugin = null;
		if (serviceInfo != null) {
			if (discovery != null) {
				discovery.unregisterService(serviceInfo);
				serviceInfo = null;
				final IContainer container = (IContainer) discovery.getAdapter(IContainer.class);
				if (container != null) {
					container.disconnect();
				}
				discovery = null;
			}
		}
		if (serviceHostContainer != null) {
			serviceHostContainer.disconnect();
			serviceHostContainer = null;
		}
		if (environmentInfoTracker != null) {
			environmentInfoTracker.close();
			environmentInfoTracker = null;
		}
		this.context = null;
	}

	/**
	 * Returns the shared instance
	 *
	 * @return the shared instance
	 */
	public static Activator getDefault() {
		return plugin;
	}

}