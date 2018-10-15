new EndpointDescriptionReader(), (Dictionary) properties);

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

import java.util.ArrayList;
import java.util.Collection;
import java.util.Dictionary;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.TreeMap;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.ecf.discovery.IDiscoveryAdvertiser;
import org.eclipse.ecf.discovery.IDiscoveryLocator;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.DebugOptions;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.LogUtility;
import org.eclipse.ecf.internal.osgi.services.remoteserviceadmin.PropertiesUtil;
import org.eclipse.equinox.concurrent.future.IExecutor;
import org.eclipse.equinox.concurrent.future.IProgressRunnable;
import org.eclipse.equinox.concurrent.future.ThreadsExecutor;
import org.eclipse.osgi.framework.eventmgr.CopyOnWriteIdentityMap;
import org.eclipse.osgi.framework.eventmgr.EventDispatcher;
import org.eclipse.osgi.framework.eventmgr.EventManager;
import org.eclipse.osgi.framework.eventmgr.ListenerQueue;
import org.osgi.framework.Bundle;
import org.osgi.framework.BundleContext;
import org.osgi.framework.Constants;
import org.osgi.framework.ServiceReference;
import org.osgi.framework.ServiceRegistration;
import org.osgi.service.remoteserviceadmin.EndpointDescription;
import org.osgi.service.remoteserviceadmin.EndpointListener;
import org.osgi.util.tracker.BundleTracker;
import org.osgi.util.tracker.ServiceTracker;
import org.osgi.util.tracker.ServiceTrackerCustomizer;

public class EndpointDescriptionLocator {

	private BundleContext context;
	private IExecutor executor;

	// service info factory default
	private ServiceInfoFactory serviceInfoFactory;
	private ServiceRegistration defaultServiceInfoFactoryRegistration;
	// service info factory service tracker
	private Object serviceInfoFactoryTrackerLock = new Object();
	private ServiceTracker serviceInfoFactoryTracker;

	// endpoint description factory default
	private DiscoveredEndpointDescriptionFactory defaultEndpointDescriptionFactory;
	private ServiceRegistration defaultEndpointDescriptionFactoryRegistration;
	// endpoint description factory tracker
	private Object endpointDescriptionFactoryTrackerLock = new Object();
	private ServiceTracker endpointDescriptionFactoryTracker;
	// endpointDescriptionReader default
	private ServiceRegistration defaultEndpointDescriptionReaderRegistration;

	// For processing synchronous notifications asynchronously
	private EventManager eventManager;
	private ListenerQueue eventQueue;
	private LocatorServiceListener localLocatorServiceListener;

	// ECF IDiscoveryLocator tracker
	private ServiceTracker locatorServiceTracker;
	// Locator listeners
	private Map<IDiscoveryLocator, LocatorServiceListener> locatorListeners;

	private ServiceTracker endpointListenerTracker;

	private ServiceTracker advertiserTracker;
	private Object advertiserTrackerLock = new Object();

	private BundleTracker bundleTracker;
	private EndpointDescriptionBundleTrackerCustomizer bundleTrackerCustomizer;

	public EndpointDescriptionLocator(BundleContext context) {
		this.context = context;
		this.executor = new ThreadsExecutor();
	}

