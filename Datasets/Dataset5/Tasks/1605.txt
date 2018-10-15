.get(sed.getLookupTimeout());

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
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.osgi.services.discovery.ECFServiceEndpointDescription;
import org.eclipse.ecf.osgi.services.discovery.ECFServicePublication;
import org.eclipse.ecf.osgi.services.distribution.ECFServiceConstants;
import org.eclipse.ecf.remoteservice.*;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceEvent;
import org.eclipse.ecf.remoteservice.events.IRemoteServiceUnregisteredEvent;
import org.eclipse.equinox.concurrent.future.IFuture;
import org.eclipse.equinox.concurrent.future.TimeoutException;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.discovery.*;

public class DiscoveredServiceTrackerImpl implements DiscoveredServiceTracker {

	DistributionProviderImpl distributionProvider;

	public DiscoveredServiceTrackerImpl(DistributionProviderImpl dp) {
		this.distributionProvider = dp;
	}

	// <Map<containerID><RemoteServiceRegistration>

	Map discoveredRemoteServiceRegistrations = Collections
			.synchronizedMap(new HashMap());

	List ecfRemoteServiceProperties = Arrays.asList(new String[] {
			Constants.SERVICE_ID, Constants.OBJECTCLASS,
			ECFServicePublication.PROP_KEY_ENDPOINT_ID,
			ECFServicePublication.PROP_KEY_ENDPOINT_INTERFACE_NAME,
			ECFServicePublication.PROP_KEY_ENDPOINT_LOCATION,
			ECFServicePublication.PROP_KEY_SERVICE_INTERFACE_NAME,
			ECFServicePublication.PROP_KEY_SERVICE_INTERFACE_VERSION,
			ECFServicePublication.PROP_KEY_SERVICE_PROPERTIES });

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.osgi.service.discovery.DiscoveredServiceTracker#serviceChanged(org
	 * .osgi.service.discovery.DiscoveredServiceNotification)
	 */
	public void serviceChanged(DiscoveredServiceNotification notification) {
		if (notification == null) {
			logWarning("serviceChanged",
					"DiscoveredServiceNotification is null.  Ignoring");
			return;
		}
		int notificationType = notification.getType();
		switch (notificationType) {
		case DiscoveredServiceNotification.AVAILABLE:
			handleDiscoveredServiceAvailable(notification
					.getServiceEndpointDescription());
			break;
		case DiscoveredServiceNotification.UNAVAILABLE:
			handleDiscoveredServiceUnavailable(notification
					.getServiceEndpointDescription());
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

	private void handleDiscoveredServiceUnavailable(
			ServiceEndpointDescription sed) {
		// If the service endpoint description is not ECF's then we
		// don't process it
		ECFServiceEndpointDescription ecfSED = getECFserviceEndpointDescription(sed);
		if (ecfSED == null) {
			return;
		}
		// Remove existing proxy service registrations that correspond to the
		// given serviceID
		ServiceRegistration[] proxyServiceRegistrations = removeProxyServiceRegistrations(ecfSED);
		// Then unregister them
		if (proxyServiceRegistrations != null) {
			for (int i = 0; i < proxyServiceRegistrations.length; i++) {
				trace("handleDiscoveredServiceUnavailable",
						"proxyServiceRegistrations="
								+ proxyServiceRegistrations[i]
								+ ",serviceEndpointDesc=" + ecfSED);
				unregisterProxyServiceRegistration(proxyServiceRegistrations[i]);
			}
		}
	}

	private void handleDiscoveredServiceAvailable(ServiceEndpointDescription sed) {
		// If the service endpoint description is not ECF's then we
		// don't process it
		ECFServiceEndpointDescription ecfSED = getECFserviceEndpointDescription(sed);
		if (ecfSED == null) {
			return;
		}

		ID endpointID = ecfSED.getECFEndpointID();
		// Find RSCAs for the given description
		ContainerAdapterHelper[] cahs = findRSCAs(endpointID, ecfSED);
		if (cahs == null || cahs.length == 0) {
			logError("handleDiscoveredServiceAvailable",
					"No RemoteServiceContainerAdapters found for description="
							+ ecfSED, null);
			return;
		}
		// Give warning if more than one ContainerAdapterHelper found
		if (cahs.length > 1) {
			logWarning("handleDiscoveredServiceAvailable",
					"Multiple remote service containers=" + Arrays.asList(cahs)
							+ " found for service endpoint description="
							+ ecfSED);
		}
		// For all remote service container adapters
		// Get futureRemoteReferences...then create a thread
		// to process the future
		Collection providedInterfaces = ecfSED.getProvidedInterfaces();
		for (int i = 0; i < cahs.length; i++) {
			for (Iterator j = providedInterfaces.iterator(); j.hasNext();) {
				String providedInterface = (String) j.next();
				// Use async call to prevent blocking here
				trace("handleDiscoveredServiceAvailable", "rsca=" + cahs[i]
						+ ",intf=" + providedInterface);
				IFuture futureRemoteReferences = cahs[i].getRSCA()
						.asyncGetRemoteServiceReferences(
								new ID[] { endpointID }, providedInterface,
								null);
				// And process the future returned in separate thread
				processFutureForRemoteServiceReferences(ecfSED,
						futureRemoteReferences, cahs[i]);
			}
		}
	}

	private ECFServiceEndpointDescription getECFserviceEndpointDescription(
			ServiceEndpointDescription aServiceEndpointDesc) {
		ECFServiceEndpointDescription ecfSED;
		if (!(aServiceEndpointDesc instanceof ECFServiceEndpointDescription)) {
			IAdapterManager adapterManager = Activator.getDefault()
					.getAdapterManager();
			ecfSED = (ECFServiceEndpointDescription) adapterManager
					.loadAdapter(aServiceEndpointDesc,
							ECFServiceEndpointDescription.class.getName());
		} else {
			ecfSED = (ECFServiceEndpointDescription) aServiceEndpointDesc;
		}
		return ecfSED;
	}

	private void processFutureForRemoteServiceReferences(
			final ECFServiceEndpointDescription sed,
			final IFuture futureRemoteReferences,
			final ContainerAdapterHelper ch) {
		Thread t = new Thread(new Runnable() {
			public void run() {
				try {
					// Call get to get the remoteReferences from the IFuture
					// instance
					// This will block, but since we're in our own thread we're
					// OK
					IRemoteServiceReference[] remoteReferences = (IRemoteServiceReference[]) futureRemoteReferences
							.get(sed.getFutureTimeout());
					// Get the status
					IStatus futureStatus = futureRemoteReferences.getStatus();
					if (futureStatus.isOK()) {
						trace("processFutureForRemoteServiceReferences.run",
								"containerHelper="
										+ ch
										+ "remoteReferences="
										+ ((remoteReferences == null) ? "null"
												: Arrays.asList(
														remoteReferences)
														.toString()));
						if (remoteReferences != null
								&& remoteReferences.length > 0) {
							registerRemoteServiceReferences(sed, ch,
									remoteReferences);
						} else {
							logError(
									"processFutureForRemoteServiceReferences",
									"getRemoteServiceReferences result is empty. "
											+ "containerHelper="
											+ ch
											+ "remoteReferences="
											+ ((remoteReferences == null) ? "null"
													: Arrays.asList(
															remoteReferences)
															.toString()), null);
						}
					} else {
						logError("processFutureForRemoteServiceReferences",
								"Future status NOT ok message="
										+ futureStatus.getMessage(),
								futureStatus.getException());
					}
				} catch (InterruptedException e) {
					logError("processFutureForRemoteServiceReferences",
							"Retrieval interrupted", e);
				} catch (OperationCanceledException e) {
					logError("processFutureForRemoteServiceReferences",
							"Retrieval cancelled", e);
				} catch (TimeoutException e) {
					logError("processFutureForRemoteServiceReferences",
							"Retrieval timedout after " + e.getDuration(), e);
				}
			}
		});
		t.start();
	}

	private void addProxyServiceRegistration(ServiceEndpointDescription sed,
			ContainerAdapterHelper ch, IRemoteServiceReference ref,
			ServiceRegistration registration) {
		ID containerID = ch.getContainer().getID();
		RemoteServiceRegistrations reg = (RemoteServiceRegistrations) discoveredRemoteServiceRegistrations
				.get(containerID);
		if (reg == null) {
			reg = new RemoteServiceRegistrations(sed, ch.getContainer(), ch
					.getRSCA(),
					new RemoteServiceReferenceUnregisteredListener());
			discoveredRemoteServiceRegistrations.put(containerID, reg);
		}
		reg.addServiceRegistration(ref, registration);
		trace("addLocalServiceRegistration", "containerHelper=" + ch
				+ ",remoteServiceReference=" + ref
				+ ",localServiceRegistration=" + registration);
		// And add to distribution provider
		distributionProvider.addRemoteService(registration.getReference());
	}

	private boolean findProxyServiceRegistration(ServiceEndpointDescription sed) {
		for (Iterator i = discoveredRemoteServiceRegistrations.keySet()
				.iterator(); i.hasNext();) {
			ID containerID = (ID) i.next();
			RemoteServiceRegistrations reg = (RemoteServiceRegistrations) discoveredRemoteServiceRegistrations
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
			RemoteServiceRegistrations reg = (RemoteServiceRegistrations) discoveredRemoteServiceRegistrations
					.get(containerID);
			// If the serviceID matches, then remove the
			// RemoteServiceRegistration
			// Get the service registrations and then dispose of the
			// RemoteServiceRegistrations instance
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
				synchronized (discoveredRemoteServiceRegistrations) {
					RemoteServiceRegistrations rsRegs = (RemoteServiceRegistrations) discoveredRemoteServiceRegistrations
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
			ECFServiceEndpointDescription sed, ContainerAdapterHelper ch,
			IRemoteServiceReference[] remoteReferences) {

		synchronized (discoveredRemoteServiceRegistrations) {
			if (findProxyServiceRegistration(sed)) {
				logError("registerRemoteServiceReferences",
						"serviceEndpointDesc=" + sed
								+ " previously registered locally...ignoring",
						null);
				return;
			}

			for (int i = 0; i < remoteReferences.length; i++) {
				// Get IRemoteService, used to create the proxy below
				IRemoteService remoteService = ch.getRSCA().getRemoteService(
						remoteReferences[i]);
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
						.getRSCA(), remoteReferences[i], remoteService);

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
					addProxyServiceRegistration(sed, ch, remoteReferences[i],
							registration);
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
		results.put(ECFServiceConstants.OSGI_REMOTE, remoteService);
		return results;
	}

	private ContainerAdapterHelper[] findRSCAs(ID endpointID,
			ServiceEndpointDescription sedh) {
		IContainerManager containerManager = Activator.getDefault()
				.getContainerManager();
		if (containerManager == null)
			return null;
		IContainer[] containers = containerManager.getAllContainers();
		if (containers == null) {
			// log this?
			logWarning("findRSCAs", "No containers found for container manager");
			return new ContainerAdapterHelper[0];
		}
		List results = new ArrayList();
		for (int i = 0; i < containers.length; i++) {
			IRemoteServiceContainerAdapter adapter = (IRemoteServiceContainerAdapter) containers[i]
					.getAdapter(IRemoteServiceContainerAdapter.class);
			if (adapter != null
					&& includeRCSAForDescription(containers[i], adapter,
							endpointID, sedh)) {
				results.add(new ContainerAdapterHelper(containers[i], adapter));
			}
		}
		return (ContainerAdapterHelper[]) results
				.toArray(new ContainerAdapterHelper[] {});
	}

	private boolean includeRCSAForDescription(IContainer container,
			IRemoteServiceContainerAdapter adapter, ID endpointID,
			ServiceEndpointDescription description) {
		// Then we check the namespace of the endpoint container ID. If it's the
		// same as the
		// container/adapter under test then we've found a compatible one
		String connectNamespaceName = (String) description
				.getProperty(ECFServicePublication.PROP_KEY_ENDPOINT_CONTAINERID_NAMESPACE);
		if (connectNamespaceName != null) {
			Namespace namespace = container.getConnectNamespace();
			if (namespace != null
					&& namespace.getName().equals(connectNamespaceName))
				return true;
		}
		return false;
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
		traceException(methodName, message, t);
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

}