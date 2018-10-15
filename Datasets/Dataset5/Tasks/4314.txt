package org.eclipse.ecf.tests.osgi.services.distribution.localdiscovery;

/*******************************************************************************
* Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.osgi.services.distribution.localdiscovery.generic;

import org.eclipse.ecf.osgi.services.discovery.local.DiscoveryCommandProvider;
import org.eclipse.ecf.tests.internal.osgi.services.distribution.localdiscovery.Activator;
import org.eclipse.osgi.framework.console.CommandProvider;
import org.osgi.util.tracker.ServiceTracker;

public class DiscoveryCommandProviderServiceTracker extends ServiceTracker {

	private DiscoveryCommandProvider discoveryCommandProvider;
	
	public DiscoveryCommandProviderServiceTracker() {
		super(Activator.getDefault().getContext(), CommandProvider.class.getName(), null);
		@SuppressWarnings("unused")
		DiscoveryCommandProvider dcp = new DiscoveryCommandProvider(null);
	}

	public void open() {
		super.open(true);
		Object[] allCommandProviders = getServices();
		for(int i=0; i < allCommandProviders.length; i++) {
			if (allCommandProviders[i] instanceof DiscoveryCommandProvider) {
				discoveryCommandProvider = (DiscoveryCommandProvider) allCommandProviders[i];
			}
		}
	}
	
	public DiscoveryCommandProvider getDiscoveryCommandProvider() {
		return discoveryCommandProvider;
	}
}