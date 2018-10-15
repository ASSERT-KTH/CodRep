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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.ContainerCreateException;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.RemoteServiceContainer;
import org.osgi.framework.ServiceReference;

public abstract class AbstractHostContainerSelector extends
		AbstractContainerSelector {

	private static final String NODEFAULT = "<<nodefault>>"; //$NON-NLS-1$
	protected String[] defaultConfigTypes;

	public AbstractHostContainerSelector(String[] defaultConfigTypes) {
		this.defaultConfigTypes = defaultConfigTypes;
	}

	protected Collection findExistingHostContainers(
			ServiceReference serviceReference,
			String[] serviceExportedInterfaces,
			String[] serviceExportedConfigs, String[] serviceIntents) {
		List results = new ArrayList();
		// Get all existing containers
		IContainer[] containers = getContainers();
		// If nothing there, then return empty array
		if (containers == null || containers.length == 0)
			return results;

		for (int i = 0; i < containers.length; i++) {
			// Check to make sure it's a rs container adapter. If it's not go
			// onto next one
			IRemoteServiceContainerAdapter adapter = hasRemoteServiceContainerAdapter(containers[i]);
			if (adapter == null)
				continue;
			// Get container type description and intents
			ContainerTypeDescription description = getContainerTypeDescription(containers[i]);
			// If it has no description go onto next
			if (description == null)
				continue;

			if (matchExistingHostContainer(serviceReference, containers[i],
					adapter, description, serviceExportedConfigs,
					serviceIntents)) {
				trace("findExistingContainers", "INCLUDING containerID=" //$NON-NLS-1$ //$NON-NLS-2$
						+ containers[i].getID()
						+ "configs=" //$NON-NLS-1$
						+ ((serviceExportedConfigs == null) ? "null" : Arrays //$NON-NLS-1$
								.asList(serviceExportedConfigs).toString())
						+ "intents=" //$NON-NLS-1$
						+ ((serviceIntents == null) ? "null" : Arrays.asList( //$NON-NLS-1$
								serviceIntents).toString()));
				results.add(new RemoteServiceContainer(containers[i], adapter));
			} else {
				trace("findExistingContainers", "EXCLUDING containerID=" //$NON-NLS-1$ //$NON-NLS-2$
						+ containers[i].getID()
						+ "configs=" //$NON-NLS-1$
						+ ((serviceExportedConfigs == null) ? "null" : Arrays //$NON-NLS-1$
								.asList(serviceExportedConfigs).toString())
						+ "intents=" //$NON-NLS-1$
						+ ((serviceIntents == null) ? "null" : Arrays.asList( //$NON-NLS-1$
								serviceIntents).toString()));
			}
		}
		return results;
	}

	protected boolean matchHostContainerToConnectTarget(
			ServiceReference serviceReference, IContainer container) {
		Object target = serviceReference
				.getProperty(RemoteConstants.EXPORTED_CONTAINER_CONNECT_TARGET);
		if (target == null)
			return true;
		// If a targetID is specified, make sure it either matches what the
		// container
		// is already connected to, or that we connect an unconnected container
		ID connectedID = container.getConnectedID();
		// If the container is not already connected to anything
		// then we connect it to the given target
		if (connectedID == null) {
			// connect to the target and we have a match
			try {
				connectHostContainer(serviceReference, container, target);
			} catch (Exception e) {
				logException("doConnectContainer containerID=" //$NON-NLS-1$
						+ container.getID() + " target=" + target, e); //$NON-NLS-1$
				return false;
			}
			return true;
		} else {
			ID targetID = createTargetID(container, target);
			// We check here if the currently connectedID equals the target.
			// If it does we have a match
			if (connectedID.equals(targetID))
				return true;
		}
		return false;
	}

	protected boolean matchExistingHostContainer(
			ServiceReference serviceReference, IContainer container,
			IRemoteServiceContainerAdapter adapter,
			ContainerTypeDescription description, String[] requiredConfigTypes,
			String[] requiredServiceIntents) {

		return matchHostSupportedConfigTypes(requiredConfigTypes, description)
				&& matchHostSupportedIntents(requiredServiceIntents,
						description)
				&& matchHostContainerID(serviceReference, container)
				&& matchHostContainerToConnectTarget(serviceReference,
						container);
	}

	protected boolean matchHostContainerID(ServiceReference serviceReference,
			IContainer container) {

		ID containerID = container.getID();
		// No match if the container has no ID
		if (containerID == null)
			return false;

		// Then get containerid if specified directly by user in properties
		ID requiredContainerID = (ID) serviceReference
				.getProperty(RemoteConstants.EXPORTED_CONTAINER_ID);
		// If the CONTAINER_I
		if (requiredContainerID != null) {
			return requiredContainerID.equals(containerID);
		}
		// Else get the container factory arguments, create an ID from the
		// arguments
		// and check if the ID matches that
		Namespace ns = containerID.getNamespace();
		Object cid = serviceReference
				.getProperty(RemoteConstants.EXPORTED_CONTAINER_FACTORY_ARGS);
		// If no arguments are present, then any container ID should match
		if (cid == null)
			return true;
		ID cID = null;
		if (cid instanceof ID) {
			cID = (ID) cid;
		} else if (cid instanceof String) {
			cID = getIDFactory().createID(ns, (String) cid);
		} else if (cid instanceof Object[]) {
			Object cido = ((Object[]) cid)[0];
			cID = getIDFactory().createID(ns, new Object[] { cido });
		}
		if (cID == null)
			return true;
		return containerID.equals(cID);
	}

	protected boolean matchHostSupportedConfigTypes(
			String[] requiredConfigTypes,
			ContainerTypeDescription containerTypeDescription) {
		// if no config type is set the spec requires to create a default
		// endpoint (see section 122.5.1)
		if (requiredConfigTypes == null)
			return true;
		// Get supported config types for this description
		String[] supportedConfigTypes = getSupportedConfigTypes(containerTypeDescription);
		// If it doesn't support anything, return false
		if (supportedConfigTypes == null || supportedConfigTypes.length == 0)
			return false;
		// Turn supported config types for this description into list
		List supportedConfigTypesList = Arrays.asList(supportedConfigTypes);
		List requiredConfigTypesList = Arrays.asList(requiredConfigTypes);
		// We check all of the required config types and make sure
		// that they are present in the supportedConfigTypes
		boolean result = true;
		for (Iterator i = requiredConfigTypesList.iterator(); i.hasNext();)
			result &= supportedConfigTypesList.contains(i.next());
		return result;
	}

	protected Collection createAndConfigureHostContainers(
			ServiceReference serviceReference,
			String[] serviceExportedInterfaces, String[] requiredConfigs,
			String[] requiredIntents) {

		List results = new ArrayList();
		ContainerTypeDescription[] descriptions = getContainerTypeDescriptions();
		if (descriptions == null)
			return results;
		// If there are no required configs specified, then create any defaults
		if (requiredConfigs == null || requiredConfigs.length == 0)
			createDefaultRSContainers(serviceReference, descriptions, results);
		else {
			// See if we have a match
			for (int i = 0; i < descriptions.length; i++) {
				IRemoteServiceContainer rsContainer = createMatchingContainer(
						descriptions[i], serviceReference,
						serviceExportedInterfaces, requiredConfigs,
						requiredIntents);
				if (rsContainer != null)
					results.add(rsContainer);
			}
		}
		// we still haven't created one then we check for no default and if
		// not present then we
		// create default ones
		if (results.size() == 0 && requiredConfigs != null
				&& requiredConfigs.length > 0) {
			List requiredConfigsList = Arrays.asList(requiredConfigs);
			if (!requiredConfigsList.contains(NODEFAULT))
				createDefaultRSContainers(serviceReference, descriptions,
						results);
		}
		return results;
	}

	private void createDefaultRSContainers(ServiceReference serviceReference,
			ContainerTypeDescription[] descriptions, List results) {
		ContainerTypeDescription[] ctds = getContainerTypeDescriptionsForDefaultConfigTypes(descriptions);
		if (ctds != null) {
			for (int i = 0; i < ctds.length; i++) {
				IRemoteServiceContainer rsContainer = createRSContainer(
						serviceReference, ctds[i]);
				if (rsContainer != null)
					results.add(rsContainer);
			}
		}
	}

	protected ContainerTypeDescription[] getContainerTypeDescriptionsForDefaultConfigTypes(
			ContainerTypeDescription[] descriptions) {
		String[] defaultConfigTypes = getDefaultConfigTypes();
		if (defaultConfigTypes == null || defaultConfigTypes.length == 0)
			return null;
		List results = new ArrayList();
		for (int i = 0; i < descriptions.length; i++) {
			// For each description, get supported config types
			String[] supportedConfigTypes = descriptions[i]
					.getSupportedConfigs();
			if (supportedConfigTypes != null
					&& matchDefaultConfigTypes(defaultConfigTypes,
							supportedConfigTypes))
				results.add(descriptions[i]);
		}
		return (ContainerTypeDescription[]) results
				.toArray(new ContainerTypeDescription[] {});
	}

	protected boolean matchDefaultConfigTypes(String[] defaultConfigTypes,
			String[] supportedConfigTypes) {
		List supportedConfigTypesList = Arrays.asList(supportedConfigTypes);
		for (int i = 0; i < defaultConfigTypes.length; i++) {
			if (supportedConfigTypesList.contains(defaultConfigTypes[i]))
				return true;
		}
		return false;
	}

	protected String[] getDefaultConfigTypes() {
		return defaultConfigTypes;
	}

	protected IRemoteServiceContainer createMatchingContainer(
			ContainerTypeDescription containerTypeDescription,
			ServiceReference serviceReference,
			String[] serviceExportedInterfaces, String[] requiredConfigs,
			String[] requiredIntents) {

		if (matchHostSupportedConfigTypes(requiredConfigs,
				containerTypeDescription)
				&& matchHostSupportedIntents(requiredIntents,
						containerTypeDescription)) {
			return createRSContainer(serviceReference, containerTypeDescription);
		}
		return null;
	}

	protected IRemoteServiceContainer createRSContainer(
			ServiceReference serviceReference,
			ContainerTypeDescription containerTypeDescription) {
		try {
			IContainer container = createContainer(serviceReference,
					containerTypeDescription);
			IRemoteServiceContainerAdapter adapter = (IRemoteServiceContainerAdapter) container
					.getAdapter(IRemoteServiceContainerAdapter.class);
			if (adapter == null)
				throw new ContainerCreateException(
						"Container does not implement IRemoteServiceContainerAdapter"); //$NON-NLS-1$
			return new RemoteServiceContainer(container, adapter);
		} catch (Exception e) {
			logException(
					"Exception creating container from ContainerTypeDescription=" //$NON-NLS-1$
							+ containerTypeDescription, e);
			return null;
		}
	}

	protected void connectHostContainer(ServiceReference serviceReference,
			IContainer container, Object target)
			throws ContainerConnectException, IDCreateException {
		ID targetID = createTargetID(container, target);
		Object context = serviceReference
				.getProperty(RemoteConstants.EXPORTED_CONTAINER_CONNECT_CONTEXT);
		IConnectContext connectContext = null;
		if (context != null) {
			connectContext = createConnectContext(serviceReference, container,
					context);
		}
		// connect the container
		container.connect(targetID, connectContext);
	}

	protected boolean matchHostSupportedIntents(
			String[] serviceRequiredIntents,
			ContainerTypeDescription containerTypeDescription) {
		// If there are no required intents then we have a match
		if (serviceRequiredIntents == null)
			return true;

		String[] supportedIntents = getSupportedIntents(containerTypeDescription);

		if (supportedIntents == null)
			return false;

		List supportedIntentsList = Arrays.asList(supportedIntents);

		boolean result = true;
		for (int i = 0; i < serviceRequiredIntents.length; i++)
			result = result
					&& supportedIntentsList.contains(serviceRequiredIntents[i]);

		return result;
	}

}