	public void start() {
		// For service info and endpoint description factories
		// set the service ranking to Integer.MIN_VALUE
		// so that any other registered factories will be preferred
		final Properties properties = new Properties();
		properties.put(Constants.SERVICE_RANKING,
				new Integer(Integer.MIN_VALUE));
		serviceInfoFactory = new ServiceInfoFactory();
		defaultServiceInfoFactoryRegistration = context.registerService(
				IServiceInfoFactory.class.getName(), serviceInfoFactory,
				(Dictionary) properties);
		defaultEndpointDescriptionFactory = new DiscoveredEndpointDescriptionFactory();
		defaultEndpointDescriptionFactoryRegistration = context
				.registerService(
						IDiscoveredEndpointDescriptionFactory.class.getName(),
						defaultEndpointDescriptionFactory,
						(Dictionary) properties);
		// setup/register default endpointDescriptionReader
		defaultEndpointDescriptionReaderRegistration = context.registerService(
				IEndpointDescriptionReader.class.getName(),
				new EndpointDescriptionReader(), properties);

		// Create thread group, event manager, and eventQueue, and setup to
		// dispatch EndpointListenerEvents
		ThreadGroup eventGroup = new ThreadGroup(
				"EventAdmin EndpointDescriptionLocator EndpointListener Dispatcher"); //$NON-NLS-1$
		eventGroup.setDaemon(true);
		eventManager = new EventManager(
				"EventAdmin EndpointListener Dispatcher", eventGroup); //$NON-NLS-1$
		eventQueue = new ListenerQueue(eventManager);
		CopyOnWriteIdentityMap listeners = new CopyOnWriteIdentityMap();
		listeners.put(this, this);
		eventQueue.queueListeners(listeners.entrySet(), new EventDispatcher() {
			public void dispatchEvent(Object eventListener,
					Object listenerObject, int eventAction, Object eventObject) {
				final String logMethodName = "dispatchEvent";
				final EndpointListenerEvent event = (EndpointListenerEvent) eventObject;
				final EndpointListener endpointListener = event
						.getEndpointListener();
				final EndpointDescription endpointDescription = event
						.getEndointDescription();
				final String matchingFilter = event.getMatchingFilter();

				try {
					if (event.isDiscovered())
						endpointListener.endpointAdded(endpointDescription,
								matchingFilter);
					else
						endpointListener.endpointRemoved(endpointDescription,
								matchingFilter);
				} catch (Exception e) {
					String message = "Exception in EndpointListener listener="
							+ endpointListener + " description="
							+ endpointDescription + " matchingFilter="
							+ matchingFilter;
					logError(logMethodName, message, e);
				} catch (LinkageError e) {
					String message = "LinkageError in EndpointListener listener="
							+ endpointListener
							+ " description="
							+ endpointDescription
							+ " matchingFilter="
							+ matchingFilter;
					logError(logMethodName, message, e);
				} catch (AssertionError e) {
					String message = "AssertionError in EndpointListener listener="
							+ endpointListener
							+ " description="
							+ endpointDescription
							+ " matchingFilter="
							+ matchingFilter;
					logError(logMethodName, message, e);
				}
			}
		});
		// Register the endpoint listener tracker, so that endpoint listeners
		// that are subsequently added
		// will then be notified of discovered endpoints
		endpointListenerTracker = new ServiceTracker(context,
				EndpointListener.class.getName(),
				new ServiceTrackerCustomizer() {
					public Object addingService(ServiceReference reference) {
						return addingEndpointListener(reference);
					}

					public void modifiedService(ServiceReference reference,
							Object service) {
					}

					public void removedService(ServiceReference reference,
							Object service) {
					}
				});

		endpointListenerTracker.open();

		locatorListeners = new HashMap();
		localLocatorServiceListener = new LocatorServiceListener(this);
		// Create locator service tracker, so new IDiscoveryLocators can
		// be used to discover endpoint descriptions
		locatorServiceTracker = new ServiceTracker(context,
				IDiscoveryLocator.class.getName(),
				new LocatorTrackerCustomizer());
		locatorServiceTracker.open();
		// Get any existing locators
		Object[] locators = locatorServiceTracker.getServices();
		if (locators != null) {
			// for all of them
			for (int i = 0; i < locators.length; i++) {
				// Add service listener to locator
				openLocator((IDiscoveryLocator) locators[i]);
			}
		}
		// Create bundle tracker for reading local/xml-file endpoint
		// descriptions
		bundleTrackerCustomizer = new EndpointDescriptionBundleTrackerCustomizer(
				context, localLocatorServiceListener);
		bundleTracker = new BundleTracker(context, Bundle.ACTIVE
				| Bundle.STARTING, bundleTrackerCustomizer);
		// This may trigger local endpoint description discovery
		bundleTracker.open();
	}

	private EndpointListener addingEndpointListener(
			ServiceReference serviceReference) {
		Collection<org.osgi.service.remoteserviceadmin.EndpointDescription> allDiscoveredEndpointDescriptions = getAllDiscoveredEndpointDescriptions();
		if (context == null)
			return null;
		EndpointListener listener = (EndpointListener) context
				.getService(serviceReference);
		if (listener == null)
			return null;
		for (org.osgi.service.remoteserviceadmin.EndpointDescription ed : allDiscoveredEndpointDescriptions) {
			EndpointDescriptionLocator.EndpointListenerHolder[] endpointListenerHolders = getMatchingEndpointListenerHolders(
					new ServiceReference[] { serviceReference }, ed);
			if (endpointListenerHolders != null) {
				for (int i = 0; i < endpointListenerHolders.length; i++) {
					queueEndpointDescription(
							endpointListenerHolders[i].getListener(),
							endpointListenerHolders[i].getDescription(),
							endpointListenerHolders[i].getMatchingFilter(),
							true);
				}
			}
		}
		return listener;
	}

