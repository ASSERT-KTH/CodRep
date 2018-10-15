private volatile ServiceTracker tracker;

/*******************************************************************************
 * Copyright (c) 2007 Versant Corp.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Kuppe (mkuppe <at> versant <dot> com) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.provider.discovery;

import java.util.*;
import org.eclipse.ecf.discovery.service.IDiscoveryService;
import org.eclipse.ecf.provider.discovery.CompositeDiscoveryContainer;
import org.osgi.framework.*;
import org.osgi.util.tracker.ServiceTracker;

/**
 * 
 */
public class Activator implements BundleActivator {
	// The shared instance
	private static Activator plugin;
	public static final String PLUGIN_ID = "org.eclipse.ecf.provider.discovery"; //$NON-NLS-1$

	/**
	 * Returns the shared instance
	 * 
	 * @return the shared instance
	 */
	public static Activator getDefault() {
		return plugin;
	}

	private ServiceTracker tracker;

	/**
	 * The constructor
	 */
	public Activator() {
		plugin = this;
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.core.runtime.Plugins#start(org.osgi.framework.BundleContext)
	 */
	public void start(final BundleContext context) throws Exception {
		// get all previously registered IDS from OSGi
		tracker = new ServiceTracker(context, IDiscoveryService.class.getName(), null);
		tracker.open();
		Object[] services = tracker.getServices();
		List discoveries = services == null ? new ArrayList() : new ArrayList(Arrays.asList(services));

		// register the composite discovery service)
		final CompositeDiscoveryContainer cdc = new CompositeDiscoveryContainer(discoveries);
		cdc.connect(null, null);
		Properties props = new Properties();
		props.put(IDiscoveryService.CONTAINER_ID, cdc.getID());
		props.put(IDiscoveryService.CONTAINER_NAME, CompositeDiscoveryContainer.NAME);
		context.registerService(IDiscoveryService.class.getName(), cdc, props);

		// add a service listener to add/remove IDS dynamically 
		context.addServiceListener(new ServiceListener() {
			/* (non-Javadoc)
			 * @see org.osgi.framework.ServiceListener#serviceChanged(org.osgi.framework.ServiceEvent)
			 */
			public void serviceChanged(ServiceEvent arg0) {
				IDiscoveryService anIDS = (IDiscoveryService) context.getService(arg0.getServiceReference());
				switch (arg0.getType()) {
					case ServiceEvent.REGISTERED :
						cdc.addContainer(anIDS);
						break;
					case ServiceEvent.UNREGISTERING :
						cdc.removeContainer(anIDS);
						break;
					default :
						break;
				}
			}

		}, "(" + Constants.OBJECTCLASS + "=" + IDiscoveryService.class.getName() + ")"); //$NON-NLS-1$//$NON-NLS-2$ //$NON-NLS-3$
	}

	/*
	 * (non-Javadoc)
	 * @see org.eclipse.core.runtime.Plugin#stop(org.osgi.framework.BundleContext)
	 */
	public void stop(BundleContext context) throws Exception {
		if (tracker != null) {
			tracker.close();
			tracker = null;
		}
		plugin = null;
	}
}