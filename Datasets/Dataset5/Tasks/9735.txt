remoteSupportedConfigs, connectTargetID);

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.distribution;

import java.util.Collection;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.IRemoteServiceEndpointDescription;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;

/**
 * Default implementation of IProxyContainerFinder.
 * 
 */
public class DefaultProxyContainerFinder extends AbstractProxyContainerFinder
		implements IProxyContainerFinder {

	private boolean autoCreateContainer = false;

	public DefaultProxyContainerFinder(boolean autoCreateContainer) {
		this.autoCreateContainer = autoCreateContainer;
	}

	public IRemoteServiceContainer[] findProxyContainers(IServiceID serviceID,
			IRemoteServiceEndpointDescription endpointDescription) {

		trace("findProxyContainers", "serviceID=" + serviceID //$NON-NLS-1$ //$NON-NLS-2$
				+ " endpointDescription=" + endpointDescription); //$NON-NLS-1$

		// Get the endpointID
		ID endpointID = endpointDescription.getEndpointAsID();
		// Get the remote supported configs
		String[] remoteSupportedConfigs = endpointDescription
				.getSupportedConfigs();
		// Get connect targetID
		ID connectTargetID = endpointDescription.getConnectTargetID();

		// Find any/all existing containers for the proxy that
		// match the endpointID namespace and the remoteSupportedConfigs
		Collection rsContainers = findExistingProxyContainers(endpointID,
				remoteSupportedConfigs);

		// If we haven't found any existing containers then we create one
		// from the remoteSupportedConfigs...*iff* autoCreateContainer is
		// set to true
		if (rsContainers.size() == 0 && autoCreateContainer)
			rsContainers = createAndConfigureProxyContainers(
					remoteSupportedConfigs, endpointDescription.getProperties());

		// Get the connect target ID from the endpointDescription
		// and connect the given containers to the connect targetID
		// This is only needed when when the endpointID is different from
		// the connect targetID, and the containers are not already connected
		connectContainersToTarget(rsContainers, connectTargetID);

		return (IRemoteServiceContainer[]) rsContainers
				.toArray(new IRemoteServiceContainer[] {});
	}

}