	private void logError(String methodName, String message, Throwable e) {
		LogUtility.logError(methodName, DebugOptions.DISCOVERY,
				this.getClass(), message, e);
	}

	public void close() {
		if (bundleTracker != null) {
			bundleTracker.close();
			bundleTracker = null;
		}
		if (bundleTrackerCustomizer != null) {
			bundleTrackerCustomizer.close();
			bundleTrackerCustomizer = null;
		}

		// shutdown locatorListeners
		synchronized (locatorListeners) {
			for (IDiscoveryLocator l : locatorListeners.keySet()) {
				LocatorServiceListener locatorListener = locatorListeners
						.get(l);
				if (locatorListener != null) {
					l.removeServiceListener(locatorListener);
					locatorListener.close();
				}
			}
			locatorListeners.clear();
		}

		Object[] locators = locatorServiceTracker.getServices();
		if (locators != null) {
			for (int i = 0; i < locators.length; i++) {
				// Add service listener to locator
				shutdownLocator((IDiscoveryLocator) locators[i]);
			}
		}

		if (localLocatorServiceListener != null) {
			localLocatorServiceListener.close();
			localLocatorServiceListener = null;
		}

		if (endpointListenerTracker != null) {
			endpointListenerTracker.close();
			endpointListenerTracker = null;
		}
		// Shutdown asynchronous event manager
		if (eventManager != null) {
			eventManager.close();
			eventManager = null;
		}

		synchronized (endpointDescriptionFactoryTrackerLock) {
			if (endpointDescriptionFactoryTracker != null) {
				endpointDescriptionFactoryTracker.close();
				endpointDescriptionFactoryTracker = null;
			}
		}
		if (defaultEndpointDescriptionFactoryRegistration != null) {
			defaultEndpointDescriptionFactoryRegistration.unregister();
			defaultEndpointDescriptionFactoryRegistration = null;
		}
		if (defaultEndpointDescriptionFactory != null) {
			defaultEndpointDescriptionFactory.close();
			defaultEndpointDescriptionFactory = null;
		}

		synchronized (serviceInfoFactoryTrackerLock) {
			if (serviceInfoFactoryTracker != null) {
				serviceInfoFactoryTracker.close();
				serviceInfoFactoryTracker = null;
			}
		}
		if (defaultServiceInfoFactoryRegistration != null) {
			defaultServiceInfoFactoryRegistration.unregister();
			defaultServiceInfoFactoryRegistration = null;
		}
		if (serviceInfoFactory != null) {
			serviceInfoFactory.close();
			serviceInfoFactory = null;
		}
		if (defaultEndpointDescriptionReaderRegistration != null) {
			defaultEndpointDescriptionReaderRegistration.unregister();
			defaultEndpointDescriptionReaderRegistration = null;
		}
		if (locatorServiceTracker != null) {
			locatorServiceTracker.close();
			locatorServiceTracker = null;
		}
		synchronized (advertiserTrackerLock) {
			if (advertiserTracker != null) {
				advertiserTracker.close();
				advertiserTracker = null;
			}
		}
		this.executor = null;
		this.context = null;
	}

	public IDiscoveryAdvertiser[] getDiscoveryAdvertisers() {
		synchronized (advertiserTrackerLock) {
			if (advertiserTracker == null) {
				advertiserTracker = new ServiceTracker(context,
						IDiscoveryAdvertiser.class.getName(), null);
				advertiserTracker.open();
			}
		}
		ServiceReference[] advertiserRefs = advertiserTracker
				.getServiceReferences();
		if (advertiserRefs == null)
			return null;
		List<IDiscoveryAdvertiser> results = new ArrayList<IDiscoveryAdvertiser>();
		for (int i = 0; i < advertiserRefs.length; i++) {
			results.add((IDiscoveryAdvertiser) context
					.getService(advertiserRefs[i]));
		}
		return results.toArray(new IDiscoveryAdvertiser[results.size()]);
	}

