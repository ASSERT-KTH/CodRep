ID connectTargetID = endpointDescription.getConnectTargetID();

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import java.util.Collection;
import java.util.List;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;

public class ConsumerContainerSelector extends
		AbstractConsumerContainerSelector implements IConsumerContainerSelector {

	private boolean autoCreateContainer = false;

	public ConsumerContainerSelector(boolean autoCreateContainer) {
		this.autoCreateContainer = autoCreateContainer;
	}

	public IRemoteServiceContainer[] selectConsumerContainers(
			EndpointDescription endpointDescription) {
		trace("selectConsumerContainers", "endpointDescription=" + endpointDescription); //$NON-NLS-1$

		// Get the endpointID
		ID endpointID = endpointDescription.getContainerID();
		// Get the remote supported configs
		List<String> remoteSupportedConfigsList = endpointDescription
				.getConfigurationTypes();
		String[] remoteSupportedConfigs = (String[]) remoteSupportedConfigsList
				.toArray();
		// Get connect targetID
		ID connectTargetID = endpointDescription.getTargetID();

		// Find any/all existing containers for the proxy that
		// match the endpointID namespace and the remoteSupportedConfigs
		Collection rsContainers = findExistingProxyContainers(endpointID,
				remoteSupportedConfigs, connectTargetID);

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

	public void close() {
	}

}