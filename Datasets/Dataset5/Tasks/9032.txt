serviceInfo = new ServiceInfo(UPDATE_SITE_SERVICE_TYPE, null, getServicePort(), ServiceIDFactory.getDefault().createServiceID(discovery.getServicesNamespace(), serviceType1, serviceName1), new ServiceProperties(new UpdateSiteProperties(serviceName1, servicePath1).toProperties()));

package org.eclipse.ecf.internal.examples.updatesite;

import java.net.URL;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.discovery.*;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.ecf.discovery.service.IDiscoveryService;
import org.osgi.framework.BundleActivator;
import org.osgi.framework.BundleContext;
import org.osgi.service.http.HttpService;
import org.osgi.util.tracker.ServiceTracker;

public class Activator implements BundleActivator {

	static final String PLUGIN_ID = "org.eclipse.ecf.examples.updatesite.server"; //$NON-NLS-1$
	static final String UPDATE_SITE_SERVICE_TYPE = Messages.Activator_UPDATE_SITE_SERVICE;
	static final String HTTP_SERVICE_TYPE = "http"; //$NON-NLS-1$

	public static final String DEFAULT_SERVICE_TYPE = "_" + UPDATE_SITE_SERVICE_TYPE + "._" + HTTP_SERVICE_TYPE + "._tcp.local."; //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
	private static final String DEFAULT_SERVICE_PATH = "/update"; //$NON-NLS-1$
	private static final String DEFAULT_SERVICE_NAME_SUFFIX = " update site"; //$NON-NLS-1$

	// Properties
	private String username;
	protected String serviceType;
	private String serviceName;

	private String servicePath;
	// Update site name and location
	private String updateSiteName;
	private URL updateSiteLocation;

	private static Activator plugin;
	private BundleContext context;

	private ServiceTracker httpServiceTracker;
	private ServiceTracker discoveryTracker;

	private IDiscoveryContainerAdapter discovery;
	private IServiceInfo serviceInfo;

	public static Activator getDefault() {
		return plugin;
	}

	public void setupProperties() throws Exception {
		// Username is org.eclipse.ecf.examples.updatesite.server.username.  Default is System property "user.name"
		username = System.getProperty("username", System.getProperty("user.name")); //$NON-NLS-1$ //$NON-NLS-2$
		serviceType = System.getProperty("serviceType", DEFAULT_SERVICE_TYPE); //$NON-NLS-1$
		serviceName = System.getProperty("serviceName", username + DEFAULT_SERVICE_NAME_SUFFIX); //$NON-NLS-1$
		servicePath = System.getProperty("servicePath", DEFAULT_SERVICE_PATH); //$NON-NLS-1$
		updateSiteName = System.getProperty("updateSiteName", username + DEFAULT_SERVICE_NAME_SUFFIX); //$NON-NLS-1$
		String uSiteLocation = System.getProperty("updateSiteLocation"); //$NON-NLS-1$
		if (!uSiteLocation.endsWith("/")) //$NON-NLS-1$
			uSiteLocation += "/"; //$NON-NLS-1$

		try {
			updateSiteLocation = new URL(uSiteLocation);
		} catch (final Exception e) {
			e.printStackTrace();
			throw e;
		}
	}

	public void setupDiscovery() throws Exception {
		try {
			ContainerFactory.getDefault().getDescriptions();
			Thread.sleep(1000);
			discovery = getDiscoveryService();
			if (discovery == null) {
				final IContainer discoveryContainer = ContainerFactory.getDefault().createContainer("ecf.discovery.jmdns"); //$NON-NLS-1$
				discoveryContainer.connect(null, null);
				discovery = (IDiscoveryContainerAdapter) discoveryContainer.getAdapter(IDiscoveryContainerAdapter.class);
			}
		} catch (final Exception e) {
			e.printStackTrace();
		}
	}

	/*
	 * (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#start(org.osgi.framework.BundleContext)
	 */
	public void start(BundleContext ctxt) throws Exception {
		plugin = this;
		context = ctxt;

		// Get/setup properties
		setupProperties();
		// Setup discovery
		setupDiscovery();
		// Setup http server/service
		registerHttpResource(servicePath, "/", updateSiteLocation); //$NON-NLS-1$
		// Register service with discovery
		registerService(serviceType, serviceName, updateSiteName, servicePath);
	}

	private void registerService(String serviceType1, String serviceName1, String updateSiteName1, String servicePath1) throws Exception {
		try {
			serviceInfo = new ServiceInfo(null, getServicePort(), ServiceIDFactory.getDefault().createServiceID(discovery.getServicesNamespace(), serviceType1, serviceName1), new ServiceProperties(new UpdateSiteProperties(serviceName1, servicePath1).toProperties()));
			discovery.registerService(serviceInfo);
		} catch (final Exception e) {
			e.printStackTrace();
			throw e;
		}

	}

	private int getServicePort() {
		final String osgiPort = System.getProperty("org.osgi.service.http.port"); //$NON-NLS-1$
		Integer servicePort = new Integer(80);
		if (osgiPort != null) {
			servicePort = Integer.valueOf(osgiPort);
		}
		return servicePort.intValue();
	}

	public void registerHttpResource(String alias, String servicePath1, URL fileSystemLocation) throws Exception {
		try {
			final HttpService httpService = getHttpService();
			if (httpService == null)
				throw new NullPointerException("Http service not found."); //$NON-NLS-1$
			httpService.registerResources(alias, servicePath1, new UpdateSiteContext(httpService.createDefaultHttpContext(), fileSystemLocation));

		} catch (final Exception e) {
			e.printStackTrace();
			throw e;
		}
	}

	/*
	 * (non-Javadoc)
	 * @see org.osgi.framework.BundleActivator#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext ctxt) throws Exception {
		if (discovery != null && serviceInfo != null) {
			discovery.unregisterService(serviceInfo);
			discovery = null;
			serviceInfo = null;
		}
		if (httpServiceTracker != null) {
			httpServiceTracker.close();
			httpServiceTracker = null;
		}
		if (discoveryTracker != null) {
			discoveryTracker.close();
			discoveryTracker = null;
		}

		ctxt = null;
		plugin = null;
	}

	public HttpService getHttpService() {
		if (httpServiceTracker == null) {
			httpServiceTracker = new ServiceTracker(context, HttpService.class.getName(), null);
			httpServiceTracker.open();
		}
		return (HttpService) httpServiceTracker.getService();
	}

	public IDiscoveryService getDiscoveryService() {
		if (discoveryTracker == null) {
			discoveryTracker = new ServiceTracker(context, IDiscoveryService.class.getName(), null);
			discoveryTracker.open();
		}
		return (IDiscoveryService) discoveryTracker.getService();
	}

}