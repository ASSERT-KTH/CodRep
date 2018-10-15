package org.eclipse.ecf.internal.example.collab.start;

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
package org.eclipse.ecf.example.collab.start;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.identity.IServiceID;

public class Discovery {
	
	IContainer container = null;
	IDiscoveryContainerAdapter discoveryContainer = null;
	
	public Discovery() throws Exception {
		startDiscovery();
	}
	private void startDiscovery() throws Exception {
		container = ContainerFactory.getDefault().createContainer(
				"ecf.discovery.jmdns");
		container.connect(null, null);
		discoveryContainer = (IDiscoveryContainerAdapter) container
				.getAdapter(IDiscoveryContainerAdapter.class);
		discoveryContainer
				.addServiceTypeListener(new CollabServiceTypeListener());
		System.out.println("startDiscovery()");
	}
	
	class CollabServiceTypeListener implements IServiceTypeListener {
		public void serviceTypeAdded(IServiceEvent event) {
			System.out.println("serviceTypeAdded(" + event + ")");
			IServiceID svcID = event.getServiceInfo().getServiceID();
			discoveryContainer.addServiceListener(svcID.getServiceType(),
					new CollabServiceListener());
			discoveryContainer.registerServiceType(svcID.getServiceType());
		}
	}
	class CollabServiceListener implements IServiceListener {
		public void serviceAdded(IServiceEvent event) {
			System.out.println("serviceAdded(" + event + ")");
			discoveryContainer.requestServiceInfo(event.getServiceInfo()
					.getServiceID(), 3000);
		}
		public void serviceRemoved(IServiceEvent event) {
			System.out.println("serviceRemoved(" + event + ")");
		}
		public void serviceResolved(IServiceEvent event) {
			System.out.println("serviceResolved(" + event + ")");
		}
	}
}