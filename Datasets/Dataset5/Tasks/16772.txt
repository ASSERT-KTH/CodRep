String remoteServiceFilter = ecfSED.getRemoteServicesFilter();

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.distribution;

import java.util.*;
import org.eclipse.core.runtime.*;
import org.eclipse.ecf.core.*;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.osgi.services.discovery.*;
import org.eclipse.ecf.osgi.services.distribution.IProxyContainerFinder;
import org.eclipse.ecf.osgi.services.distribution.IServiceConstants;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceUnregisteredEvent;
import org.eclipse.equinox.concurrent.future.IExecutor;
import org.eclipse.equinox.concurrent.future.IProgressRunnable;
import org.osgi.framework.InvalidSyntaxException;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.discovery.*;

public class DiscoveredServiceTrackerImpl implements DiscoveredServiceTracker,
		IProxyContainerFinder {

	DistributionProviderImpl distributionProvider;
	IExecutor executor;
	IProgressMonitor executorProgressMonitor;

	List serviceLocations = new ArrayList();

	private boolean addDiscoveredServiceID(ECFServiceEndpointDescription desc) {
		if (desc == null)
			return false;
		synchronized (serviceLocations) {
			return serviceLocations.add(new DiscoveredServiceID(desc
					.getServiceID().getLocation(), desc.getRemoteServiceId()));
		}
	}

	private boolean removeDiscoveredServiceID(ECFServiceEndpointDescription desc) {
		if (desc == null)
			return false;
		synchronized (serviceLocations) {
			return serviceLocations.remove(new DiscoveredServiceID(desc
					.getServiceID().getLocation(), desc.getRemoteServiceId()));
		}
	}

	private boolean containsDiscoveredServiceID(
			ECFServiceEndpointDescription desc) {
		if (desc == null)
			return false;
		synchronized (serviceLocations) {
			return serviceLocations.contains(new DiscoveredServiceID(desc
					.getServiceID().getLocation(), desc.getRemoteServiceId()));
		}
	}

	public DiscoveredServiceTrackerImpl(DistributionProviderImpl dp,
			IExecutor executor) {
		this.distributionProvider = dp;
		this.executor = executor;
	}

	// <Map<containerID><RemoteServiceRegistration>

	Map discoveredRemoteServiceRegistrations = Collections
			.synchronizedMap(new HashMap());

	List ecfRemoteServiceProperties = Arrays.asList(new String[] {
			Constants.SERVICE_ID, Constants.OBJECTCLASS,
			IServicePublication.PROP_KEY_ENDPOINT_ID,
			IServicePublication.PROP_KEY_ENDPOINT_INTERFACE_NAME,
			IServicePublication.PROP_KEY_ENDPOINT_LOCATION,
			IServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME,
			IServicePublication.PROP_KEY_SERVICE_INTERFACE_VERSION,
			IServicePublication.PROP_KEY_SERVICE_PROPERTIES });

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.service.discovery.DiscoveredServiceTracker#serviceChanged(org
	 * .osgi.service.discovery.DiscoveredServiceNotification)
	 */
	public void serviceChanged(final DiscoveredServiceNotification notification) {
		if (notification == null) {
			logWarning("serviceChanged",
					"DiscoveredServiceNotification is null.  Ignoring");
			return;
		}
		int notificationType = notification.getType();
		ServiceEndpointDescription notificationDescription = notification
				.getServiceEndpointDescription();

		trace("serviceChanged", "type=" + notificationType
				+ ",notificationDescription=" + notificationDescription);

		switch (notificationType) {
		case DiscoveredServiceNotification.AVAILABLE:
			ECFServiceEndpointDescription adesc = null;
			try {
				// If the service endpoint description is not ECF's then we
				// don't process it
				adesc = getECFserviceEndpointDescription(notificationDescription);
			} catch (Exception e) {
				logError("serviceChanged.AVAILABLE",
						"Error creating ECF endpoint description", e);
				return;
			}
			// If it's not for us then return
			if (adesc == null)
				return;

			if (!isValidService(adesc)) {
				logWarning("serviceChanged.AVAILABLE",
						"Duplicate or invalid description=" + adesc);
				return;
			}
			final ECFServiceEndpointDescription ecfASED = adesc;
			// Otherwise execute with executor
			this.executor.execute(new IProgressRunnable() {
				public Object run(IProgressMonitor monitor) throws Exception {
					try {
						handleDiscoveredServiceAvailable(ecfASED, monitor);
					} catch (Exception e) {
						logError("handleDiscoveredServiceAvailble",
								"Unexpected exception with ecfSED=" + ecfASED,
								e);
						throw e;
					}
					return null;
				}
			}, new NullProgressMonitor());
			break;
		case DiscoveredServiceNotification.UNAVAILABLE:
			try {
				ECFServiceEndpointDescription udesc = getECFserviceEndpointDescription(notificationDescription);
				// If it's not for us then return
				if (udesc == null)
					return;

				// Remove existing proxy service registrations that correspond
				// to the
				// given serviceID
				synchronized (serviceLocations) {
					ServiceRegistration[] proxyServiceRegistrations = removeProxyServiceRegistrations(udesc);
					// Then unregister them
					if (proxyServiceRegistrations != null) {
						for (int i = 0; i < proxyServiceRegistrations.length; i++) {
							trace("handleDiscoveredServiceUnavailable",
									"proxyServiceRegistrations="
											+ proxyServiceRegistrations[i]
											+ ",serviceEndpointDesc=" + udesc);
							unregisterProxyServiceRegistration(proxyServiceRegistrations[i]);
						}
						removeDiscoveredServiceID(udesc);
					}
				}
			} catch (Exception e) {
				logError("serviceChanged", "UNAVAILABLE", e);
			}
			break;
		case DiscoveredServiceNotification.MODIFIED:
			// Do nothing for now
			break;
		case DiscoveredServiceNotification.MODIFIED_ENDMATCH:
			// Do nothing for now
			break;
		default:
			logWarning("serviceChanged", "DiscoveredServiceNotification type="
					+ notificationType + " not found.  Ignoring");
			break;
		}
	}

	private boolean isValidService(ECFServiceEndpointDescription desc) {
		if (desc == null)
			return false;
		synchronized (serviceLocations) {
			if (containsDiscoveredServiceID(desc)) {
				return false;
			} else {
				addDiscoveredServiceID(desc);
				return true;
			}
		}
	}

	private IRemoteServiceContainer[] findRemoteServiceContainersViaService(
			IServiceID serviceID, IServiceEndpointDescription description,
			IProgressMonitor monitor) {
		Activator activator = Activator.getDefault();
		if (activator == null)
			return new IRemoteServiceContainer[0];
		IProxyContainerFinder[] finders = activator
				.getProxyRemoteServiceContainerFinders();
		if (finders == null || finders.length == 0) {
			logError("findRemoteServiceContainersViaService",
					"No container finders available");
			return new IRemoteServiceContainer[0];
		}
		List result = new ArrayList();
		for (int i = 0; i < finders.length; i++) {
			IRemoteServiceContainer[] foundRSContainers = finders[i]
					.findProxyContainers(serviceID, description,
							monitor);
			if (foundRSContainers != null && foundRSContainers.length > 0) {
				trace("findRemoteServiceContainersViaService",
						"findRemoteServiceContainers finder=" + finders[i]
								+ " ecfSED=" + description
								+ " foundRSContainers="
								+ Arrays.asList(foundRSContainers));
				for (int j = 0; j < foundRSContainers.length; j++)
					result.add(foundRSContainers[j]);
			}
		}
		return (IRemoteServiceContainer[]) result
				.toArray(new IRemoteServiceContainer[] {});
	}

	private void handleDiscoveredServiceAvailable(
			ECFServiceEndpointDescription ecfSED, IProgressMonitor monitor) {
		// Find IRemoteServiceContainers for the given
		// ECFServiceEndpointDescription via registered services
		IRemoteServiceContainer[] rsContainers = findRemoteServiceContainersViaService(
				ecfSED.getServiceID(), ecfSED, monitor);
		if (rsContainers == null || rsContainers.length == 0) {
			logError("handleDiscoveredServiceAvailable",
					"No RemoteServiceContainerAdapters found for description="
							+ ecfSED, null);
			return;
		}
		// Give warning if more than one ContainerAdapterHelper found
		if (rsContainers.length > 1) {
			logWarning("handleDiscoveredServiceAvailable",
					"Multiple remote service containers="
							+ Arrays.asList(rsContainers)
							+ " found for service endpoint description="
							+ ecfSED);
		}

		// Get endpoint ID
		ID ecfEndpointID = ecfSED.getECFEndpointID();
		// Get remote service filter from the service endpoint description
		// if it exists.
		String remoteServiceFilter = ecfSED.getECFRemoteServicesFilter();
		// For all remote service container adapters
		// Get futureRemoteReferences...then create a thread
		// to process the future
		Collection providedInterfaces = ecfSED.getProvidedInterfaces();
		for (int i = 0; i < rsContainers.length; i++) {
			for (Iterator j = providedInterfaces.iterator(); j.hasNext();) {
				String providedInterface = (String) j.next();
				IRemoteServiceReference[] remoteReferences = null;
				try {
					remoteReferences = rsContainers[i].getContainerAdapter()
							.getRemoteServiceReferences(ecfEndpointID,
									providedInterface, remoteServiceFilter);
				} catch (ContainerConnectException e) {
					logError("handleDiscoveredServiceAvailable", "rsca="
							+ rsContainers[i] + ",endpointId=" + ecfEndpointID
							+ ",intf=" + providedInterface
							+ ". Connect error in getRemoteServiceReferences",
							e);
					continue;
				} catch (InvalidSyntaxException e) {
					logError(
							"handleDiscoveredServiceAvailable",
							"rsca="
									+ rsContainers[i]
									+ ",endpointId="
									+ ecfEndpointID
									+ ",intf="
									+ providedInterface
									+ " Filter syntax error in getRemoteServiceReferences",
							e);
					continue;
				}
				if (remoteReferences == null || remoteReferences.length == 0) {
					logError("handleDiscoveredServiceAvailable",
							"getRemoteServiceReferences result is empty. "
									+ "containerHelper="
									+ rsContainers[i]
									+ "remoteReferences="
									+ ((remoteReferences == null) ? "null"
											: Arrays.asList(remoteReferences)
													.toString()), null);
					continue;
				} else
					registerRemoteServiceReferences(ecfSED, rsContainers[i],
							remoteReferences);
			}
		}
	}

	private ECFServiceEndpointDescription getECFserviceEndpointDescription(
			ServiceEndpointDescription aServiceEndpointDesc) {
		ECFServiceEndpointDescription ecfSED;
		if (!(aServiceEndpointDesc instanceof ECFServiceEndpointDescription)) {
			ecfSED = (ECFServiceEndpointDescription) Activator.getDefault()
					.getAdapterManager().loadAdapter(aServiceEndpointDesc,
							ECFServiceEndpointDescription.class.getName());
		} else
			ecfSED = (ECFServiceEndpointDescription) aServiceEndpointDesc;
		return ecfSED;
	}

	private boolean findProxyServiceRegistration(ServiceEndpointDescription sed) {
		for (Iterator i = discoveredRemoteServiceRegistrations.keySet()
				.iterator(); i.hasNext();) {
			ID containerID = (ID) i.next();
			RemoteServiceRegistration reg = (RemoteServiceRegistration) discoveredRemoteServiceRegistrations
					.get(containerID);
			if (sed.equals(reg.getServiceEndpointDescription()))
				return true;
		}
		return false;
	}

	private ServiceRegistration[] removeProxyServiceRegistrations(
			ServiceEndpointDescription sed) {
		List results = new ArrayList();
		for (Iterator i = discoveredRemoteServiceRegistrations.keySet()
				.iterator(); i.hasNext();) {
			ID containerID = (ID) i.next();
			RemoteServiceRegistration reg = (RemoteServiceRegistration) discoveredRemoteServiceRegistrations
					.get(containerID);
			// If the serviceID matches, then remove the
			// RemoteServiceRegistration
			// Get the service registrations and then dispose of the
			// RemoteServiceRegistration instance
			if (sed.equals(reg.getServiceEndpointDescription())) {
				i.remove();
				results.addAll(reg.removeAllServiceRegistrations());
				reg.dispose();
			}
		}
		// Then return all the ServiceRegistrations that were found
		// corresponding to this serviceID
		return (ServiceRegistration[]) results
				.toArray(new ServiceRegistration[] {});
	}

	class RemoteServiceReferenceUnregisteredListener implements
			IRemoteServiceListener {
		public void handleServiceEvent(IRemoteServiceEvent event) {
			if (event instanceof IRemoteServiceUnregisteredEvent) {
				trace("handleRemoteServiceUnregisteredEvent",
						"localContainerID=" + event.getLocalContainerID()
								+ ",containerID=" + event.getContainerID()
								+ ",remoteReference=" + event.getReference());
				// Synchronize on the map so no other changes happen while
				// this is going on...as it can be invoked by an arbitrary
				// thread
				ServiceRegistration[] proxyServiceRegistrations = null;
				synchronized (serviceLocations) {
					RemoteServiceRegistration rsRegs = (RemoteServiceRegistration) discoveredRemoteServiceRegistrations
							.get(event.getLocalContainerID());
					if (rsRegs != null) {
						proxyServiceRegistrations = rsRegs
								.removeServiceRegistration(event.getReference());
						if (rsRegs.isEmpty()) {
							rsRegs.dispose();
							discoveredRemoteServiceRegistrations.remove(event
									.getContainerID());
						}
					}
				}
				// Call this outside of synchronized block
				if (proxyServiceRegistrations != null) {
					for (int i = 0; i < proxyServiceRegistrations.length; i++) {
						trace(
								"handleRemoteServiceUnregisteredEvent.unregister",
								"localContainerID="
										+ event.getLocalContainerID()
										+ ",containerID="
										+ event.getContainerID()
										+ ",remoteReference="
										+ event.getReference()
										+ ",proxyServiceRegistrations="
										+ proxyServiceRegistrations[i]);
						unregisterProxyServiceRegistration(proxyServiceRegistrations[i]);
					}
				}
			}
		}
	}

	private void unregisterProxyServiceRegistration(ServiceRegistration reg) {
		try {
			distributionProvider.removeRemoteService(reg.getReference());
			reg.unregister();
		} catch (IllegalStateException e) {
			// Ignore
			logWarning("unregisterProxyServiceRegistration",
					"Exception unregistering serviceRegistration=" + reg);
		} catch (Exception e) {
			logError("unregisterProxyServiceRegistration",
					"Exception unregistering serviceRegistration=" + reg, e);
		}
	}

	private void registerRemoteServiceReferences(
			ECFServiceEndpointDescription sed, IRemoteServiceContainer ch,
			IRemoteServiceReference[] remoteReferences) {

		synchronized (serviceLocations) {
			// check to make sure that this serviceLocation
			// is still present
			if (!containsDiscoveredServiceID(sed)) {
				logError("registerRemoteServiceReferences", "serviceLocation="
						+ sed + " no longer present", null);
				return;
			}
			// check to make sure that the proxy service registry is not
			// already there
			if (findProxyServiceRegistration(sed)) {
				logError("registerRemoteServiceReferences",
						"serviceEndpointDesc=" + sed
								+ " previously registered locally...ignoring",
						null);
				return;
			}
			// Then setup remote service
			for (int i = 0; i < remoteReferences.length; i++) {
				// Get IRemoteService, used to create the proxy below
				IRemoteService remoteService = ch.getContainerAdapter()
						.getRemoteService(remoteReferences[i]);
				// If no remote service then give up
				if (remoteService == null) {
					logError("registerRemoteServiceReferences",
							"Remote service is null for remote reference "
									+ remoteReferences[i], null);
					continue;
				}

				// Get classes to register for remote service
				String[] clazzes = (String[]) remoteReferences[i]
						.getProperty(Constants.OBJECTCLASS);
				if (clazzes == null || clazzes.length == 0) {
					logError("registerRemoteServiceReferences",
							"No classes specified for remote service reference "
									+ remoteReferences[i], null);
					continue;
				}

				// Get service properties for the proxy
				Dictionary properties = getPropertiesForRemoteService(sed, ch
						.getContainerAdapter(), remoteReferences[i],
						remoteService);

				// Create proxy right here
				Object proxy = null;
				try {
					proxy = remoteService.getProxy();
					if (proxy == null) {
						logError("registerRemoteServiceReferences",
								"Remote service proxy is null", null);
						continue;
					}
					// Finally register
					trace("registerRemoteServiceReferences", "rsca=" + ch
							+ ",remoteReference=" + remoteReferences[i]);
					ServiceRegistration registration = Activator.getDefault()
							.getContext().registerService(clazzes, proxy,
									properties);
					IRemoteServiceReference ref = remoteReferences[i];
					ID containerID = ch.getContainer().getID();
					RemoteServiceRegistration reg = (RemoteServiceRegistration) discoveredRemoteServiceRegistrations
							.get(containerID);
					if (reg == null) {
						reg = new RemoteServiceRegistration(
								sed,
								ch,
								new RemoteServiceReferenceUnregisteredListener());
						discoveredRemoteServiceRegistrations.put(containerID,
								reg);
					}
					reg.addServiceRegistration(ref, registration);
					// And add to distribution provider
					distributionProvider.addRemoteService(registration
							.getReference());
					trace("addLocalServiceRegistration.COMPLETE",
							"containerHelper=" + ch
									+ ",remoteServiceReference=" + ref
									+ ",localServiceRegistration="
									+ registration);
				} catch (Exception e) {
					logError("registerRemoteServiceReferences",
							"Exception creating or registering remote reference "
									+ remoteReferences[i], e);
					continue;
				}
			}
		}
	}

	private boolean isRemoteServiceProperty(String propertyKey) {
		return ecfRemoteServiceProperties.contains(propertyKey);
	}

	private Dictionary getPropertiesForRemoteService(
			ServiceEndpointDescription description,
			IRemoteServiceContainerAdapter containerAdapter,
			IRemoteServiceReference remoteReference,
			IRemoteService remoteService) {
		Properties results = new Properties();
		String[] propKeys = remoteReference.getPropertyKeys();
		for (int i = 0; i < propKeys.length; i++) {
			if (!isRemoteServiceProperty(propKeys[i])) {
				results.put(propKeys[i], remoteReference
						.getProperty(propKeys[i]));
			}
		}
		results.put(IServiceConstants.OSGI_REMOTE, remoteService);
		return results;
	}

	protected void trace(String methodName, String message) {
		Trace.trace(Activator.PLUGIN_ID, DebugOptions.DISCOVEREDSERVICETRACKER,
				this.getClass(), methodName, message);
	}

	protected void traceException(String methodName, String message, Throwable t) {
		Trace.catching(Activator.PLUGIN_ID, DebugOptions.EXCEPTIONS_CATCHING,
				this.getClass(), ((methodName == null) ? "<unknown>"
						: methodName)
						+ ":" + ((message == null) ? "<empty>" : message), t);
	}

	protected void logError(String methodName, String message, Throwable t) {
		if (t != null)
			traceException(methodName, message, t);
		else
			trace(methodName, message);
		Activator.getDefault()
				.log(
						new Status(IStatus.ERROR, Activator.PLUGIN_ID,
								IStatus.ERROR, this.getClass().getName()
										+ ":"
										+ ((methodName == null) ? "<unknown>"
												: methodName)
										+ ":"
										+ ((message == null) ? "<empty>"
												: message), t));
	}

	protected void logError(String methodName, String message) {
		logError(methodName, message, null);
		traceException(methodName, message, null);
	}

	private void logWarning(String methodName, String message) {
		trace(methodName, "WARNING:" + message);
		Activator.getDefault().log(
				new Status(IStatus.WARNING, Activator.PLUGIN_ID,
						IStatus.WARNING, DiscoveredServiceTrackerImpl.class
								.getName()
								+ ":"
								+ ((methodName == null) ? "<unknown>"
										: methodName)
								+ ":"
								+ ((message == null) ? "<empty>" : message),
						null));
	}

	// Impl of IProxyContainerFinder
	public IRemoteServiceContainer[] findProxyContainers(
			IServiceID serviceID,
			IServiceEndpointDescription endpointDescription,
			IProgressMonitor monitor) {
		IContainerManager containerManager = Activator.getDefault()
				.getContainerManager();
		if (containerManager == null)
			return null;
		IContainer[] containers = containerManager.getAllContainers();
		if (containers == null) {
			// log this?
			logWarning("findRSCAs", "No containers found for container manager");
			return new IRemoteServiceContainer[0];
		}
		// If the container id is equal to the endpointID, then we don't want to
		// include it
		List results = new ArrayList();
		for (int i = 0; i < containers.length; i++) {
			// If the container under consideration has the same id
			// as the endpoint id, then we don't want to consider it
			ID containerID = containers[i].getID();
			if (containerID != null
					&& containerID.equals(endpointDescription
							.getECFEndpointID())) {
				continue;
			}
			IRemoteServiceContainerAdapter adapter = (IRemoteServiceContainerAdapter) containers[i]
					.getAdapter(IRemoteServiceContainerAdapter.class);
			if (adapter != null
					&& includeRCSAForDescription(containers[i],
							endpointDescription)) {
				results.add(new RemoteServiceContainer(containers[i], adapter));
			}
		}
		return (IRemoteServiceContainer[]) results
				.toArray(new IRemoteServiceContainer[] {});
	}

	private boolean includeRCSAForDescription(IContainer container,
			ServiceEndpointDescription description) {
		// Then we check the namespace of the endpoint container ID. If it's the
		// same as the
		// container/adapter under test then we've found a compatible one
		String connectNamespaceName = (String) description
				.getProperty(IServicePublication.PROP_KEY_ENDPOINT_CONTAINERID_NAMESPACE);
		if (connectNamespaceName != null) {
			Namespace namespace = container.getConnectNamespace();
			if (namespace != null
					&& namespace.getName().equals(connectNamespaceName))
				return true;
		}
		return false;
	}

}