	private void openLocator(IDiscoveryLocator locator) {
		if (context == null)
			return;
		synchronized (locatorListeners) {
			LocatorServiceListener locatorListener = new LocatorServiceListener(
					this, locator);
			locatorListeners.put(locator, locatorListener);
			processInitialLocatorServices(locator, locatorListener);
		}
	}

	private void shutdownLocator(IDiscoveryLocator locator) {
		if (locator == null || context == null)
			return;
		synchronized (locatorListeners) {
			LocatorServiceListener locatorListener = locatorListeners
					.remove(locator);
			if (locatorListener != null)
				locatorListener.close();
		}
	}

	void queueEndpointDescription(
			EndpointListener listener,
			org.osgi.service.remoteserviceadmin.EndpointDescription endpointDescription,
			String matchingFilters, boolean discovered) {
		if (eventQueue == null)
			return;
		synchronized (eventQueue) {
			eventQueue
					.dispatchEventAsynchronous(0, new EndpointListenerEvent(
							listener, endpointDescription, matchingFilters,
							discovered));
		}
	}

	Collection<org.osgi.service.remoteserviceadmin.EndpointDescription> getAllDiscoveredEndpointDescriptions() {
		Collection<org.osgi.service.remoteserviceadmin.EndpointDescription> result = new ArrayList();
		if (localLocatorServiceListener == null)
			return result;
		// Get local first
		result.addAll(localLocatorServiceListener.getEndpointDescriptions());
		synchronized (locatorListeners) {
			for (IDiscoveryLocator l : locatorListeners.keySet()) {
				LocatorServiceListener locatorListener = locatorListeners
						.get(l);
				result.addAll(locatorListener.getEndpointDescriptions());
			}
		}
		return result;
	}

	void queueEndpointDescription(
			org.osgi.service.remoteserviceadmin.EndpointDescription endpointDescription,
			boolean discovered) {
		EndpointListenerHolder[] endpointListenerHolders = getMatchingEndpointListenerHolders(endpointDescription);
		if (endpointListenerHolders != null) {
			for (int i = 0; i < endpointListenerHolders.length; i++) {
				queueEndpointDescription(
						endpointListenerHolders[i].getListener(),
						endpointListenerHolders[i].getDescription(),
						endpointListenerHolders[i].getMatchingFilter(),
						discovered);

			}
		} else {
			LogUtility.logWarning("queueEndpointDescription",
					DebugOptions.DISCOVERY, this.getClass(),
					"No matching EndpointListeners found for "
							+ (discovered ? "discovered" : "undiscovered")
							+ " endpointDescription=" + endpointDescription);
		}

	}

	private void processInitialLocatorServices(final IDiscoveryLocator locator,
			final LocatorServiceListener locatorListener) {
		IProgressRunnable runnable = new IProgressRunnable() {
			public Object run(IProgressMonitor arg0) throws Exception {
				IServiceInfo[] serviceInfos = locator.getServices();
				for (int i = 0; i < serviceInfos.length; i++) {
					locatorListener.handleService(serviceInfos[i], true);
				}
				return null;
			}
		};
		executor.execute(runnable, null);
	}

	void shutdownLocators() {
		Object[] locators = locatorServiceTracker.getServices();
		if (locators != null) {
			for (int i = 0; i < locators.length; i++) {
				// Add service listener to locator
				shutdownLocator((IDiscoveryLocator) locators[i]);
			}
		}
	}

	private class EndpointListenerEvent {

		private EndpointListener endpointListener;
		private org.osgi.service.remoteserviceadmin.EndpointDescription endpointDescription;
		private String matchingFilter;
		private boolean discovered;

		public EndpointListenerEvent(
				EndpointListener endpointListener,
				org.osgi.service.remoteserviceadmin.EndpointDescription endpointDescription,
				String matchingFilter, boolean discovered) {
			this.endpointListener = endpointListener;
			this.endpointDescription = endpointDescription;
			this.matchingFilter = matchingFilter;
			this.discovered = discovered;
		}

		public EndpointListener getEndpointListener() {
			return endpointListener;
		}

		public org.osgi.service.remoteserviceadmin.EndpointDescription getEndointDescription() {
			return endpointDescription;
		}

