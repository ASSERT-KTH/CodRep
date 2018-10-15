import org.eclipse.ecf.discovery.identity.ServiceID;

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
package org.eclipse.ecf.example.collab;

import org.eclipse.ecf.discovery.IDiscoveryContainer;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.IServiceTypeListener;
import org.eclipse.ecf.discovery.ServiceID;
import org.eclipse.ecf.ui.views.DiscoveryView;
import org.eclipse.ecf.ui.views.IDiscoveryController;

public class CollabDiscoveryView extends DiscoveryView {
	protected static final int SERVICE_REQUEST_TIMEOUT = 3000;
	public CollabDiscoveryView() {
		super();
		setShowTypeDetails(false);
		this.setDiscoveryController(ClientPlugin.getDefault()
				.getDiscoveryController());
	}
	public void setDiscoveryController(final IDiscoveryController controller) {
		super.setDiscoveryController(controller);
		if (controller != null) {
			final IDiscoveryContainer dc = controller.getDiscoveryContainer();
			if (dc != null) {
				// setup listeners
				dc.addServiceTypeListener(new IServiceTypeListener() {
					public void serviceTypeAdded(IServiceEvent event) {
						ServiceID svcID = event.getServiceInfo().getServiceID();
						addServiceTypeInfo(svcID.getServiceType());
						dc.addServiceListener(event.getServiceInfo()
								.getServiceID(), new IServiceListener() {
							public void serviceAdded(IServiceEvent evt) {
								addServiceInfo(evt.getServiceInfo()
										.getServiceID());
								dc.requestServiceInfo(evt.getServiceInfo()
										.getServiceID(),
										SERVICE_REQUEST_TIMEOUT);
							}
							public void serviceRemoved(IServiceEvent evt) {
								removeServiceInfo(evt.getServiceInfo());
							}
							public void serviceResolved(IServiceEvent evt) {
								addServiceInfo(evt.getServiceInfo());
							}
						});
						dc.registerServiceType(svcID);
					}
				});
			}
		}
	}
	public void dispose() {
		IDiscoveryController c = getController();
		if (c != null && c.isDiscoveryStarted()) {
			c.stopDiscovery();
		}
		super.dispose();
	}
}