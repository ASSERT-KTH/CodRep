trace("selectConsumerContainers", "endpointDescription=" + endpointDescription); //$NON-NLS-1$ //$NON-NLS-2$

/*******************************************************************************
 * Copyright (c) 2010-2011 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.remoteserviceadmin;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;

public class ConsumerContainerSelector extends
		AbstractConsumerContainerSelector implements IConsumerContainerSelector {

	private boolean autoCreateContainer = false;

	public ConsumerContainerSelector(boolean autoCreateContainer) {
		this.autoCreateContainer = autoCreateContainer;
	}

	public IRemoteServiceContainer selectConsumerContainer(
			EndpointDescription endpointDescription) {
		trace("selectConsumerContainers", "endpointDescription=" + endpointDescription); //$NON-NLS-1$

		// Get the endpointID
		ID endpointContainerID = endpointDescription.getContainerID();

		String[] remoteSupportedConfigs = (String[]) endpointDescription
				.getProperties()
				.get(org.osgi.service.remoteserviceadmin.RemoteConstants.REMOTE_CONFIGS_SUPPORTED);

		// Get connect targetID
		ID connectTargetID = endpointDescription.getConnectTargetID();

		IRemoteServiceContainer rsContainer = selectExistingConsumerContainer(
				endpointContainerID, remoteSupportedConfigs, connectTargetID);

		// If we haven't found any existing containers then we create one
		// from the remoteSupportedConfigs...*iff* autoCreateContainer is
		// set to true
		if (rsContainer == null && autoCreateContainer)
			rsContainer = createAndConfigureConsumerContainer(
					remoteSupportedConfigs, endpointDescription.getProperties());

		// Get the connect target ID from the endpointDescription
		// and connect the given containers to the connect targetID
		// This is only needed when when the endpointID is different from
		// the connect targetID, and the containers are not already connected
		connectContainerToTarget(rsContainer, connectTargetID);

		return rsContainer;
	}

	public void close() {
	}

}