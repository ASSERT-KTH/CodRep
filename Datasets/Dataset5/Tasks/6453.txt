System.out.println("http server\n\tupdateSiteLocation=" + updateSiteLocation + "\n\turl=" + serviceInfo.getLocation()); //$NON-NLS-1$ //$NON-NLS-2$

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.examples.updatesite;

import java.net.*;
import java.security.InvalidParameterException;
import java.util.Map;
import javax.naming.ServiceUnavailableException;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.discovery.*;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.identity.ServiceIDFactory;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.osgi.service.http.HttpService;

/**
 *
 */
public class DiscoverableServer implements IApplication {

	static final String DEFAULT_UPDATE_SITE_SERVICE_TYPE = "updatesite"; //$NON-NLS-1$

	private String username;
	protected String serviceType;
	private String serviceName;

	private String servicePath;
	private String updateSiteName;
	private URL updateSiteLocation;

	private IDiscoveryContainerAdapter discovery;
	private IServiceInfo serviceInfo;

	private boolean done = false;

	private String getCompleteServiceType() {
		return "_" + serviceType + "._http._tcp.local."; //$NON-NLS-1$ //$NON-NLS-2$ 
	}

	public DiscoverableServer() {
		// nothing to do
	}

	/* (non-Javadoc)
	 * @see org.eclipse.equinox.app.IApplication#start(org.eclipse.equinox.app.IApplicationContext)
	 */
	public Object start(IApplicationContext ctxt) throws Exception {
		Map args = ctxt.getArguments();
		initializeFromArguments((String[]) args.get("application.args")); //$NON-NLS-1$

		// Load and start ECF core bundles (to execute ecfstart jobs like discovery providers)
		ContainerFactory.getDefault().getDescriptions();

		// get discovery service
		discovery = Activator.getDefault().waitForDiscoveryService(5000);
		if (discovery == null)
			throw new ServiceUnavailableException("Discovery service not found."); //$NON-NLS-1$

		// Create service id
		IServiceID serviceID = ServiceIDFactory.getDefault().createServiceID(discovery.getServicesNamespace(), getCompleteServiceType(), serviceName);
		// create service info
		URI uri = URI.create("http://" + InetAddress.getLocalHost().getHostAddress() + ":" + getServicePort() + servicePath); //$NON-NLS-1$ //$NON-NLS-2$
		serviceInfo = new ServiceInfo(uri, serviceID, new ServiceProperties(new UpdateSiteProperties(serviceName).toProperties()));

		// get http service
		final HttpService httpService = Activator.getDefault().waitForHttpService(2000);
		if (httpService == null)
			throw new ServiceUnavailableException("Http service not found."); //$NON-NLS-1$

		// start http service
		httpService.registerResources(servicePath, "/", new UpdateSiteContext(httpService.createDefaultHttpContext(), updateSiteLocation)); //$NON-NLS-1$
		System.out.println("http server\n\tupdateSiteLocation=" + updateSiteLocation + "\n\turl=" + serviceInfo.getLocation() + servicePath); //$NON-NLS-1$ //$NON-NLS-2$

		// setup discovery
		discovery.registerService(serviceInfo);
		System.out.println("discovery publish\n\tserviceName=" + serviceID.getServiceName() + "\n\tserviceTypeID=" + serviceID.getServiceTypeID()); //$NON-NLS-1$ //$NON-NLS-2$

		// wait until done
		synchronized (this) {
			while (!done) {
				wait();
			}
		}
		return new Integer(0);
	}

	private int getServicePort() {
		final String osgiPort = System.getProperty("org.osgi.service.http.port"); //$NON-NLS-1$
		Integer servicePort = new Integer(80);
		if (osgiPort != null) {
			servicePort = Integer.valueOf(osgiPort);
		}
		return servicePort.intValue();
	}

	private void initializeFromArguments(String[] args) throws Exception {
		if (args == null)
			return;
		for (int i = 0; i < args.length; i++) {
			if (!args[i].startsWith("-")) { //$NON-NLS-1$
				String arg = args[i++];
				if (!arg.endsWith("/")) //$NON-NLS-1$
					arg = arg + "/"; //$NON-NLS-1$
				updateSiteLocation = new URL(arg);
			} else {
				if (args[i - 1].equalsIgnoreCase("-username")) //$NON-NLS-1$
					username = args[++i];
				else if (args[i - 1].equalsIgnoreCase("-serviceType")) //$NON-NLS-1$
					serviceType = args[++i];
				else if (args[i - 1].equalsIgnoreCase("-serviceName")) //$NON-NLS-1$
					serviceName = args[++i];
				else if (args[i - 1].equalsIgnoreCase("-servicePath")) //$NON-NLS-1$
					servicePath = args[++i];
				else if (args[i - 1].equalsIgnoreCase("-updateSiteName")) //$NON-NLS-1$
					updateSiteName = args[++i];
			}
		}
		if (updateSiteLocation == null) {
			usage();
			throw new InvalidParameterException("updateSiteDirectoryURL required"); //$NON-NLS-1$
		}
		username = (username == null) ? System.getProperty("user.name") : username; //$NON-NLS-1$
		serviceType = (serviceType == null) ? DEFAULT_UPDATE_SITE_SERVICE_TYPE : serviceType;
		serviceName = (serviceName == null) ? username + " update site" : serviceName; //$NON-NLS-1$
		servicePath = (servicePath == null) ? "/update" : servicePath; //$NON-NLS-1$
		updateSiteName = (updateSiteName == null) ? System.getProperty("updateSiteName", username + " update site") : updateSiteName; //$NON-NLS-1$ //$NON-NLS-2$
	}

	private void usage() {
		System.out.println("usage: eclipse -console [options] -application org.eclipse.ecf.examples.updatesite.server.updateSiteServer <updateSiteDirectoryURL>"); //$NON-NLS-1$
		System.out.println("   options: [-username <username>] default=<current user>"); //$NON-NLS-1$
		System.out.println("            [-serviceType <servicetype>] default=updatesite"); //$NON-NLS-1$
		System.out.println("            [-serviceName <name>] default=<current user> update site"); //$NON-NLS-1$
		System.out.println("            [-servicePath <path>] default=/update"); //$NON-NLS-1$
		System.out.println("            [-updateSiteName <name>] default=<current user> update site"); //$NON-NLS-1$
	}

	/* (non-Javadoc)
	 * @see org.eclipse.equinox.app.IApplication#stop()
	 */
	public void stop() {
		if (discovery != null && serviceInfo != null) {
			try {
				discovery.unregisterService(serviceInfo);
			} catch (ECFException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			discovery = null;
			serviceInfo = null;
		}
		synchronized (this) {
			done = true;
			notifyAll();
		}
	}

}