		public String getMatchingFilter() {
			return matchingFilter;
		}

		public boolean isDiscovered() {
			return discovered;
		}
	}

	private class LocatorTrackerCustomizer implements ServiceTrackerCustomizer {

		/*
		 * (non-Javadoc)
		 * 
		 * @see
		 * org.osgi.util.tracker.ServiceTrackerCustomizer#addingService(org.
		 * osgi.framework.ServiceReference)
		 */
		public Object addingService(ServiceReference reference) {
			IDiscoveryLocator locator = (IDiscoveryLocator) context
					.getService(reference);
			if (locator != null)
				openLocator(locator);
			return locator;
		}

		public void modifiedService(ServiceReference reference, Object service) {
		}

		public void removedService(ServiceReference reference, Object service) {
			shutdownLocator((IDiscoveryLocator) service);
		}
	}

	public IServiceInfoFactory getServiceInfoFactory() {
		if (context == null)
			return null;
		synchronized (serviceInfoFactoryTrackerLock) {
			if (serviceInfoFactoryTracker == null) {
				serviceInfoFactoryTracker = new ServiceTracker(context,
						IServiceInfoFactory.class.getName(), null);
				serviceInfoFactoryTracker.open();
			}
		}
		return (IServiceInfoFactory) serviceInfoFactoryTracker.getService();
	}

	public IDiscoveredEndpointDescriptionFactory getDiscoveredEndpointDescriptionFactory() {
		synchronized (endpointDescriptionFactoryTrackerLock) {
			if (context == null)
				return null;
			if (endpointDescriptionFactoryTracker == null) {
				endpointDescriptionFactoryTracker = new ServiceTracker(context,
						IDiscoveredEndpointDescriptionFactory.class.getName(),
						null);
				endpointDescriptionFactoryTracker.open();
			}
			return (IDiscoveredEndpointDescriptionFactory) endpointDescriptionFactoryTracker
					.getService();
		}
	}

	private Object endpointListenerServiceTrackerLock = new Object();

	public EndpointListenerHolder[] getMatchingEndpointListenerHolders(
			EndpointDescription description) {
		synchronized (endpointListenerServiceTrackerLock) {
			if (context == null)
				return null;
			return getMatchingEndpointListenerHolders(
					endpointListenerTracker.getServiceReferences(), description);
		}
	}

	public class EndpointListenerHolder {

		private EndpointListener listener;
		private EndpointDescription description;
		private String matchingFilter;

		public EndpointListenerHolder(EndpointListener l,
				EndpointDescription d, String f) {
			this.listener = l;
			this.description = d;
			this.matchingFilter = f;
		}

		public EndpointListener getListener() {
			return listener;
		}

		public EndpointDescription getDescription() {
			return description;
		}

		public String getMatchingFilter() {
			return matchingFilter;
		}
	}

	public EndpointListenerHolder[] getMatchingEndpointListenerHolders(
			ServiceReference[] refs, EndpointDescription description) {
		if (refs == null)
			return null;
		List results = new ArrayList();
		for (int i = 0; i < refs.length; i++) {
			EndpointListener listener = (EndpointListener) context
					.getService(refs[i]);
			if (listener == null)
				continue;
			List filters = PropertiesUtil.getStringPlusProperty(
					getMapFromProperties(refs[i]),
					EndpointListener.ENDPOINT_LISTENER_SCOPE);
			String matchingFilter = isMatch(description, filters);
			if (matchingFilter != null)
				results.add(new EndpointListenerHolder(listener, description,
						matchingFilter));
		}
		return (EndpointListenerHolder[]) results
				.toArray(new EndpointListenerHolder[results.size()]);
	}

	private String isMatch(EndpointDescription description, List filters) {
		for (Iterator j = filters.iterator(); j.hasNext();) {
			String filter = (String) j.next();
			if (description.matches(filter))
				return filter;
		}
		return null;
	}

	private Map getMapFromProperties(ServiceReference ref) {
		Map<String, Object> results = new TreeMap<String, Object>(
				String.CASE_INSENSITIVE_ORDER);
		String[] keys = ref.getPropertyKeys();
		if (keys != null) {
			for (int i = 0; i < keys.length; i++) {
				results.put(keys[i], ref.getProperty(keys[i]));
			}
		}
		return results;
	}

}