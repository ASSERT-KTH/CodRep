(String[]) interfaces.toArray(), proxy, (Dictionary) proxyProperties);

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
import java.util.Collection;
import java.util.Collections;
import java.util.Dictionary;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.IDUtil;
import org.eclipse.ecf.remoteservice.IOSGiRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainerAdapter;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.osgi.framework.BundleContext;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;

public class RemoteServiceAdmin extends AbstractRemoteServiceAdmin implements
		org.osgi.service.remoteserviceadmin.RemoteServiceAdmin {

	private Collection<ExportRegistration> exportedRegistrations = new ArrayList<ExportRegistration>();

	private Collection<ImportRegistration> importedRegistrations = new ArrayList<ImportRegistration>();

	public RemoteServiceAdmin(BundleContext context) {
		super(context);
	}

	public Collection<org.osgi.service.remoteserviceadmin.ExportRegistration> exportService(
			ServiceReference serviceReference, Map<String, Object> properties) {
		String[] exportedInterfaces = (String[]) getPropertyValue(
				org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_EXPORTED_INTERFACES,
				serviceReference, properties);
		String[] exportedConfigs = (String[]) getPropertyValue(
				org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_EXPORTED_CONFIGS,
				serviceReference, properties);
		String[] serviceIntents = (String[]) getPropertyValue(
				org.osgi.service.remoteserviceadmin.RemoteConstants.SERVICE_INTENTS,
				serviceReference, properties);
		// Get a host container selector
		IHostContainerSelector hostContainerSelector = getHostContainerSelector();
		if (hostContainerSelector == null) {
			logError("handleServiceRegistering",
					"No hostContainerSelector available");
			return Collections.EMPTY_LIST;
		}
		// select ECF remote service containers that match given exported
		// interfaces, configs, and intents
		IRemoteServiceContainer[] rsContainers = hostContainerSelector
				.selectHostContainers(serviceReference, exportedInterfaces,
						exportedConfigs, serviceIntents);
		// If none found, log a warning and we're done
		if (rsContainers == null || rsContainers.length == 0) {
			logWarning(
					"handleServiceRegistered", "No remote service containers found for serviceReference=" //$NON-NLS-1$
							+ serviceReference
							+ ". Remote service NOT EXPORTED"); //$NON-NLS-1$
			return Collections.EMPTY_LIST;
		}
		Collection<org.osgi.service.remoteserviceadmin.ExportRegistration> results = new ArrayList<org.osgi.service.remoteserviceadmin.ExportRegistration>();
		synchronized (exportedRegistrations) {
			for (int i = 0; i < rsContainers.length; i++) {
				ExportRegistration rsRegistration = null;
				try {
					rsRegistration = doExportService(serviceReference,
							properties, exportedInterfaces, serviceIntents,
							rsContainers[i]);
				} catch (Exception e) {
					logError("exportService",
							"Exception exporting serviceReference="
									+ serviceReference + " with properties="
									+ properties + " rsContainerID="
									+ rsContainers[i].getContainer().getID(), e);
					rsRegistration = new ExportRegistration(e);
				}
				results.add(rsRegistration);
				exportedRegistrations.add(rsRegistration);
			}
		}
		return results;
	}

	private ExportRegistration doExportService(
			ServiceReference serviceReference, Map<String, Object> properties,
			String[] exportedInterfaces, String[] serviceIntents,
			IRemoteServiceContainer rsContainer) throws Exception {
		IRemoteServiceRegistration remoteRegistration = null;
		try {
			// Create remote service properties for remote service export
			Dictionary remoteServiceProperties = createRemoteServiceProperties(
					serviceReference, properties, rsContainer);
			// Get container adapter
			IRemoteServiceContainerAdapter containerAdapter = rsContainer
					.getContainerAdapter();
			// If it's an IOSGiRemoteServiceContainerAdapter then call it one
			// way
			if (containerAdapter instanceof IOSGiRemoteServiceContainerAdapter) {
				IOSGiRemoteServiceContainerAdapter osgiContainerAdapter = (IOSGiRemoteServiceContainerAdapter) containerAdapter;
				remoteRegistration = osgiContainerAdapter
						.registerRemoteService(exportedInterfaces,
								serviceReference, remoteServiceProperties);
			} else {
				// call it the normal way
				remoteRegistration = containerAdapter.registerRemoteService(
						exportedInterfaces, getService(serviceReference),
						remoteServiceProperties);
			}
			// Create EndpointDescription from remoteRegistration
			EndpointDescription endpointDescription = createExportEndpointDescription(
					serviceReference, properties, exportedInterfaces,
					serviceIntents, remoteRegistration, rsContainer);
			// Create ExportRegistration
			return createExportRegistration(remoteRegistration,
					serviceReference, endpointDescription);
		} catch (Exception e) {
			// If we actually created an IRemoteRegistration then unregister
			if (remoteRegistration != null)
				remoteRegistration.unregister();
			// rethrow
			throw e;
		}
	}

	private ExportRegistration createExportRegistration(
			IRemoteServiceRegistration remoteRegistration,
			ServiceReference serviceReference,
			EndpointDescription endpointDescription) {
		return new ExportRegistration(remoteRegistration, serviceReference,
				endpointDescription);
	}

	public org.osgi.service.remoteserviceadmin.ImportRegistration importService(
			org.osgi.service.remoteserviceadmin.EndpointDescription endpoint) {

		if (endpoint instanceof EndpointDescription) {
			EndpointDescription ed = (EndpointDescription) endpoint;
			IConsumerContainerSelector consumerContainerSelector = getConsumerContainerSelector();
			if (consumerContainerSelector == null) {
				logError("importService",
						"No consumerContainerSelector available");
				return null;
			}
			IRemoteServiceContainer rsContainer = consumerContainerSelector
					.selectConsumerContainer(ed);
			// If none found, log a warning and we're done
			if (rsContainer == null) {
				logWarning(
						"importService", "No remote service container selected for endpoint=" //$NON-NLS-1$
								+ endpoint + ". Remote service NOT IMPORTED"); //$NON-NLS-1$
				return null;
			}

			ImportRegistration importRegistration = null;
			synchronized (importedRegistrations) {
				try {
					importRegistration = doImportService(ed, rsContainer);
				} catch (ECFException e) {
					importRegistration = handleImportServiceException(ed,
							rsContainer, e);
				}
				if (importRegistration != null)
					importedRegistrations.add(importRegistration);
			}
			return importRegistration;
		} else
			return null;
	}

	private ImportRegistration handleImportServiceException(
			EndpointDescription endpoint,
			IRemoteServiceContainer iRemoteServiceContainer, Exception e) {
		// TODO Auto-generated method stub
		return null;
	}

	private String getFullRemoteServicesFilter(String remoteServicesFilter,
			long remoteServiceId) {
		if (remoteServiceId < 0)
			return remoteServicesFilter;
		StringBuffer filter = new StringBuffer("(&(") //$NON-NLS-1$
				.append(org.eclipse.ecf.remoteservice.Constants.SERVICE_ID)
				.append("=").append(remoteServiceId).append(")"); //$NON-NLS-1$ //$NON-NLS-2$
		if (remoteServicesFilter != null)
			filter.append(remoteServicesFilter);
		filter.append(")"); //$NON-NLS-1$
		return filter.toString();
	}

	private ImportRegistration doImportService(
			EndpointDescription endpointDescription,
			IRemoteServiceContainer rsContainer) throws ECFException {
		Collection<String> interfaces = endpointDescription.getInterfaces();
		ID endpointID = IDUtil.createContainerID(endpointDescription);
		ID targetID = endpointDescription.getConnectTargetID();
		ID[] idFilter = endpointDescription.getIDFilter();
		if (idFilter == null)
			idFilter = new ID[] { endpointID };

		String rsFilter = getFullRemoteServicesFilter(
				endpointDescription.getRemoteServiceFilter(),
				endpointDescription.getRemoteServiceId());

		Collection<IRemoteServiceReference> rsRefs = new ArrayList<IRemoteServiceReference>();
		IRemoteServiceContainerAdapter containerAdapter = rsContainer
				.getContainerAdapter();

		for (String intf : interfaces) {
			try {
				IRemoteServiceReference[] refs = containerAdapter
						.getRemoteServiceReferences(targetID, idFilter, intf,
								rsFilter);
				if (refs == null || refs.length == 0) {
					logWarning("doImportService",
							"getRemoteServiceReferences targetID=" + targetID
									+ ",idFilter=" + idFilter + ",intf=" + intf
									+ ",rsFilter=" + rsFilter
									+ " on rsContainer="
									+ rsContainer.getContainer().getID()
									+ " return null");
					continue;
				}
				for (int i = 0; i < refs.length; i++)
					rsRefs.add(refs[i]);
			} catch (Exception e) {

			}
		}
		if (rsRefs.size() == 0) {
			// This is an error...as no remote service reference was
			// available/reachable with given endpointDescription
			logError("doImportService",
					"remote service reference not found for targetID="
							+ targetID + ",idFilter=" + idFilter
							+ ",interfaces=" + interfaces + ",rsFilter="
							+ rsFilter + " on rsContainer="
							+ rsContainer.getContainer().getID());
			return null;
		}
		// The rsRefs collection should have a single reference in it. If it has
		// more than one, then something is wrong.
		if (rsRefs.size() > 1) {
			logWarning("doImportService",
					"getRemoteServiceReferences for interfaces=" + interfaces
							+ " returned multiple rsRefs=" + rsRefs);
		}
		// Now get first/only one
		IRemoteServiceReference rsReference = rsRefs.iterator().next();
		IRemoteService rs = rsContainer.getContainerAdapter().getRemoteService(
				rsReference);
		if (rs == null)
			throw new ECFException("getRemoteService for rsReference="
					+ rsReference + " returned null for rsContainer="
					+ rsContainer);

		Object proxy = rs.getProxy();
		if (proxy == null)
			throw new ECFException("getProxy() returned null for rsReference="
					+ rsReference + " and rsContainer=" + rsContainer);

		Dictionary proxyProperties = getProxyProperties(rsContainer,
				endpointDescription, rsReference);

		ServiceRegistration proxyRegistration = getContext().registerService(
				(String[]) interfaces.toArray(), proxy, proxyProperties);
		// Now create import registration for newly registered proxy
		return new ImportRegistration(rsContainer, rsReference,
				endpointDescription, proxyRegistration);
	}

	private Dictionary getProxyProperties(IRemoteServiceContainer rsContainer,
			EndpointDescription endpointDescription,
			IRemoteServiceReference rsReference) {
		// TODO Auto-generated method stub
		return null;
	}

	public Collection<org.eclipse.ecf.osgi.services.remoteserviceadmin.ExportRegistration> getExportedRegistrations() {
		Collection<org.eclipse.ecf.osgi.services.remoteserviceadmin.ExportRegistration> results = new ArrayList<org.eclipse.ecf.osgi.services.remoteserviceadmin.ExportRegistration>();
		synchronized (exportedRegistrations) {
			results.addAll(exportedRegistrations);
		}
		return results;
	}

	public Collection<org.osgi.service.remoteserviceadmin.ExportReference> getExportedServices() {
		Collection<org.osgi.service.remoteserviceadmin.ExportReference> results = new ArrayList<org.osgi.service.remoteserviceadmin.ExportReference>();
		synchronized (exportedRegistrations) {
			for (ExportRegistration reg : exportedRegistrations) {
				results.add(reg.getExportReference());
			}
		}
		return results;
	}

	public Collection<org.eclipse.ecf.osgi.services.remoteserviceadmin.ImportRegistration> getImportedRegistrations() {
		Collection<org.eclipse.ecf.osgi.services.remoteserviceadmin.ImportRegistration> results = new ArrayList<org.eclipse.ecf.osgi.services.remoteserviceadmin.ImportRegistration>();
		synchronized (importedRegistrations) {
			results.addAll(importedRegistrations);
		}
		return results;
	}

	public Collection<org.osgi.service.remoteserviceadmin.ImportReference> getImportedEndpoints() {
		Collection<org.osgi.service.remoteserviceadmin.ImportReference> results = new ArrayList<org.osgi.service.remoteserviceadmin.ImportReference>();
		synchronized (importedRegistrations) {
			for (ImportRegistration reg : importedRegistrations) {
				results.add(reg.getImportReference());
			}
		}
		return results;
	}

	public void close() {
		synchronized (exportedRegistrations) {
			exportedRegistrations.clear();
		}
		synchronized (importedRegistrations) {
			importedRegistrations.clear();
		}
		super.close();
	}

	private ExportRegistration[] findExportRegistrations(
			ServiceReference serviceReference) {
		List<ExportRegistration> results = new ArrayList<ExportRegistration>();
		for (ExportRegistration exportReg : exportedRegistrations)
			if (exportReg.matchesServiceReference(serviceReference))
				results.add(exportReg);
		return results.toArray(new ExportRegistration[results.size()]);
	}

	public EndpointDescription[] unexportService(ServiceReference serviceReference) {
		List<EndpointDescription> endpointDescriptions = new ArrayList<EndpointDescription>();
		synchronized (exportedRegistrations) {
			ExportRegistration[] exportRegs = findExportRegistrations(serviceReference);
			if (exportRegs != null) {
				for (int i = 0; i < exportRegs.length; i++) {
					org.osgi.service.remoteserviceadmin.ExportReference exportRef = exportRegs[i]
							.getExportReference();
					if (exportRef != null) {
						org.osgi.service.remoteserviceadmin.EndpointDescription endpointDescription = exportRef
								.getExportedEndpoint();
						if (endpointDescription != null
								&& endpointDescription instanceof EndpointDescription) {
							endpointDescriptions
									.add((EndpointDescription) endpointDescription);
						}
					}
					exportRegs[i].close();
					exportedRegistrations.remove(exportRegs[i]);
				}
			}
		}
		return endpointDescriptions.toArray(new EndpointDescription[endpointDescriptions.size()]);
	}
}