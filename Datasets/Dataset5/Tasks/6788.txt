serviceInfo) : factory

/*******************************************************************************
 * Copyright (c) 2010 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.osgi.services.remoteserviceadmin;

import java.util.Arrays;

import org.eclipse.core.runtime.ISafeRunnable;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.SafeRunner;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceListener;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.Activator.EndpointListenerHolder;
import org.eclipse.ecf.osgi.services.remoteserviceadmin.IEndpointDescriptionFactory;
import org.eclipse.osgi.framework.eventmgr.CopyOnWriteIdentityMap;
import org.eclipse.osgi.framework.eventmgr.EventDispatcher;
import org.eclipse.osgi.framework.eventmgr.EventManager;
import org.eclipse.osgi.framework.eventmgr.ListenerQueue;
import org.osgi.service.remoteserviceadmin.EndpointDescription;
import org.osgi.service.remoteserviceadmin.EndpointListener;

class LocatorServiceListener implements IServiceListener {

	private Object listenerLock = new Object();

	private ListenerQueue queue;
	private EventManager eventManager;

	class EndpointListenerEvent {
		
		private EndpointListenerHolder holder;
		private boolean discovered;

		public EndpointListenerEvent(EndpointListenerHolder holder,
				boolean discovered) {
			this.holder = holder;
			this.discovered = discovered;
		}

		public EndpointListenerHolder getEndpointListenerHolder() {
			return holder;
		}

		public boolean isDiscovered() {
			return discovered;
		}
	}

	public LocatorServiceListener() {
		ThreadGroup eventGroup = new ThreadGroup(
				"EventAdmin EndpointListener Dispatcher"); //$NON-NLS-1$
		eventGroup.setDaemon(true);
		eventManager = new EventManager(
				"EventAdmin EndpointListener Dispatcher", eventGroup); //$NON-NLS-1$
		queue = new ListenerQueue(eventManager);
		CopyOnWriteIdentityMap listeners = new CopyOnWriteIdentityMap();
		listeners.put(this, this);
		queue.queueListeners(listeners.entrySet(), new EventDispatcher() {
			public void dispatchEvent(Object eventListener,
					Object listenerObject, int eventAction, Object eventObject) {
				EndpointListenerHolder endpointListenerHolder = ((EndpointListenerEvent) eventObject).getEndpointListenerHolder();
				final boolean discovered = ((EndpointListenerEvent) eventObject).isDiscovered();
				
				final EndpointListener endpointListener = endpointListenerHolder.getListener();
				final EndpointDescription endpointDescription = endpointListenerHolder
						.getDescription();
				final String matchingFilter = endpointListenerHolder
						.getMatchingFilter();
				
				// run with SafeRunner, so that any exceptions are logged by
				// our logger
				SafeRunner.run(new ISafeRunnable() {
					public void handleException(Throwable exception) {
						logError("Exception notifying EndpointListener ",
								exception);
						Activator a = Activator.getDefault();
						if (a != null)
							a.log(new Status(
									IStatus.ERROR,
									Activator.PLUGIN_ID,
									IStatus.ERROR,
									"Exception in EndpointListener listener="+endpointListener+" description="+endpointDescription+" matchingFilter="+matchingFilter, exception)); //$NON-NLS-1$
					}

					public void run() throws Exception {
						// Call endpointAdded or endpointRemoved
						if (discovered)
							endpointListener.endpointAdded(endpointDescription, matchingFilter);
						else
							endpointListener.endpointRemoved(endpointDescription,
									matchingFilter);
					}
				});
			}
		});
	}

	public void serviceDiscovered(IServiceEvent anEvent) {
		handleService(anEvent.getServiceInfo(), true);
	}

	public void serviceUndiscovered(IServiceEvent anEvent) {
		handleService(anEvent.getServiceInfo(), false);
	}

	private boolean matchServiceID(IServiceID serviceId) {
		if (Arrays.asList(serviceId.getServiceTypeID().getServices()).contains(
				"osgiservices"))
			return true;
		return false;
	}

	void handleService(IServiceInfo serviceInfo, boolean discovered) {
		IServiceID serviceID = serviceInfo.getServiceID();
		if (matchServiceID(serviceID))
			handleOSGiServiceEndpoint(serviceID, serviceInfo, true);
	}

	private void handleOSGiServiceEndpoint(IServiceID serviceId,
			IServiceInfo serviceInfo, boolean discovered) {
		synchronized (listenerLock) {
			EndpointDescription description = createEndpointDescription(
					serviceId, serviceInfo, discovered);
			if (description != null) {
				Activator.EndpointListenerHolder[] endpointListenerHolders = Activator
						.getDefault().getMatchingEndpointListenerHolders(
								description);
				if (endpointListenerHolders != null) {
					for (int i = 0; i < endpointListenerHolders.length; i++) {
						queue.dispatchEventAsynchronous(0,
								new EndpointListenerEvent(
										endpointListenerHolders[i], discovered));
					}
				} else {
					logError("No matching EndpointListeners found for"
							+ (discovered ? "discovered" : "undiscovered")
							+ " serviceInfo=" + serviceInfo);
				}
			}
		}
	}

	private void logError(String message) {
		logError(message, null);
	}

	private void logError(String message, Throwable t) {
		Activator a = Activator.getDefault();
		if (a != null) {
			a.log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, message, t));
		}
	}

	private EndpointDescription createEndpointDescription(IServiceID serviceId,
			IServiceInfo serviceInfo, boolean discovered) {
		// Get activator
		Activator activator = Activator.getDefault();
		if (activator == null)
			return null;
		// Get IEndpointDescriptionFactory
		IEndpointDescriptionFactory factory = activator
				.getEndpointDescriptionFactory();
		if (factory == null) {
			logError("No IEndpointDescriptionFactory found, could not create EndpointDescription for "
					+ (discovered ? "discovered" : "undiscovered")
					+ " serviceInfo=" + serviceInfo);
			return null;
		}
		try {
		// Else get endpoint description factory to create EndpointDescription
		// for given serviceID and serviceInfo
		return (discovered) ? factory.createDiscoveredEndpointDescription(
				serviceId, serviceInfo) : factory
				.getUndiscoveredEndpointDescription(serviceId, serviceInfo);
		} catch (Exception e) {
			logError("Exception calling IEndpointDescriptionFactory."+((discovered)?"createDiscoveredEndpointDescription":"getUndiscoveredEndpointDescription"), e);
			return null;
		} catch (NoClassDefFoundError e) {
			logError("NoClassDefFoundError calling IEndpointDescriptionFactory."+((discovered)?"createDiscoveredEndpointDescription":"getUndiscoveredEndpointDescription"), e);
			return null;
		}
	}

	public void close() {
		if (eventManager != null) {
			eventManager.close();
			eventManager = null;
			queue = null;
		}
	}
}
 No newline at end of file