container = ContainerFactory.getDefault().createContainer("ecf.discovery.jmdns"); //$NON-NLS-1$

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
package org.eclipse.ecf.internal.example.collab.start;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.discovery.IDiscoveryContainerAdapter;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceTypeEvent;
import org.eclipse.ecf.discovery.IServiceTypeListener;

public class Discovery {

	IContainer container = null;
	IDiscoveryContainerAdapter discoveryContainer = null;

	public Discovery() throws Exception {
		startDiscovery();
	}

	private void startDiscovery() throws Exception {
		container = ContainerFactory.getDefault().createContainer("ecf.discovery.jmdns");
		container.connect(null, null);
		discoveryContainer = (IDiscoveryContainerAdapter) container.getAdapter(IDiscoveryContainerAdapter.class);
		discoveryContainer.addServiceTypeListener(new CollabServiceTypeListener());
	}

	class CollabServiceTypeListener implements IServiceTypeListener {
		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceTypeListener#serviceTypeDiscovered(org.eclipse.ecf.discovery.IServiceTypeEvent)
		 */
		public void serviceTypeDiscovered(IServiceTypeEvent event) {
			discoveryContainer.addServiceListener(event.getServiceTypeID(), new CollabServiceListener());
		}
	}

	class CollabServiceListener implements IServiceListener {
		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceListener#serviceDiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceDiscovered(IServiceEvent anEvent) {
			// TODO Auto-generated method stub

		}

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.discovery.IServiceListener#serviceUndiscovered(org.eclipse.ecf.discovery.IServiceEvent)
		 */
		public void serviceUndiscovered(IServiceEvent anEvent) {
			// TODO Auto-generated method stub

		}
	}
}