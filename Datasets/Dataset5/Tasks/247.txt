.getProperty(RemoteConstants.ENDPOINT_CONNECTTARGET_ID);

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
import java.util.Iterator;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.osgi.framework.ServiceReference;

public class HostContainerSelector extends AbstractHostContainerSelector
		implements IHostContainerSelector {

	private boolean autoCreateContainer = false;

	public HostContainerSelector(String[] defaultConfigTypes,
			boolean autoCreateContainer) {
		super(defaultConfigTypes);
		this.autoCreateContainer = autoCreateContainer;
	}

	public IRemoteServiceContainer[] selectHostContainers(
			ServiceReference serviceReference,
			String[] serviceExportedInterfaces,
			String[] serviceExportedConfigs, String[] serviceIntents) {
		// Find previously created containers that match the given
		// serviceExportedConfigs and serviceIntents
		Collection rsContainers = findExistingHostContainers(serviceReference,
				serviceExportedInterfaces, serviceExportedConfigs,
				serviceIntents);

		if (rsContainers.size() == 0 && autoCreateContainer) {
			// If no existing containers are found we'll go through
			// finding/creating/configuring/connecting
			rsContainers = createAndConfigureHostContainers(serviceReference,
					serviceExportedInterfaces, serviceExportedConfigs,
					serviceIntents);

			// if SERVICE_EXPORTED_CONTAINER_CONNECT_TARGET service property is
			// specified, then
			// connect the host container(s)
			Object target = serviceReference
					.getProperty(RemoteConstants.EXPORTED_CONTAINER_CONNECT_TARGET);
			if (target != null) {
				for (Iterator i = rsContainers.iterator(); i.hasNext();) {
					IContainer container = ((IRemoteServiceContainer) i.next())
							.getContainer();
					try {
						connectHostContainer(serviceReference, container,
								target);
					} catch (Exception e) {
						logException("doConnectContainer failure containerID=" //$NON-NLS-1$
								+ container.getID() + " target=" + target, e); //$NON-NLS-1$
					}
				}

			}
		}

		// return result
		return (IRemoteServiceContainer[]) rsContainers
				.toArray(new IRemoteServiceContainer[] {});
	}

	public void close() {
	}
}