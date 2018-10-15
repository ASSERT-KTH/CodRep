IContainer[] allContainers = getContainers();

/*******************************************************************************
 * Copyright (c) 2009 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.osgi.services.distribution;

import java.util.ArrayList;
import java.util.List;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.IRemoteServiceEndpointDescription;
import org.eclipse.ecf.osgi.services.discovery.RemoteServicePublication;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;

/**
 * Default implementation of IProxyContainerFinder.
 * 
 */
public class DefaultProxyContainerFinder extends AbstractContainerFinder
		implements IProxyContainerFinder {

	protected IContainer[] getContainers(IServiceID serviceID,
			IRemoteServiceEndpointDescription endpointDescription) {

		// Get all containers available
		IContainer[] allContainers = getAllContainers();
		// If none then return null
		if (allContainers == null)
			return null;

		List results = new ArrayList();
		for (int i = 0; i < allContainers.length; i++) {
			// Do *not* include containers with same ID as endpoint ID
			ID containerID = allContainers[i].getID();
			if (containerID == null
					|| containerID
							.equals(endpointDescription.getEndpointAsID()))
				continue;
			// And make sure that the namespaces match
			if (includeContainerWithConnectNamespace(
					allContainers[i],
					(String) endpointDescription
							.getProperty(RemoteServicePublication.ENDPOINT_CONTAINERID_NAMESPACE)))
				results.add(allContainers[i]);
		}
		return (IContainer[]) results.toArray(new IContainer[] {});
	}

	protected IRemoteServiceContainer[] getRemoteServiceContainers(
			IServiceID serviceID,
			IRemoteServiceEndpointDescription endpointDescription) {
		IContainer[] containers = getContainers(serviceID, endpointDescription);
		if (containers == null)
			return null;

		return getRemoteServiceContainers(containers);
	}

	public IRemoteServiceContainer[] findProxyContainers(IServiceID serviceID,
			IRemoteServiceEndpointDescription endpointDescription,
			IProgressMonitor monitor) {
		trace("findProxyContainers", "serviceID=" + serviceID
				+ " endpointDescription=" + endpointDescription);
		// Get remote service containers under consideration
		IRemoteServiceContainer[] rsContainers = getRemoteServiceContainers(
				serviceID, endpointDescription);
		// If none available then return
		if (rsContainers == null) {
			logWarning("findProxyContainers",
					"No remote service containers found");
			return EMPTY_REMOTE_SERVICE_CONTAINER_ARRAY;
		}
		trace("findProxyContainers", "getRemoteServiceContainers.length="
				+ rsContainers.length);

		ID connectTargetID = endpointDescription.getConnectTargetID();
		IRemoteServiceContainer[] connectedContainers = (connectTargetID == null) ? rsContainers
				: connectRemoteServiceContainers(rsContainers, connectTargetID,
						monitor);
		if (connectedContainers == null) {
			logWarning("findProxyContainers",
					"No remote service containers found after connect");
			return EMPTY_REMOTE_SERVICE_CONTAINER_ARRAY;
		}
		trace("findProxyContainers", "connectRemoteServiceContainers.length="
				+ rsContainers.length);
		return connectedContainers;
	}

	protected IConnectContext getConnectContext(
			IRemoteServiceContainer rsContainer, ID connectTargetID) {
		return null;
	}

	protected IRemoteServiceContainer[] connectRemoteServiceContainers(
			IRemoteServiceContainer[] rsContainers, ID connectTargetID,
			IProgressMonitor monitor) {
		List results = new ArrayList();
		for (int i = 0; i < rsContainers.length; i++) {
			IContainer c = rsContainers[i].getContainer();
			try {
				// If the container is not already connected,
				// then connect it to the connectTargetID
				if (c.getConnectedID() == null) {
					connectContainer(c, connectTargetID, getConnectContext(
							rsContainers[i], connectTargetID));
				}
				// If it's connected (either was already connected or was
				// connected via lines above...then add it to result set
				results.add(rsContainers[i]);
			} catch (ContainerConnectException e) {
				logError("connectRemoteServiceContainers",
						"Exception connecting container=" + c.getID()
								+ " to connectTargetID=" + connectTargetID, e);
			}
		}
		return (IRemoteServiceContainer[]) results
				.toArray(new IRemoteServiceContainer[] {});
	}

}